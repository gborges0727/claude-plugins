#!/usr/bin/env sh
# SessionStart hook: prints the working conventions followed by the
# writing-voice ruleset, so the rules are present every session and after every
# compaction rather than waiting on a skill to trigger.
#
# The agent's harness caps hook output. Over the cap it keeps the head, saves
# the rest to a file, and says so in a system reminder that is easy to read past
# once the visible part looks like a whole document. On 2026-08-07 that dropped
# the two passes while keeping the sentence instructing the agent to run them.
# So the output is kept small by design (the eleven rules live in RULES.md,
# reached by a pointer), and BUDGET below guards the rest: over it, the warning
# prints first, where truncation cannot reach it.
#
# Never blocks session start. Any missing file is skipped and the hook exits 0.

# Well under the observed cap. 14565 bytes truncated; 2048 survived.
BUDGET=8000

root="${CLAUDE_PLUGIN_ROOT:-$(dirname -- "$0")/..}"
# The injected text names check.py and RULES.md, so it must carry paths the
# agent can actually run from anywhere. Resolve to absolute; keep as-is if the
# directory is unreadable.
abs="$(CDPATH= cd -- "$root" 2>/dev/null && pwd)" && root="$abs"
conventions="$root/CONVENTIONS.md"
skill="$root/skills/writing-voice/SKILL.md"
voice="$root/skills/writing-voice"

# Drop a leading YAML frontmatter block. An unterminated fence is not
# frontmatter, so the file prints whole unless the closing --- exists.
strip_frontmatter() {
  if [ "$(head -n 1 "$1")" = "---" ] && tail -n +2 "$1" | grep -q '^---[[:space:]]*$'; then
    awk 'NR == 1 { next } !past && /^---[[:space:]]*$/ { past = 1; next } past' "$1"
  else
    cat "$1"
  fi
}

body=""
[ -f "$conventions" ] && body="$(cat "$conventions")"
[ -f "$skill" ] && body="$body
$(strip_frontmatter "$skill")"
body="$body

File paths for this install (run check.py from anywhere with this path):
- check.py: $voice/scripts/check.py
- RULES.md: $voice/RULES.md
- EXAMPLES.md: $voice/EXAMPLES.md"

size=$(printf '%s' "$body" | wc -c | tr -d ' ')
if [ "$size" -gt "$BUDGET" ]; then
  printf 'WARNING: these conventions are %s bytes and may have been truncated.\n' "$size"
  printf 'Read %s and %s in full before drafting.\n\n' "$conventions" "$skill"
fi

printf '%s\n' "$body"

exit 0
