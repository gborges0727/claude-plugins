---
name: codex-delegate
description: >-
  Delegate a coding subtask to the Codex CLI on an OpenAI model (GPT-5.6 Luna, Terra, Sol, or
  GPT-6 Astra), spending ChatGPT-plan quota instead of Claude tokens. Use only when
  `~/.claude/gborges-standard.json` says `"codex": true` (a missing file means off). Then prefer
  this over the sonnet-medium subagent whenever the subtask is mechanical and already fully
  specified: boilerplate, a repeated edit across many files, tests against an interface you can
  paste in, or a second-model opinion. Also use when the user says to delegate, hand off, or use
  Codex, when the user names a Codex rung (consult astra, ask sol, send it to terra, luna), and
  when continuing a Codex thread already started.
---

# Codex delegation

Delegation runs on two tools that a registered Codex MCP server provides:

- `mcp__codex__codex` starts a thread. It returns Codex's final text and a `threadId`.
- `mcp__codex__codex-reply` continues that thread. It takes `threadId` and `prompt`.

## Check the tools exist first

This bundle also installs into Codex, so a session running this skill may already be Codex. When
you are Codex, skip the skill and do the work yourself. Handing a Codex subtask to Codex buys
nothing and spends the allowance twice.

Look for `mcp__codex__codex` in your available tools before planning any of what follows. A cloud
VM and a fresh machine both run this bundle without a Codex install, so the tools are often
absent.

When they are absent, do the work in this session and say once, in a sentence, that Codex was not
reachable. Offer the registration command only if the user asks how to get it:

```
claude mcp add --transport stdio --scope user codex -- codex mcp-server
```

That command needs the Codex CLI installed and `codex login` already run, so it is the user's
step, not yours. A session that adds the server mid-conversation still sees no tools until it
restarts.

## The allowance you are spending

Codex signs in through the ChatGPT account, not an API key, so a delegated call spends the same
five-hour allowance as the Codex web app and the IDE extension. Delegating a whole afternoon of
work can drain the allowance the user also wants for their own Codex sessions.

## What to delegate

Hand Codex work that is wide, mechanical, and fully specifiable in one prompt: renaming a symbol
across forty files, writing tests against an interface you paste in, porting one pattern to every
call site, filling in boilerplate the shape of which you already decided.

Keep in this session anything that needs the conversation: design decisions, work in a codebase
you are still mapping, and any task whose spec you would have to discover while doing it. Codex
starts blind. It reads none of this conversation, so a prompt that leans on what was said here
sends Codex off to guess.

## Pick the rung

Four Codex rungs mirror the plugin's four Claude agents. Each is a `model` plus a
`model_reasoning_effort`, and the name says both.

| Rung | `model` | Effort | Mirrors | Takes |
|---|---|---|---|---|
| `luna-xhigh` | `gpt-5.6-luna` | `xhigh` | `sonnet-medium` | An edit or a run whose brief names the exact change and a command that checks it. Parallel copies of one such task. Never a brief past 272K tokens, since Luna's recall past 256K is 41% |
| `terra-xhigh` | `gpt-5.6-terra` | `xhigh` | `opus-medium` | The default. Any task that reads code to reach a conclusion, and any second-model opinion |
| `sol-xhigh` | `gpt-5.6-sol` | `xhigh` | `opus-xhigh` | A task that failed once on a lower rung. One long dependent chain. Any brief that must read past 272K tokens |
| `astra-xhigh` | `gpt-6-astra` | `xhigh` | `fable-xhigh` | Only when the user's latest message names Astra. A hook refuses every other Astra call and points it at Sol |

A failure on one rung is first a reason to reread the brief for a bad spec and resend it to the
same rung. Escalate one rung, once, when the brief's own check failed or Codex said it could not
finish, and put the exact failing output in the escalated brief. After a second failure report
to the user instead of climbing again.

Astra costs the same per token as Fable and drains the ChatGPT allowance faster than Sol, so the
orchestrator never chooses it. The user does, by naming it ("consult astra", "ask astra xhigh").
Astra at `max` or `ultra` is never set from here: `ultra` spawns subagents inside the call and
multiplies what one call spends, and the API tops out at `max` anyway.

`docs/model-routing.md` in this repo holds the prices and scores behind the table.

## Every call sets these

| Argument | Value | Why |
|---|---|---|
| `model` | the rung's model | Unpinned, Codex runs the orchestrator model from `~/.codex/config.toml`, which is Sol |
| `config` | `{"model_reasoning_effort": "xhigh"}` | One shot with no conversation to correct it, so the effort that avoids a retry is the cheap one |
| `cwd` | absolute path to the repo | Codex resolves a relative path against the MCP server's own working directory, not yours |
| `sandbox` | `read-only` to investigate, `workspace-write` to edit | The sandbox is the guardrail, since approvals are off |
| `approval-policy` | `never` | Codex has no terminal to ask in. Any other policy stalls the call until it times out |

Every model here reads up to 1,050,000 tokens and writes up to 128,000 on the API, and OpenAI
reprices the whole request (double input, output up by half) once the input passes 272K tokens.
Keep briefs under that line unless the task needs the room, and then send it to Sol or Astra.

## Write the prompt as a briefing

State the task, the files, the constraints, and the definition of done, the way you would brief a
contractor who has the repo and nothing else. Paste the interface, the example, the error text.

Codex's reply lands in this context whole, so a chatty delegate costs Claude tokens on the way
back. End every prompt with a return contract:

> Return under 15 lines: every file you changed and what changed in it, then anything you could
> not finish. No transcript, no narration, no code blocks unless the diff itself is the answer.

## Verify before you build on it

Codex's summary is a claim, not a result. Run `git status` and read the diff of every file it
names, plus any file it changed without naming. The step is done when you have read the diff of
every changed file and run whatever the repo uses to check it, tests or typecheck or lint. Report
what the diff actually shows, not what the summary said.

## Fanning out

Several `mcp__codex__codex` calls in one message run at once. Split the work so no two workers
touch the same file, or give each one its own git worktree. Parallel workers editing one file
overwrite each other, and neither summary mentions it.

## When Codex refuses to start

Codex only runs inside a git repository or a directory marked trusted. The MCP tools expose no
flag to skip that check, so add the directory to `~/.codex/config.toml`:

```toml
[projects."/absolute/path"]
trust_level = "trusted"
```
