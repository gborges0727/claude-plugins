#!/usr/bin/env python3
"""Append the writing rules to every subagent's prompt before it spawns.

Runs as a PreToolUse hook on the Agent tool (Task in older Claude Code).
A subagent runs its own system prompt, so the Plain English output style
never reaches it, and prose it publishes (a PR body, a commit message, a
comment) ships unstyled. The style asks the main agent to copy the rules
into spawn prompts by hand, and that instruction fails the way any
instruction fails. This hook does the same copy mechanically.

Codex spawns subagents through its own tool, which no Agent matcher
catches, and it fires a SubagentStart event instead. Passing
--subagent-start handles that event: same block, delivered as
additionalContext rather than as a rewritten prompt, since SubagentStart
cannot edit the prompt.

The injected block is read from the installed plain-english.md at run time,
so the rules keep one source and the hook needs no edit when they change.
Explore and Plan spawns are skipped. They publish nothing, and only the
styled main conversation reads their reports. A prompt that already carries
the block is left alone, and on any read failure the hook stays silent
rather than breaking the spawn.

The same hook also decides who may run the Fable agent. Fable is the
expensive model, so gborges-standard:fable-xhigh runs only when the user
asked for it by name in their latest message. remind-writing-rules.py
records that answer per session, and this hook reads the record. A Fable
spawn with no such record comes back denied, and the reason tells the main
agent to send the same brief to gborges-standard:opus-xhigh instead.

Some machines have no Fable access at all. The "fable" key in
~/.claude/gborges-standard.json says so, and plugin_config.load() reads it.
When the user named Fable but the key is false, the hook rewrites
subagent_type to gborges-standard:opus-xhigh and lets the spawn through.
The writing rules still get appended to the rewritten spawn.

A spawn that does go to Fable gets one more paragraph after the rules. At
xhigh effort Fable can draft a long deliverable in its thinking and then
write it out again as the reply, which doubles the turn's output.
Anthropic's Fable 5.1 prompting guide gives a note that stops that, and this
hook appends it to a Fable spawn's prompt only. The guide's wording names
the request's max_tokens, which a Claude Code subagent never sees, so that
sentence is left out.
"""

import json
import re
import sys
from pathlib import Path

try:
    import plugin_config
except ImportError:
    # Fail safe when the sibling module is missing. A Fable spawn reads as
    # unmentioned and is refused, and every other spawn runs as before.
    class plugin_config:  # noqa: N801
        @staticmethod
        def load():
            return {"fable": True, "codex": False}

        @staticmethod
        def read_mention(session_id):
            return False

STYLE = Path(__file__).resolve().parent.parent / "output-styles" / "plain-english.md"

# Sections of the style a subagent needs. Size, Plans, and Deliverables
# shape replies and plans the main conversation owns; these four shape the
# sentences and commits a subagent writes on its own.
SECTIONS = ("Sentences", "The reader is new to this", "Punctuation", "Git")

MARKER = "<writing-rules>"

SPAWN_TOOLS = ("Agent", "Task")

# Read-only searchers. Their output goes to the main agent, not a person.
SKIP_TYPES = ("Explore", "Plan")

# Both ways a dispatch can name the Fable agent.
FABLE_TYPES = ("gborges-standard:fable-xhigh", "fable-xhigh")

FALLBACK_TYPE = "gborges-standard:opus-xhigh"

DENY_REASON = (
    "The Fable agent runs only when the user's own message names "
    "@agent-fable-xhigh. This message did not, so send the same brief to "
    "gborges-standard:opus-xhigh instead."
)

SUBSTITUTE_REASON = (
    "Fable is turned off on this machine, so this spawn goes to "
    "gborges-standard:opus-xhigh. Appended the writing rules to the "
    "subagent prompt."
)

LONG_OUTPUT = """Everything you produce in one reply, including any reasoning or drafting
before the reply, counts toward one output limit. Composing an entire
deliverable in full as reasoning and then again as a reply would double the
length of the turn without improving the result, so don't do that. When the
brief asks for a long deliverable, such as a multi-section document, a large
table, or a complete code file, spend the reasoning on understanding the
request, checking the inputs the answer depends on, and settling the
structure, and write the deliverable once, in the output."""

CODA = """Before shipping any artifact (a PR body, a commit message, a comment, a
doc, an audit, a spec, a plan), whatever its length, draft it to a file and
run both passes of the writing-voice skill on the draft. When you cannot run
the skill, return the draft in your final report instead of publishing it."""


def rules_block():
    """Build the injected block from the installed style, or None."""
    try:
        text = STYLE.read_text(encoding="utf-8")
    except OSError:
        return None
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    parts = re.split(r"^## (.+)$", body, flags=re.M)
    sections = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}
    kept = [f"## {name}\n\n{sections[name]}" for name in SECTIONS if name in sections]
    if not kept:
        return None
    return (
        f"{MARKER}\nProse a person will read follows these rules.\n\n"
        + "\n\n".join(kept)
        + f"\n\n{CODA}\n</writing-rules>"
    )


def subagent_start(event):
    """Return the block to Codex as context on the spawned agent's first turn."""
    if event.get("agent_type") in SKIP_TYPES:
        return

    block = rules_block()
    if block is None:
        return

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SubagentStart",
                "additionalContext": block,
            }
        },
        sys.stdout,
    )


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    if "--subagent-start" in sys.argv:
        subagent_start(event)
        return

    if event.get("tool_name") not in SPAWN_TOOLS:
        return

    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return
    if tool_input.get("subagent_type") in SKIP_TYPES:
        return

    reason = "Appended the writing rules to the subagent prompt"
    substitute = False
    fable_note = False

    if tool_input.get("subagent_type") in FABLE_TYPES:
        if not plugin_config.read_mention(event.get("session_id")):
            json.dump(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": DENY_REASON,
                    }
                },
                sys.stdout,
            )
            return
        if not plugin_config.load()["fable"]:
            substitute = True
            reason = SUBSTITUTE_REASON
        else:
            fable_note = True
            reason = "Appended the writing rules and the long-output note to the subagent prompt"

    prompt = tool_input.get("prompt")
    block = rules_block()
    injectable = (
        isinstance(prompt, str)
        and prompt.strip()
        and MARKER not in prompt
        and block is not None
    )
    if not injectable and not substitute:
        return

    updated = dict(tool_input)
    if injectable:
        updated["prompt"] = f"{prompt.rstrip()}\n\n{block}"
        if fable_note:
            updated["prompt"] += f"\n\n{LONG_OUTPUT}"
    if substitute:
        updated["subagent_type"] = FALLBACK_TYPE

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": reason,
                "updatedInput": updated,
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
