---
name: codex-delegate
description: >-
  Delegate a coding subtask to the Codex CLI on an OpenAI model (GPT-5.6 Luna, GPT-5.6 Sol, or
  GPT-6 Astra), spending ChatGPT-plan quota instead of Claude tokens. Use only when
  `~/.claude/gborges-standard.json` says `"codex": true` (a missing file means off). Then prefer
  this over a Claude subagent whenever the brief stands alone from the conversation and a command
  checks the result: boilerplate, a repeated edit across files, tests against a pasted interface,
  a bug a named test confirms, or a second-model opinion. Also use when the user says to delegate
  or use Codex, names a Codex rung (consult astra, ask sol, send it to luna), or continues a
  Codex thread.
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

Codex on this machine has the same tools, MCP servers, and skills as this session. The one thing
it lacks is this conversation. So the host question is two questions. Does the brief stand alone
from what was said here? Does a command check the result?

Hand Codex any brief that answers yes to both: renaming a symbol across forty files, writing
tests against an interface you paste in, porting one pattern to every call site, filling in
boilerplate the shape of which you already decided, or finding why a named test fails. Pick the
rung that mirrors the Claude agent the task would have taken.

Keep in this session anything that needs the conversation (design decisions, work in a codebase
you are still mapping, any task whose spec you would have to discover while doing it) and any
task whose result is a conclusion nobody downstream checks. Codex starts blind to this
conversation, so a prompt that leans on what was said here sends Codex off to guess, and a wrong
conclusion with no check is the failure nothing catches.

## Pick the rung

Four Codex rungs mirror the plugin's four Claude agents. Each is a `model` plus a
`model_reasoning_effort`, and the name says both.

| Rung | `model` | Effort | Mirrors | Takes |
|---|---|---|---|---|
| `luna-xhigh` | `gpt-5.6-luna` | `xhigh` | `sonnet-medium` | An edit or a run whose brief names the exact change and a command that checks it. Parallel copies of one such task. Never a brief past 272K tokens, since Luna's recall past 256K is 41% |
| `sol-xhigh` | `gpt-5.6-sol` | `xhigh` | `opus-medium` | The default. Any task that reads code to reach a result a command can check, any second-model opinion, and any brief that must read past 272K tokens |
| `astra-medium` | `gpt-6-astra` | `medium` | `opus-xhigh` | A task that failed once on a lower rung. One long dependent chain. The orchestrator picks this on its own |
| `astra-xhigh` | `gpt-6-astra` | `xhigh` | `fable-xhigh` | Only when the user's latest message names Astra. A hook refuses any Astra call above medium the user did not ask for |

Terra has no rung. On long-horizon coding it passes 23 points fewer tasks than Sol while
spending 2.6 times the output tokens, so it costs more per finished task than Sol on the work
the default rung sends, and Luna already covers the short work at a quarter of Terra's price.

A failure on one rung is first a reason to reread the brief for a bad spec and resend it to the
same rung. Escalate one rung, once, when the brief's own check failed or Codex said it could not
finish, and put the exact failing output in the escalated brief. The escalation is a model step,
Sol to Astra, because Astra leads Sol by 20 points on Terminal-Bench 4.0 while Sol at max scores
the same as Sol at xhigh. After a second failure report to the user instead of climbing again.

Astra costs 2.5 times Sol per token and per unit of ChatGPT allowance. At medium it is the
escalation rung and needs no permission. Above medium (high, xhigh, max, ultra) it runs only
when the user named Astra in their latest message ("consult astra", "ask astra at max"). The
hook fills in medium on an unnamed Astra call that set no effort, and xhigh on a named one.
`ultra` spawns subagents inside the call and multiplies what one call spends, so leave it to the
user to ask for.

`docs/model-routing.md` in this repo holds the prices and scores behind the table.

## Every call sets these

| Argument | Value | Why |
|---|---|---|
| `model` | the rung's model | Unpinned, Codex runs the orchestrator model from `~/.codex/config.toml`, which is Sol |
| `config` | `{"model_reasoning_effort": "xhigh"}`, or `"medium"` on the escalation rung | One shot with no conversation to correct it, so the effort that avoids a retry is the cheap one |
| `cwd` | absolute path to the repo | Codex resolves a relative path against the MCP server's own working directory, not yours |
| `sandbox` | `read-only` to investigate, `workspace-write` to edit | The sandbox is the guardrail, since approvals are off |
| `approval-policy` | `never` | Codex has no terminal to ask in. Any other policy stalls the call until it times out |

Every model here reads up to 1,050,000 tokens and writes up to 128,000 on the API, and OpenAI
reprices the whole request (double input, output up by half) once the input passes 272K tokens.
Keep briefs under that line unless the task needs the room, and then send it to Sol.

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
