#!/bin/bash
# PostToolUse hook for mcp__github__create_pull_request, wired up in
# .claude/settings.json. The cloud PR-creation path appends a Claude Code
# attribution footer to the PR body server-side, after the submitted text
# leaves the session's hands. This hook fires right after the PR exists and
# tells the session to strip the footer. The update path does not re-append
# it, so the edit sticks.
cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"This repo carries no AI attribution on PRs. The platform has just appended a Claude Code attribution footer to the PR body server-side, even though it was not in the submitted text. Before doing anything else: fetch the PR body, and if it ends with an attribution block (a --- rule followed by a 'Generated with/by Claude Code' line, or the '🤖 Generated with [Claude Code]' form), edit the PR body to remove that block, then confirm the body ends at the intended last line."}}
EOF
