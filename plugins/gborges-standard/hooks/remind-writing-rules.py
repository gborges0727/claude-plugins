#!/usr/bin/env python3
"""Re-inject the style's Reminder paragraph on every user prompt.

Runs as a UserPromptSubmit hook. The Plain English output style sits at the
top of the system prompt, and its pull on a reply weakens as the
conversation grows over it. The writing-voice ritual covers artifacts only, so
a chat reply is shaped while it is being written, which is exactly where
the style's pull is weakest. This hook
fires after the user sends a message and before Claude answers it, and
returns the style's own ## Reminder section as one line of context. The
distillation of the rules then sits at the bottom of the conversation, next
to the reply being written, where recency gives it the most force.

The line is read from the installed plain-english.md at run time, so the
reminder keeps one source and this hook needs no edit when the style
changes.

The line restates the rules and nothing else. A reminder that quotes
mistakes pastes the banned phrasing back into fresh context and feeds the
habit it polices, so no scan output and no violation content belongs here.

The hook does two more jobs on the same event. It records whether this
message names the Fable agent, writing 1 or 0 to a per-session file under
~/.claude/gborges-standard/state. Every message rewrites that file, so it
always describes the latest message. inject-writing-rules.py reads the
record and denies a Fable spawn the user never asked for.

It also appends one sentence saying whether this machine may hand coding
subtasks to the Codex CLI. The "codex" key in ~/.claude/gborges-standard.json
decides the wording, and plugin_config.load() reads it. The main agent then
knows the answer with no tool call and no guess.

On any problem (the style file is missing, the Reminder section is gone,
the settings file will not read) the hook still exits 0 and the turn
proceeds. The switch below silences the reminder line only. The mention
record and the Codex line are written either way, because the two rules
they feed do not depend on the writing style.

Config:
  WRITING_VOICE_REMIND  1|0  switch for the reminder line (default 1)
"""

import json
import os
import re
import sys
from pathlib import Path

try:
    import plugin_config
except ImportError:
    # Fail open when the sibling module is missing. The reminder line still
    # goes out, and the two switches take their defaults.
    class plugin_config:  # noqa: N801
        @staticmethod
        def load():
            return {"fable": True, "codex": False}

        @staticmethod
        def mention_from_prompt(prompt):
            return False

        @staticmethod
        def write_mention(session_id, mentioned):
            return None

STYLE = Path(__file__).resolve().parent.parent / "output-styles" / "plain-english.md"

SECTION = re.compile(r"^## Reminder\s*\n(.*?)(?=^#|\Z)", re.MULTILINE | re.DOTALL)

PREFIX = "Plain English reminder: "


def reminder_line():
    match = SECTION.search(STYLE.read_text(encoding="utf-8"))
    if not match:
        return None
    return " ".join(match.group(1).split()) or None


def main():
    try:
        raw = sys.stdin.read()
    except OSError:
        raw = ""
    try:
        event = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        event = {}
    if not isinstance(event, dict):
        event = {}

    plugin_config.write_mention(
        event.get("session_id"),
        plugin_config.mention_from_prompt(event.get("prompt")),
    )

    lines = []
    if os.environ.get("WRITING_VOICE_REMIND", "1") == "1":
        try:
            line = reminder_line()
        except OSError:
            line = None
        if line:
            lines.append(PREFIX + line)

    if not lines:
        return

    try:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": "\n".join(lines),
                }
            },
            sys.stdout,
        )
    except OSError:
        pass


if __name__ == "__main__":
    main()
