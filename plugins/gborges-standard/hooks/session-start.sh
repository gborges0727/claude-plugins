#!/usr/bin/env sh
# SessionStart hook: prints the working conventions followed by the full
# writing-voice ruleset, so the rules are present every session and after every
# compaction rather than waiting on a skill to trigger.
#
# The skill sets disable-model-invocation, so this hook is the only loader.
# EXAMPLES.md stays out: it is read on demand when a rule call is ambiguous.
#
# Never blocks session start. Any missing file is skipped and the hook exits 0.

root="${CLAUDE_PLUGIN_ROOT:-$(dirname -- "$0")/..}"
conventions="$root/CONVENTIONS.md"
skill="$root/skills/writing-voice/SKILL.md"

[ -f "$conventions" ] && cat "$conventions"

if [ -f "$skill" ]; then
  printf '\n'
  # Strip a leading YAML frontmatter block. An unterminated fence is not
  # frontmatter, so the file is printed whole unless the closing --- exists.
  awk '
    NR == FNR {
      if (FNR == 1 && $0 ~ /^---[[:space:]]*$/) { open = 1; next }
      if (open && $0 ~ /^---[[:space:]]*$/) { open = 0; closed = 1 }
      next
    }
    FNR == 1 { skipping = closed }
    skipping && FNR == 1 { next }
    skipping && $0 ~ /^---[[:space:]]*$/ { skipping = 0; next }
    !skipping { print }
  ' "$skill" "$skill"
fi

exit 0
