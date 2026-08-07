#!/usr/bin/env python3
"""Strip AI-attribution footers from GitHub writes before they are posted.

Runs as a PreToolUse hook on mcp__github__* calls. CONVENTIONS.md bans
attribution trailers on PR bodies and comments, but the GitHub tool guidance in
some harnesses instructs the opposite, and instructions lose to instructions.
This enforces it mechanically instead.

Only speaks up when it actually removed something. A body that is already clean
produces no output, so the normal permission flow still runs on that call. The
implicit approval that rides along with updatedInput is therefore limited to
calls this hook just corrected.
"""

import json
import re
import sys

# Tool arguments that can carry a body of prose bound for GitHub.
BODY_FIELDS = ("body", "message", "commit_message")

PATTERNS = (
    # Markdown footer, with or without the horizontal rule above it.
    r"\n*(?:---+\s*\n+)?_?\s*(?:🤖\s*)?Generated (?:by|with) \[Claude Code\]\([^)]*\)_?\s*",
    # Bare prose variants.
    r"\n*(?:🤖\s*)?Generated (?:by|with) Claude Code\s*",
    # Commit-style trailers that also show up pasted into bodies.
    r"\n*Co-Authored-By:\s*Claude[^\n]*",
    r"\n*Claude-Session:\s*https?://[^\s]+",
    # The session link the harness footer leaves on its own line.
    r"\n*https?://claude\.(?:ai|com)/code/\S*",
    # A rule left stranded at the end once the footer above it is gone.
    r"\n+---+[ \t]*$",
)


def strip(text):
    """Return (text, changed). Only normalizes whitespace if a pattern hit,
    so an already-clean body compares equal and the hook stays silent."""
    cleaned = text
    for pattern in PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    if cleaned == text:
        return text, False
    return cleaned.rstrip() + "\n", True


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    if not event.get("tool_name", "").startswith("mcp__github__"):
        return

    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return

    cleaned = dict(tool_input)
    removed = False

    for field in BODY_FIELDS:
        original = cleaned.get(field)
        if not isinstance(original, str) or not original.strip():
            continue
        stripped, changed = strip(original)
        if changed:
            cleaned[field] = stripped
            removed = True

    if not removed:
        # Say nothing. Normal permission flow applies.
        return

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": "Removed AI-attribution footer per CONVENTIONS.md",
                "updatedInput": cleaned,
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
