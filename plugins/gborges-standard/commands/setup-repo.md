---
description: Ask where this repo keeps agent-written documents and whether specs become GitHub issues, then write .claude/gborges-standard.json at the repo root.
disable-model-invocation: true
---

# Setup repo

## Step 1: Ask

Call AskUserQuestion once with both questions in the one call.

Ask which folder specs, research notes, handoffs, wayfinder maps, and
routine specs go under. Offer "docs" (the default) and let the user type
another folder name. Each skill writes under its own subfolder there, for
example `docs/specs/` and `docs/handoff/`.

Ask whether specs and tickets should also become GitHub issues. Offer "Files
only" (the skills write files under the docs folder and touch GitHub only
when asked) and "GitHub issues" (the `spec` and `wayfinder` skills also open
one issue per spec, ticket, map, or question). Files only is the default.

## Step 2: Write the file

Turn the answers into a folder name and `files` or `github`, then run:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-repo.sh" --docs <folder> --tracker <files|github>
```

## Step 3: Report

Print the `Wrote ...` line the script printed. Say nothing else.
