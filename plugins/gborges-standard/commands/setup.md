---
description: Ask which models this machine can reach and write the answers to ~/.claude/gborges-standard.json.
disable-model-invocation: true
---

# Setup

## Step 1: Ask

Call AskUserQuestion once with both questions in the one call.

Ask whether this account can run the Claude Fable 5 model. Offer "Yes" (the
account has Fable, so the fable-xhigh subagent runs as written) and "No" (the
hook rewrites fable-xhigh to opus-xhigh). Yes is the default.

Ask whether to delegate mechanical work to the Codex CLI. Offer "Off" (every
subagent is a Claude subagent) and "On" (fully specified mechanical work goes
to the codex-delegate skill first). Off is the default.

## Step 2: Write the file

Turn the two answers into `on` or `off` and run:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh" --fable <on|off> --codex <on|off>
```

## Step 3: Report

Print the `Wrote ...` line the script printed. Say nothing else.
