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

A delegation is one `codex exec` command run through the Bash tool with `run_in_background`
set. The command starts a Codex thread, runs it to the end, and writes Codex's final message to
a file. Claude Code notifies you when the process exits. Nothing in this session waits on it.

Do not delegate through the `mcp__codex__codex` tool. Claude Code runs MCP tool calls one at a
time and a Codex call returns only when the whole task is done, so a fan-out of five lanes
through MCP starts the fifth lane eight minutes after the first. The MCP tool remains fine for
one short question where you would wait for the answer anyway.

## Check the binary exists first

This bundle also installs into Codex, so a session running this skill may already be Codex. When
you are Codex, skip the skill and do the work yourself. Handing a Codex subtask to Codex buys
nothing and spends the allowance twice.

Run `command -v codex` before planning any of what follows. A cloud VM and a fresh machine both
run this bundle without a Codex install, so the binary is often absent. When it is, do the work
in this session and say once, in a sentence, that Codex was not reachable. Installing and
signing in (`codex login`) is the user's step, not yours.

## The allowance you are spending

Codex signs in through the ChatGPT account, not an API key, so a delegated run spends the same
five-hour allowance as the Codex web app and the IDE extension. Delegating a whole afternoon of
work can drain the allowance the user also wants for their own Codex sessions.

## What to delegate

Codex on this machine has the same tools, MCP servers, and skills as this session. The one thing
it lacks is this conversation. So the host question is two questions. Does the brief stand alone
from what was said here? Does a command check the result?

Hand Codex any brief that answers yes to both: renaming a symbol across forty files, writing
tests against an interface you paste in, porting one pattern to every call site, filling in
boilerplate whose shape you already decided, or finding why a named test fails. Pick the
rung that mirrors the Claude agent the task would have taken.

Keep in this session anything that needs the conversation (design decisions, work in a codebase
you are still mapping, any task whose spec you would have to discover while doing it) and any
task whose result is a conclusion nobody downstream checks. Codex starts blind to this
conversation, so a prompt that leans on what was said here sends Codex off to guess, and a wrong
conclusion with no check is the failure nothing catches.

## Pick the rung

Four Codex rungs mirror the plugin's four Claude agents. Each is a model plus an effort, and the
name says both.

| Rung | `-m` | Effort | Mirrors | Takes |
|---|---|---|---|---|
| `luna-xhigh` | `gpt-5.6-luna` | `xhigh` | `sonnet-medium` | An edit or a run whose brief names the exact change and a command that checks it. Parallel copies of one such task. Never a brief past 272K tokens, since Luna's recall past 256K is 41% |
| `sol-xhigh` | `gpt-5.6-sol` | `xhigh` | `opus-medium` | The default. Any task that reads code to reach a result a command can check, any second-model opinion, and any brief that must read past 272K tokens |
| `astra-medium` | `gpt-6-astra` | `medium` | `opus-xhigh` | A task that failed once on a lower rung. One long dependent chain. The orchestrator picks this on its own |
| `astra-xhigh` | `gpt-6-astra` | `xhigh` | `fable-xhigh` | Only when the user's latest message names Astra. A hook refuses any Astra run above medium the user did not ask for |

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
hook fills in medium on an unnamed Astra run that set no effort, and xhigh on a named one.
`ultra` spawns subagents inside the run and multiplies what one run spends, so leave it to the
user to ask for.

`docs/model-routing.md` in this repo holds the prices and scores behind the table.

## The command

Write the brief to a file in the scratchpad first, then run this with `run_in_background` set:

```sh
codex exec -m gpt-5.6-luna -c model_reasoning_effort=xhigh \
  -C /absolute/path/to/repo -s workspace-write -c approval_policy=never \
  -c mcp_servers.playwright.enabled=false -c mcp_servers.chrome-devtools.enabled=false \
  --json -o <scratch>/<lane>.md - < <scratch>/<lane>.brief.md > <scratch>/<lane>.jsonl 2>&1
```

| Part | Why |
|---|---|
| `-m` and `-c model_reasoning_effort=` | The rung. Unpinned, Codex runs the orchestrator model from `~/.codex/config.toml` at its own default effort, which is low on Sol. The hook fills in the effort when the command omits it |
| `-C /absolute/path` | Codex resolves a relative path against its own working directory, not yours |
| `-s read-only` to investigate, `-s workspace-write` to edit | The sandbox is the guardrail, since approvals are off |
| `-c approval_policy=never` | Codex has no terminal to ask in. Any other policy stalls the run |
| the two `mcp_servers...enabled=false` flags | Each Codex thread otherwise starts its own Playwright and Chrome DevTools servers, each with a headless Chrome, and they outlive the thread. Drop the flags only for a brief that needs a browser |
| `--json` | Prints one event per line to stdout. The first line holds the `thread_id` a follow-up needs |
| `-o <lane>.md` | Codex writes its final message here. Read this file, not the JSON stream |
| `- < <lane>.brief.md` | The prompt comes from the file, so no shell quoting touches it. `codex exec` reads stdin either way, so always redirect it |
| `> <lane>.jsonl 2>&1` | Keeps the event stream out of the tool result and on disk for a failed run |

`codex exec` refuses to run outside a git repository unless `--skip-git-repo-check` is set. A
directory Codex has not seen before may also need a trust entry in `~/.codex/config.toml`:

```toml
[projects."/absolute/path"]
trust_level = "trusted"
```

## Write the brief

State the task, the files, the constraints, and the definition of done, the way you would brief a
contractor who has the repo and nothing else. Paste the interface, the example, the error text.

Codex's final message enters this context when you read it, so a chatty delegate costs Claude
tokens on the way back. End every brief with a return contract:

> Return under 15 lines: every file you changed and what changed in it, then anything you could
> not finish. No transcript, no narration, no code blocks unless the diff itself is the answer.

## Fanning out

Every lane is its own background Bash call, so issue all of them in one message and they start
within seconds of each other. Give each lane its own `.brief.md`, `.md`, and `.jsonl` file.
Split the work so no two lanes touch the same file, or give each lane its own git worktree.
Parallel lanes editing one file overwrite each other, and neither summary mentions it.

Stopping a lane with `TaskStop` kills its `codex exec` process, which ends the Codex run and
stops its spending. Anything the lane wrote to the worktree before the stop is still there.

## Follow-ups

The first line of a lane's `.jsonl` file names its thread:

```json
{"type":"thread.started","thread_id":"01a0..."}
```

Continue that thread with `codex exec resume <thread_id> - < <scratch>/<lane>.next.md`, with
the same `-m`, `-c`, `--json`, and `-o` flags and again in the background. `resume` has no
`-C` or `-s` flag. The thread remembers its directory, and `-c sandbox_mode=workspace-write`
sets the sandbox. Codex
keeps the thread's history, so the follow-up needs only the new instruction.

## Verify before you build on it

Codex's final message is a claim, not a result. Run `git status` and read the diff of every file
it names, plus any file it changed without naming. The step is done when you have read the diff
of every changed file and run whatever the repo uses to check it, tests or typecheck or lint.
Report what the diff actually shows, not what the message said. A lane whose `.md` file is
missing or empty ended early. Its `.jsonl` file holds the error.
