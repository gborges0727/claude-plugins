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
Explore and Plan spawns are skipped: they publish nothing, and only the
styled main conversation reads their reports. A prompt that already carries
the block is left alone, and on any read failure the hook stays silent
rather than breaking the spawn.
"""

import json
import re
import sys
from pathlib import Path

STYLE = Path(__file__).resolve().parent.parent / "output-styles" / "plain-english.md"

# Sections of the style a subagent needs. Size, Plans, and Deliverables
# shape replies and plans the main conversation owns; these four shape the
# sentences and commits a subagent writes on its own.
SECTIONS = ("Sentences", "The reader is new to this", "Punctuation", "Git")

MARKER = "<writing-rules>"

SPAWN_TOOLS = ("Agent", "Task")

# Read-only searchers. Their output goes to the main agent, not a person.
SKIP_TYPES = ("Explore", "Plan")

CODA = """Before shipping any file deliverable longer than a few paragraphs (a PR
body, an audit, a spec, a plan), draft it to a file and run both passes of
the writing-voice skill on the draft. When you cannot run the skill, return
the draft in your final report instead of publishing it."""


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

    prompt = tool_input.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip() or MARKER in prompt:
        return

    block = rules_block()
    if block is None:
        return

    updated = dict(tool_input)
    updated["prompt"] = f"{prompt.rstrip()}\n\n{block}"

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": "Appended the writing rules to the subagent prompt",
                "updatedInput": updated,
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
