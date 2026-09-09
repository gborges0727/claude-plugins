---
description: Ask which models this machine can reach and whether Claude Code may add AI attribution, write the answers to ~/.claude/gborges-standard.json and ~/.claude/settings.json, and write the Codex CLI's model and status line config.
disable-model-invocation: true
---

# Setup

## Step 1: Ask

Call AskUserQuestion once with all four questions in the one call.

Ask whether this account can run the Claude Fable 5.1 model. Offer "Yes" (the
account has Fable, so the fable-xhigh subagent runs as written) and "No" (the
hook rewrites fable-xhigh to opus-xhigh). Yes is the default.

Ask whether to delegate mechanical work to the Codex CLI. Offer "Off" (every
subagent is a Claude subagent) and "On" (fully specified mechanical work goes
to the codex-delegate skill first). Off is the default.

Ask whether to write the Codex CLI's own config. Offer "Yes" (the script
writes four agents under `~/.codex/agents`, the subagent defaults, the
orchestrator model, and the status line into `~/.codex/config.toml`) and "No"
(nothing under `~/.codex` changes). Yes is the default when `codex` is on
PATH, otherwise No.

Ask whether Claude Code may add AI attribution to commits and PR bodies.
Offer "No" (the script writes the `attribution` key in
`~/.claude/settings.json` with empty commit and PR text and the session link
off, so the prompt never asks for a trailer) and "Yes" (the script deletes
the key, so Claude Code adds its default Co-Authored-By trailer and
"Generated with Claude Code" footer). No is the default.

## Step 2: Write the files

Turn the four answers into `on` or `off` and run:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh" --fable <on|off> --codex <on|off> --codex-config <on|off> --attribution <on|off>
```

## Step 3: Report

Print the `Wrote ...` lines the script printed. Say nothing else.
