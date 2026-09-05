# Subagent routing

How the orchestrating session picks a subagent, and the cost reasoning
behind the ladder. The rule itself lives in the output style's Subagents
section, `plugins/gborges-standard/output-styles/plain-english.md`. This
file holds the why, so the rule can stay short. Prices and published
numbers below are from Anthropic's API pricing, its cost guidance, and its
Fable 5.1 prompting guide as of 2026-09-01.

## The four agents

| Agent | Model | Effort | Takes |
|---|---|---|---|
| `sonnet-medium` | Sonnet 5 | medium | An edit or a run whose brief names the exact change and a command that checks it. Parallel copies of one such task across files. Fetching a named doc page outside the codebase |
| `opus-medium` | Opus 5 | medium | The default. The floor for any task that reads code to reach a conclusion |
| `opus-xhigh` | Opus 5 | xhigh | A task that failed once below it. A task that is one dependent chain the orchestrator cannot split. The stand-in for Fable on an account without it |
| `fable-xhigh` | Fable 5.1 | xhigh | Only when the user's message names `@agent-fable-xhigh` |

Each name states its model and effort so the orchestrator sees the cost of
a dispatch in the name it types.

## Prices

| Model | Input, $ per million tokens | Cache hit, $ per million tokens | Output, $ per million tokens | Against Opus 5 (input, cache hit, output) |
|---|---|---|---|---|
| Sonnet 5 | 2 | 0.20 | 10 | 40%, 40%, 40% |
| Opus 5 | 5 | 0.50 | 25 | 100%, 100%, 100% |
| Fable 5.1 | 10 | 0.25 | 50 | 200%, 50%, 200% |

Fable 5.1 prices a cache hit at 2.5% of its input price, where every other
model uses 10%, so a Fable 5.1 cache hit costs half of an Opus 5 cache hit.
A subagent that reads many files sends its
whole context back on every turn, and after the first turn most of that
input is cache hits, so Fable 5.1 pays less than Opus 5 for those tokens.
Uncached input and output stay at double. Nobody has measured what share
of a real dispatch's tokens are cache hits, so 200% is the ceiling on the
Fable premium and 50% is the floor.

Per-token price is an input to the analysis, not the ranking. The ranking
is cost per finished task, which counts the retry a cheap failure causes
and the orchestrator tokens spent writing the brief again.

## Why Opus at medium is the default

Anthropic's coding runs on Opus 5 put the effort curve like this. At
`medium`, Opus 5 gives up about 2 points of pass rate for half the cost of
the default (`high`). At `low` it gives up about 8 points for a quarter of
the cost. Two points is the price of halving the bill, and eight points is
not, so `medium` is the default and `low` appears nowhere in the ladder.

On research and knowledge work the curve is nearly flat. `medium` matched
the default's accuracy at 70% to 85% of its cost across four benchmarks,
so nothing there argues for a higher default either.

## Why Sonnet stays out of code investigation

Sonnet reached wrong conclusions investigating codebases in this user's
own sessions more than once. A wrong conclusion is the most expensive
failure a subagent can produce, because nothing downstream catches it and
the orchestrator builds on it. Anthropic's guidance says the same thing in
general terms. Price models on the hardest tenth of the work, because the
tasks a cheap model fails decide the bill. On one twenty-problem research
run two problems carried 43% of the spend.

So Sonnet takes only work whose result a command can check. A test suite,
a build, or a diff that applies is a checker that costs no judgment. Code
investigation has no such checker, and it goes to Opus or higher.

## Why the ladder escalates instead of starting high

In Anthropic's coding runs, running every task at `low` and re-running
only the failures at the default passed 93% of tasks for about $0.70 per
task. Running everything at the default passed 91.7% for $1.39. Starting at
`medium` and escalating failures passed about 94% for $0.95. Escalating
after a failed check beats picking the strong setting up front, as long as
the task carries a failure signal.

The ladder here keeps three brakes so escalation stays rare:

- Only a failed check named in the brief, or the agent's own report that
  it could not finish, triggers a step. The orchestrator's opinion of the
  result does not.
- Before escalating, the orchestrator rereads the failure for a bad brief
  (wrong file, missing constraint, a request the repo cannot satisfy) and
  re-runs the fixed brief on the same agent. Most first failures on
  mechanical work are spec failures.
- A task climbs one step, once. A second failure goes back to the user,
  because two failures in a row on checkable work usually mean the brief is
  wrong, not the model.

The escalated brief is the same brief plus the exact failure output. A
summary of what the first agent tried steers the stronger model into the
same dead end.

## Why there is no Sonnet at xhigh

Anthropic's guidance is to sweep effort on the current model before
dropping a tier, and it reports that the larger model at lower effort often
wins on cost per task. Fable 5 at `low` beat Sonnet 5 on a deep-research
benchmark while costing about 10% less per task. Nobody has measured Sonnet
5 at `xhigh` against Opus 5 at `medium` on this user's work, and a fourth
agent makes every dispatch a harder choice. The model step is the one the
published numbers say moves accuracy, so a failed Sonnet task goes to Opus
at `medium`, not to Sonnet at a higher effort.

## Why Fable is user-only

