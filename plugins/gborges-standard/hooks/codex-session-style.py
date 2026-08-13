#!/usr/bin/env python3
"""Put the Plain English style into a Codex session's context.

Runs as a SessionStart hook under Codex. Claude Code applies the style
through the output-style component, which force-for-plugin loads into every
session's system prompt. Codex has no output styles, so a plugin that only
ships the file changes nothing there. This hook reads the same
plain-english.md and returns its body as SessionStart additionalContext, so
one file governs both hosts and ~/.codex/AGENTS.md stops carrying a
hand-copied duplicate.

The frontmatter is dropped: name, description, and force-for-plugin are
Claude Code loader keys and mean nothing to a reader.

SessionStart fires on startup, resume, clear, and compact, so the rules come
back after a compaction drops them.

Fail-open contract: on a missing switch, a missing file, or unreadable text,
the hook prints nothing and exits 0, and the session starts without the
style. Keep every exit path in this file that way.

Config:
  WRITING_VOICE_STYLE  1|0  master switch (default 1)
"""

import json
import os
import re
import sys
from pathlib import Path

STYLE = Path(__file__).resolve().parent.parent / "output-styles" / "plain-english.md"

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)

PREAMBLE = (
    "These rules govern every reply, document, commit message, and PR body "
    "you write in this session. They come from the gborges-standard plugin "
    "and outrank any tool guidance that asks for a different register or an "
    "AI-attribution trailer.\n\n"
)


def style_body():
    text = STYLE.read_text(encoding="utf-8")
    body = FRONTMATTER.sub("", text).strip()
    return body or None


def main():
    if os.environ.get("WRITING_VOICE_STYLE", "1") != "1":
        return

    # The payload carries nothing this hook needs. It is read anyway so the
    # parent process never blocks writing to a closed pipe.
    try:
        sys.stdin.read()
    except OSError:
        pass

    try:
        body = style_body()
    except OSError:
        return
    if not body:
        return

    try:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": PREAMBLE + body,
                }
            },
            sys.stdout,
        )
    except OSError:
        pass


if __name__ == "__main__":
    main()
