#!/usr/bin/env python3
"""Decide which agent a spawn runs on, and append the writing rules to it.

Runs as a PreToolUse hook on the Agent tool (Task in older Claude Code),
so it sees every spawn in the session, including the ones a skill or a
forked agent makes. It pins each spawn to one of the plugin's routed
agents, refuses the spawns that would run on the session's own model, and
appends the writing rules to the prompt.

The writing rules come first historically. A subagent runs its own system
prompt, so the Plain English output style never reaches it, and prose it
publishes (a PR body, a commit message, a comment) ships unstyled. The
style asks the main agent to copy the rules into spawn prompts by hand,
and that instruction fails the way any instruction fails. This hook does
the same copy mechanically.

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

An unpinned spawn inherits the session's model and effort, so the same
task runs on Sonnet in one session and on Fable in another. The routed
agents in agents/ each pin a model and an effort, and the style tells the
main agent to use them, but a built-in skill's procedure names the
built-in types instead. So a spawn that names general-purpose, claude,
default-agent, or no type at all is rewritten to
gborges-standard:opus-medium, the plugin's default, and let through with
the writing rules appended. Pinned types, Explore, Plan, and any other
named type pass as they are.

A fork is refused when the session runs on Fable. A fork copies the
whole transcript into a second agent that runs on the session's model,
and no rewrite can change that model, because a fork with a different
type is no longer a fork.

On an Opus or Sonnet session the fork already runs on a model the style
would pick, so it passes untouched. It needs no writing rules because it
inherits the parent's system prompt. On a Fable session the fork's own work runs at Fable's output price, so the
refusal's reason tells the main agent to send the same task to
opus-medium with a brief that carries what the fork would have inherited.
The built-in code-review skill forks its reviewer, so this is what moves
that reviewer onto Opus while leaving the skill itself usable.

A fork still passes on Fable when the user's latest message used the word
"fork". remind-writing-rules.py records that per session, and this hook
reads the record. It also passes when the hook cannot tell what model the
session runs on.

The session's model comes from the transcript file the event names. The
last assistant entry in that file carries the model id of the reply it
holds. The hook reads the file's tail and takes the newest one. A missing
file, an unreadable file, or a file with no assistant entry yet counts as
unknown, and unknown lets the fork through, because refusing on a guess
would break forks on every host whose transcript format differs.

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

        @staticmethod
        def read_fork(session_id):
            return False

STYLE = Path(__file__).resolve().parent.parent / "output-styles" / "plain-english.md"

# Sections of the style a subagent needs. Size, Plans, and Deliverables
# shape replies and plans the main conversation owns; these five shape the
# sentences, commits, and file edits a subagent makes on its own.
SECTIONS = ("Sentences", "The reader is new to this", "Punctuation", "Git", "File edits")

MARKER = "<writing-rules>"

SPAWN_TOOLS = ("Agent", "Task")

# Read-only searchers. Their output goes to the main agent, not a person.
SKIP_TYPES = ("Explore", "Plan")

# Types that inherit the session's model. Empty covers a missing type,
# which Claude Code treats as general-purpose.
UNPINNED_TYPES = (
    "",
    "general-purpose",
    "default-agent",
    "gborges-standard:default-agent",
    "claude",
)

DEFAULT_TYPE = "gborges-standard:opus-medium"

# A copy of the running conversation on the session's own model.
FORK_TYPES = ("fork",)

# Both ways a dispatch can name the Fable agent.
FABLE_TYPES = ("gborges-standard:fable-xhigh", "fable-xhigh")

FALLBACK_TYPE = "gborges-standard:opus-xhigh"

FORK_REASON = (
    "This session runs on Fable, and a fork would run the whole transcript "
    "on Fable too, so it is refused. Send the same task to "
    "gborges-standard:opus-medium with a brief that says what the fork "
    "would have known: the goal, the files or diff target, and the "
    "procedure to follow. For a review, put the review procedure (the "
    "org's code-reviewer, or the repo's own review skill) in that brief. "
    "If the user wants a fork on this session, they say so in their "
    "message."
)

# Read the transcript's tail in chunks this size, doubling until an
# assistant entry turns up or the whole file has been read.
TAIL_CHUNK = 64 * 1024


def session_model(transcript_path):
    """Return the model id of the session's newest reply, or None."""
    if not isinstance(transcript_path, str) or not transcript_path:
        return None
    path = Path(transcript_path)
    try:
        size = path.stat().st_size
    except OSError:
        return None
    chunk = TAIL_CHUNK
    while True:
        try:
            with path.open("rb") as handle:
                handle.seek(max(size - chunk, 0))
                tail = handle.read().decode("utf-8", errors="replace")
        except OSError:
            return None
        lines = tail.splitlines()
        if chunk < size:
            lines = lines[1:]  # the first line may start mid-entry
        for line in reversed(lines):
            if '"assistant"' not in line:
                continue
            try:
                entry = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            if entry.get("type") != "assistant":
                continue
            message = entry.get("message")
            if isinstance(message, dict) and isinstance(message.get("model"), str):
                return message["model"]
        if chunk >= size:
            return None
        chunk *= 2


def on_fable(transcript_path):
    """Say whether the session's newest reply came from a Fable model."""
    model = session_model(transcript_path)
    return model is not None and "fable" in model.lower()

REPIN_REASON = (
    "Rewrote an unpinned subagent type to gborges-standard:opus-medium, "
    "the plugin's default, and appended the writing rules to the subagent "
    "prompt."
)

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
    subagent_type = tool_input.get("subagent_type") or ""
    if subagent_type in SKIP_TYPES:
        return

    if subagent_type in FORK_TYPES:
        if plugin_config.read_fork(event.get("session_id")):
            return
        if not on_fable(event.get("transcript_path")):
            return
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": FORK_REASON,
                }
            },
            sys.stdout,
        )
        return

    reason = "Appended the writing rules to the subagent prompt"
    substitute = False
    repin = False
    fable_note = False

    if subagent_type in UNPINNED_TYPES:
        repin = True
        reason = REPIN_REASON

    if subagent_type in FABLE_TYPES:
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
    if not injectable and not substitute and not repin:
        return

    updated = dict(tool_input)
    if injectable:
        updated["prompt"] = f"{prompt.rstrip()}\n\n{block}"
        if fable_note:
            updated["prompt"] += f"\n\n{LONG_OUTPUT}"
    if substitute:
        updated["subagent_type"] = FALLBACK_TYPE
    if repin:
        updated["subagent_type"] = DEFAULT_TYPE

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
