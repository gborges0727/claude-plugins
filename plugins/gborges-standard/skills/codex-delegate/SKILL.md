---
name: codex-delegate
description: >-
  Delegate a coding subtask to the Codex CLI on GPT-5.6 Luna, spending ChatGPT-plan quota instead
  of Claude tokens. Use only when the per-message hook line says Codex delegation is on for this
  machine. Then prefer this over the sonnet-medium subagent whenever the subtask is mechanical and
  already fully specified: boilerplate, a repeated edit across many files, tests against an
  interface you can paste in, or a second-model opinion. Also use when the user says to delegate,
  hand off, or use Codex, and when continuing a Codex thread already started.
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

## Every call sets these

| Argument | Value | Why |
|---|---|---|
| `model` | `gpt-5.6-luna` | Always, unless the user names a different model in this conversation |
| `config` | `{"model_reasoning_effort": "xhigh"}` | Luna thinks hard for its tier, which is what makes it worth delegating to |
| `cwd` | absolute path to the repo | Codex resolves a relative path against the MCP server's own working directory, not yours |
| `sandbox` | `read-only` to investigate, `workspace-write` to edit | The sandbox is the guardrail, since approvals are off |
| `approval-policy` | `never` | Codex has no terminal to ask in. Any other policy stalls the call until it times out |

Luna is the model for every delegated call. Reach for `gpt-5.6-sol` in one case, when the task
must read more than Luna's 400K of context or write more than its 128K limit. Luna failing a
review is a reason to sharpen the prompt and send it back to Luna, not a reason to switch models.
Switch because the user said to.

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
