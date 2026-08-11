#!/usr/bin/env python3
"""Re-inject the style's Reminder paragraph on every user prompt.

Runs as a UserPromptSubmit hook. The Plain English output style sits at the
top of the system prompt, and its pull on a reply weakens as the
conversation grows over it. File deliverables get the writing-voice ritual,
and an ordinary chat reply has nothing between it and that drift. This hook
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

Fail-open contract: on any problem (the switch is off, the style file is
missing, the Reminder section is gone), the hook prints nothing and exits
0, and the turn proceeds without a reminder. Keep every exit path in this
file that way.

Config:
  WRITING_VOICE_REMIND  1|0  master switch (default 1)
"""

import json
import os
import re
import sys
from pathlib import Path

STYLE = Path(__file__).resolve().parent.parent / "output-styles" / "plain-english.md"

SECTION = re.compile(r"^## Reminder\s*\n(.*?)(?=^#|\Z)", re.MULTILINE | re.DOTALL)

PREFIX = "Plain English reminder: "


def reminder_line():
    match = SECTION.search(STYLE.read_text(encoding="utf-8"))
    if not match:
        return None
    return " ".join(match.group(1).split()) or None


def main():
    if os.environ.get("WRITING_VOICE_REMIND", "1") != "1":
        return

    # The event payload carries nothing this hook needs. It is read anyway so
    # the parent process never blocks writing to a closed pipe.
    try:
        sys.stdin.read()
    except OSError:
        pass

    try:
        line = reminder_line()
    except OSError:
        return
    if not line:
        return

    try:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": PREFIX + line,
                }
            },
            sys.stdout,
        )
    except OSError:
        pass


if __name__ == "__main__":
    main()