Fable costs double Opus on uncached input and on output, and on a coding
subset Opus 5 matched Fable 5 (91.7% against 91.3%) at about 60% of its
cost. Those are Fable 5 numbers. Anthropic's Fable 5.1 prompting guide
says the 5.1 gains over Fable 5 are largest at the higher effort levels,
that 5.1 at `medium` roughly matches Fable 5 at lower cost, and that 5.1
at `low` is often competitive with Opus and Sonnet on cost per task while
scoring higher. None of that is measured on this user's briefs.

The same guide says 5.1 at `low` calls search and retrieval tools less
often and answers from memory instead. On a code investigation that is a
wrong conclusion nobody catches, the failure that keeps Sonnet out of that
work. So a `fable-low` or `fable-medium` rung waits on a measurement
against `opus-medium` on real briefs, and the rule stands until then.

The orchestrator judging a task "hard enough for Fable" is the guess that
spends the most money when wrong, so no judgment is allowed. Cheaper cache
hits do not change that, because the guess is about which task deserves
the model, not about the per-token price. The user types
`@agent-fable-xhigh`, and a hook refuses every dispatch that did not follow
such a message.

## What the dispatch history says

Across 34 sessions on this user's desktop, 242 subagent calls went out.
188 (78%) went to the old `default-agent`, 22 to Explore, 20 to the
built-in general-purpose agent, and the rest to one-off types. Only 11
calls passed a `model` override, all of them `opus`.

A keyword pass over the 188 `default-agent` briefs splits them as 102
edits (54%), 72 investigations (38%), 6 runs (3%), 1 doc fetch, and 7
unclassified. The median brief runs 2,763 characters.

So the Sonnet slot covers at most the 54% of edits that carry a command
check, and the 38% that investigate code stay on Opus by rule. Against
per-token price, moving every eligible edit to Sonnet cuts those
dispatches' cost by 60%. Some of those runs will fail and escalate, so the
true saving on that slice sits below 60% and above zero until it is
measured on real briefs.

## The setup file

`~/.claude/gborges-standard.json` holds two per-machine switches:

```json
{"fable": true, "codex": false}
```

`fable` false makes the dispatch hook rewrite `fable-xhigh` to
`opus-xhigh`, so an account without Fable never pays for a failed call.
`codex` true tells the orchestrator, through one line the per-message hook
adds, to send fully specified mechanical work to the `codex-delegate` skill
ahead of `sonnet-medium`. A missing file means Fable on and Codex off.

`/gborges-standard:setup` writes the file from two questions.
`plugins/gborges-standard/scripts/setup.sh --fable off --codex off` writes
it with no model turn, which is the form a cloud environment's setup script
can call.

A third flag, `--codex-config on`, writes the Codex CLI's copy of this
routing: four agents under `~/.codex/agents` (`luna-xhigh` for fully
specified edits, `sol-xhigh` as the default worker, `astra-medium` as the
escalation step, `astra-xhigh` only when the user names it), the `[agents]`
defaults in `~/.codex/config.toml` that send an unnamed spawn to Sol at
xhigh, the orchestrator model, and the status line. The README's Codex
section lists the mapping.

## The hooks

`hooks/route-spawns.py` runs before every Agent dispatch, including the
ones a skill or a forked agent makes. It rewrites an unpinned type
(`general-purpose`, `claude`, `default-agent`, or none) to `opus-medium`,
so a built-in skill's spawns land on the default instead of the session's
model. It refuses a `fork` on a Fable session, since a fork copies the
whole transcript onto the session's model, with a reason that tells the
orchestrator to send the task to `opus-medium` with a brief. The fork
passes on any other session, and on Fable when the user's latest message
used the word fork or the session's model cannot be read from the
transcript.

The same hook refuses a `fable-xhigh` dispatch
unless the latest user message named the agent, with a reason that points
the orchestrator at `opus-xhigh`. When the setup file says Fable is off,
it rewrites the dispatch to `opus-xhigh` instead. It then appends the
writing rules, and on a spawn that does go to Fable it also appends
Anthropic's long-output note, which tells Fable at xhigh to write a long
deliverable once instead of drafting it in thinking and again as the reply.

`hooks/remind-writing-rules.py` runs on every user message. It records
whether the message named `@agent-fable-xhigh`, and whether it used the
word fork, in two per-session state files under
`~/.claude/gborges-standard/state/`.

`hooks/route-codex.py` runs before every Codex delegation. That is a
Bash call whose command runs `codex exec`, the way the `codex-delegate`
skill starts a lane, or an `mcp__codex__codex` call. It lets a run on
`gpt-6-astra` go at medium, the escalation rung, on the orchestrator's
own judgment. Above medium it refuses the run unless the latest user
message named Astra, with a reason that points the orchestrator at Astra
at medium. When a run sets no effort it fills in `xhigh`, or `medium` on
an unsummoned Astra run. On a command the fill-in inserts `-c
model_reasoning_effort=...` right after `codex exec`. Every other Bash
command passes untouched. The four Codex rungs, their prices, and the
scores behind them are in `docs/model-routing.md`.

`tests/test_hooks.py` covers all three hooks and runs in CI.
