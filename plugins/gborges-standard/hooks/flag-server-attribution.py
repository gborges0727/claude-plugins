#!/usr/bin/env python3
"""Tell the agent to remove the attribution footer the server adds to new PRs.

Runs as a PostToolUse hook on mcp__github__create_pull_request. The GitHub MCP
server appends its own Claude Code attribution footer to the PR body after the
call leaves the session, so the PreToolUse hook in strip-attribution.py never
sees it: that hook edits arguments on the way in, and the server writes on the
far side.

This hook has no GitHub credentials, so it cannot rewrite the body itself. It
returns additionalContext instead, telling the agent to fetch the stored body
and post a corrected one through mcp__github__update_pull_request. That update
call passes back through strip-attribution.py, and update_pull_request does not
append a footer of its own, so the correction sticks.

Only create_pull_request is covered. The comment and review write tools have no
matching update tool in the GitHub MCP server, so there is nothing to instruct
the agent to call for them.
"""

import importlib.util
import json
import os
import re
import sys

TOOL = "mcp__github__create_pull_request"

FIX_TOOL = "mcp__github__update_pull_request"

DIRTY = (
    "The GitHub server appended an AI-attribution footer to the pull request "
    "body it just stored, and this setup carries no AI attribution on PRs."
)

UNVERIFIED = (
    "The GitHub server appends an AI-attribution footer to new pull request "
    "bodies server-side, after the submitted text leaves the session, and this "
    "setup carries no AI attribution on PRs. The tool response did not include "
    "the stored body, so the footer is likely but unconfirmed."
)

ACTION = (
    " Before doing anything else, read the pull request body back with "
    "mcp__github__pull_request_read. If it ends with an attribution block (a "
    "--- rule followed by a 'Generated with/by Claude Code' line, or the "
    "'\U0001f916 Generated with [Claude Code]' form, or a bare claude.ai/code "
    "session link), call {fix} with the body cut off at the intended last "
    "line. Then confirm the stored body ends where you meant it to."
).format(fix=FIX_TOOL)


def load_patterns():
    """Reuse the PATTERNS list from strip-attribution.py.

    The filename has a hyphen, so it is not importable by name."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strip-attribution.py")
    spec = importlib.util.spec_from_file_location("strip_attribution", path)
    if spec is None or spec.loader is None:
        return ()
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PATTERNS


def find_body(response):
    """Return the PR body the server stored, or None if it is not in the
    response. The MCP server may hand back the PR object directly, wrap it in
    a text content block, or return nothing useful at all."""
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except (json.JSONDecodeError, ValueError):
            return None

    if isinstance(response, dict):
        body = response.get("body")
        if isinstance(body, str):
            return body
        for key in ("pull_request", "pullRequest", "result", "data", "text"):
            nested = find_body(response.get(key))
            if nested is not None:
                return nested
        content = response.get("content")
        if content is not None:
            return find_body(content)
        return None

    if isinstance(response, list):
        for item in response:
            nested = find_body(item)
            if nested is not None:
                return nested
    return None


def has_footer(body, patterns):
    """Match only the patterns that name Claude. The list also carries one for
    a horizontal rule left stranded once a footer above it is deleted, and a
    body that legitimately ends in a rule is not a footer."""
    named = [p for p in patterns if "claude" in p.lower()]
    return any(re.search(pattern, body, flags=re.IGNORECASE) for pattern in named)


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    if event.get("tool_name") != TOOL:
        return

    body = find_body(event.get("tool_response"))
    if body is None:
        context = UNVERIFIED + ACTION
    elif has_footer(body, load_patterns()):
        context = DIRTY + ACTION
    else:
        # The stored body is already clean. Say nothing.
        return

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": context,
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
