# Model routing across Claude and Codex

Which model takes which kind of delegated work, on both hosts, and the
prices and published scores behind each choice. The rules themselves live
in two places: the output style's Subagents section for the Claude ladder,
and the `codex-delegate` skill's table for the Codex ladder. This file
holds the numbers and the reasons, so those rules can stay short.

The `model-routing-review` skill rebuilds this file when either vendor
ships a model or moves a price. Every number carries its date and source
so the next review can tell what moved.

Last reviewed 2026-09-04 against Codex CLI 0.153.3.

## The two ladders

Each Claude rung has one Codex rung that takes the same kind of work. A
name states its model and effort, so the orchestrator sees the cost of a
dispatch in the name it types.

| Rung | Claude agent | Codex agent | Takes |
|---|---|---|---|
| mechanical | `sonnet-medium` | `luna-xhigh` | An edit or a run whose brief names the exact change and a command that checks it. Parallel copies of one such task. Fetching a named doc page |
| default | `opus-medium` | `terra-xhigh` | Any task that reads code to reach a conclusion (an investigation, a diagnosis, a review, a design choice) |
| escalation | `opus-xhigh` | `sol-xhigh` | A task that failed once below it. One long dependent chain the orchestrator cannot split. On Codex, also any brief that must read past 272K tokens |
| summoned | `fable-xhigh` | `astra-xhigh` | Only when the user's own message names the agent |

On Claude Code, a Codex rung is not a Claude agent. It is a call to the
`mcp__codex__codex` tool with the rung's model and effort, and the
`codex-delegate` skill makes that call. In the Codex CLI, the same four
rungs are agent files under `~/.codex/agents` that `setup.sh` writes.

## Prices

Standard API prices in dollars per million tokens. Codex delegations from
Claude Code spend ChatGPT plan allowance rather than API dollars. OpenAI's
Codex rate card prices that allowance in credits per million tokens
(input, cache hit, output): Astra 250, 25, 1,250. Sol 100, 10, 500. Terra
50, 5, 300. Luna 5, 0.5, 30. Those ratios match the API list prices, so
the API price is the plan burn rate too.

| Model | Input | Cache hit | Output | Long context (past 272K input) | Source date |
|---|---|---|---|---|---|
| GPT-5.6 Luna | 0.20 | 0.02 | 1.20 | 0.40 / 0.04 / 1.80 | 2026-07-30 cut, checked 2026-09-04 |
| GPT-5.6 Terra | 2 | 0.20 | 12 | 4 / 0.40 / 18 | 2026-07-30 cut, checked 2026-09-04 |
| GPT-5.6 Sol | 4 | 0.40 | 20 | 8 / 0.80 / 30 | 2026-08-21 cut, promised through 2026-11-21, then 5 / 0.50 / 30 |
| GPT-6 Astra | 10 | 1 | 50 | 20 / 2 / 75 | 2026-08 launch, checked 2026-09-04 |
| Claude Sonnet 5 | 2 | 0.20 | 10 | n/a | checked 2026-09-01 |
| Claude Opus 5 | 5 | 0.50 | 25 | n/a | checked 2026-09-01 |
| Claude Fable 5.1 | 10 | 0.25 | 50 | n/a | checked 2026-09-01 |

The OpenAI long-context row applies to the whole request once its input
passes 272K tokens: input and cache double, output goes up by half. Every
GPT-5.6 model and Astra list a 1,050,000-token window and a 128,000-token
output cap on the API. The Codex CLI catalog reports a 272,000-token
working window and an 872,000-token maximum for the same models.

Rung for rung, the Codex side is cheaper than the Claude side on every
token except Astra's cache hit:

| Rung | Claude, in / out | Codex, in / out | Codex as a share of Claude |
|---|---|---|---|
| mechanical | Sonnet 5, 2 / 10 | Luna, 0.20 / 1.20 | 10% / 12% |
| default | Opus 5, 5 / 25 | Terra, 2 / 12 | 40% / 48% |
| escalation | Opus 5, 5 / 25 | Sol, 4 / 20 | 80% / 80% |
| summoned | Fable 5.1, 10 / 50 | Astra, 10 / 50 | 100% / 100% |

Astra's cache hit costs 1.00 against Fable's 0.25, so a long
many-turn Astra session pays four times Fable's rate on the tokens it
resends. Per-token price is an input to the ranking, not the ranking. The
ranking is cost per finished task, which counts the retry a cheap failure
causes and the orchestrator tokens spent writing the brief again.

## Published scores

All OpenAI numbers ran at the model's maximum effort unless noted. Scores
compare safely only when the benchmark, the harness, and the effort match,
and the vendor tables mix all three, so treat a gap under three points as
noise.

| Benchmark | Luna | Terra | Sol | Astra | Claude | Source |
|---|---|---|---|---|---|---|
| Terminal-Bench 2.1 | 84.7 | 87.4 | 88.8 | | GPT-5.5 at 85.6 | LayerLens, July 2026 |
| Terminal-Bench 4.0 | | | 37.3 | 57.9 | Fable 5.1 at 55.8, Opus 5 at 52.3 | OpenAI Astra launch, Aug 2026 |
| SWE-Bench Pro | | 63.4 | 64.6 | | | LayerLens, July 2026 |
| DeepSWE v1.1 | | | 72.7 | 74.1 | | OpenAI Astra launch |
| Artificial Analysis Coding Agent Index | 74.6 | 77.4 | 80 | | Opus 4.8 at 72.5, Fable 5 at 82.8 | LayerLens, July 2026 |
| OSWorld 2.0 | 45.6 | 50.2 | 62.6 | 72.6 | Opus 4.8 at 54.8 | LayerLens and OpenAI |
| BrowseComp | 83.3 | 87.5 | 90.4 | 91.5 | | LayerLens and OpenAI |
| MRCR v2 8-needle, 256K to 512K | 41.3 | 89.6 | 91.5 | 100 | | LayerLens and OpenAI |
| MRCR v2 8-needle, 512K to 1M | 41.3 | 72.5 | 73.8 | 96.3 | | LayerLens and OpenAI |
| ExploitBench | 33.2 | 52.9 | 73.5 | 100 | Fable 5.1 at 70 | LayerLens and OpenAI |
| FrontierMath Tier 4 | | | | 97.6 | Fable 5.1 at 87.8, Opus 5 at 73.2 | OpenAI Astra launch |
| Humanity's Last Exam, with tools | | | | 57.2 | Fable 5.1 at 65.0, Opus 5 at 63.6 | OpenAI Astra launch |

What the rows say, one model at a time:

- Luna sits two to four points under Terra on coding and terminal work,
  and collapses on long context. Its recall past 256K tokens is 41%
  against Terra's 90%. So Luna takes narrow, fully specified work with a
  short brief, and nothing that must hold a large codebase in view.
- Terra trails Sol by one to two points on the coding benchmarks at half
  Sol's price, and OpenAI's own Codex docs call it "the pragmatic
  all-rounder". That is the default worker.
- Sol pulls ahead of Terra where the task is wide or adversarial:
  computer use (62.6 against 50.2), exploit work (73.5 against 52.9), and
  research browsing. It also keeps 74% recall between 512K and 1M tokens.
  That is the escalation step and the long-context step.
- Astra leads every OpenAI benchmark it appears on and beats Fable 5.1 on
  the agentic coding and math rows, while Fable 5.1 leads on Humanity's
  Last Exam with tools. On Terminal-Bench 4.0 OpenAI estimates Astra's API
  cost per task at 9% under Sol's and 63% under Fable 5.1's, because it
  spends fewer tokens to finish. At the same list price as Fable, Astra is
  the summoned rung, and the orchestrator never picks it on its own
  judgment.

## Effort

OpenAI's Codex docs say to start at a lower effort and raise it when the
work needs it: low for quick well-scoped tasks, medium as the balance,
high and xhigh for multi-step work, max for the hardest single problem
"when depth matters more than speed or usage", and ultra to split a task
across internal subagents. The docs add that "most tasks do not need Max
or Ultra". Ultra exists only inside Codex, and the API tops out at max.

Every Codex rung here runs at xhigh, for two reasons. A delegated call is
one shot with no conversation to correct it, so the effort that avoids a
retry is the cheap one. And the Codex catalog itself sets the effort for
its own multi-agent workers to xhigh on Astra.

One measurement on 2026-09-04 backs that for Terra. Three briefs ran once
each at medium and at xhigh, in separate scratch worktrees of this repo:
add a unit test file against a named function, find and fix a planted
bug that failed the suite, and answer four questions about the hooks with
file and line references. All six runs passed their check.

| Brief | Medium, tokens | Medium, seconds | xhigh, tokens | xhigh, seconds |
|---|---|---|---|---|
| add a test file | 30,095 | 40 | 30,801 | 51 |
| fix a planted bug | 41,009 | 49 | 21,790 | 43 |
| answer four code questions | 24,385 | 24 | 29,108 | 46 |
| total | 95,489 | 113 | 81,699 | 141 |

xhigh spent 14% fewer tokens in total and 25% more wall time, with the
same pass rate. On three briefs that is not an effort curve, but it says
medium buys nothing on the kind of brief the default rung gets, so xhigh
stays.

The same three briefs then ran on Luna and Sol through Codex and on Opus
5 through the plugin's `opus-medium` and `opus-xhigh` agents. All
eighteen runs passed. Token totals are what each host billed for the three runs, so
the Codex figures include Codex's own system prompt and the Opus figures
include Claude Code's plus the writing rules the spawn hook appends. The
API-equivalent cost takes 80% of tokens at the input price and 20% at
the output price.

| Model, effort | Tokens, three briefs | Seconds | API-equivalent cost |
|---|---|---|---|
| Luna, medium | 86,367 | 137 | $0.03 |
| Luna, xhigh | 87,304 | 166 | $0.03 |
| Terra, medium | 95,489 | 113 | $0.38 |
| Terra, xhigh | 81,699 | 141 | $0.33 |
| Sol, medium | 95,966 | 148 | $0.69 |
| Sol, xhigh | 98,292 | 179 | $0.71 |
| Opus 5, medium | 128,054 | 71 | $1.15 |
| Opus 5, xhigh | 137,221 | 108 | $1.23 |

Every model finished every brief, so these briefs cannot rank the models
on accuracy. They rank them on cost and speed for work all of them can
do: Luna costs 3% of Opus at medium, Terra at xhigh costs 29%, Sol costs
60%, and Opus finishes fastest. The Codex costs land on the ChatGPT plan allowance,
not the API bill. Ranking on the hard tenth of tasks still rests on the
published scores above, where Opus 5 leads Sol by 15 points on
Terminal-Bench 4.0.

The delegation never sets max or ultra. Ultra spawns subagents inside the
call, which multiplies the allowance one call spends, and a Plus plan
holds only a limited Astra allowance.

## Why the ladder changed on 2026-09-04

Before this review the Codex side ran Luna at xhigh as the default worker
and Luna at medium for mechanical work, with Terra as the escalation and
Sol as the summoned rung. Three facts moved it:

- OpenAI's Codex docs position Luna for "clear, repeatable tasks" and Terra
  for everyday work, and the long-context row above shows why.
- The Codex catalog marks Luna `multi_agent_version` v1 while Sol, Terra,
  and Astra are v2, so a Sol orchestrator in the Codex CLI refuses a
  spawn that names Luna by model. A custom agent file sometimes gets
  around that, sometimes not. Terra as the default spawn avoids the
  question.
- Astra shipped at Fable's price and above Fable on the agentic rows, so
  the summoned rung has a model to name, and Sol moves down to the
  escalation rung where its price (80% of Opus) fits.

## Open questions

- No effort curve is published for any GPT-5.6 model or for Astra. The
  Claude side runs Opus at medium because Anthropic published that curve.
  The three-brief Terra measurement above is one run per cell. A repeat on
  ten briefs with three runs each would give a curve worth acting on.
- Sol's price reverts on or after 2026-11-21 unless OpenAI extends it. At
  5 / 30 Sol still sits under Opus.

## Sources

- OpenAI API pricing, https://developers.openai.com/api/docs/pricing
- Model pages: https://developers.openai.com/api/docs/models/gpt-6-astra,
  https://developers.openai.com/api/docs/models/gpt-5.6-sol,
  https://developers.openai.com/api/docs/models/gpt-5.6-terra,
  https://developers.openai.com/api/docs/models/gpt-5.6-luna
- Codex model and effort guidance, https://learn.chatgpt.com/docs/models
- Codex subagent config, https://learn.chatgpt.com/docs/agent-configuration/subagents
- Luna and subagents v2, https://gist.github.com/kcosr/fa4807178bddb8cffe5896e37679c59b
- GPT-5.6 scores, https://layerlens.ai/blog/gpt-5-6-benchmark-review-sol-terra-luna
- Astra scores, https://openai.com/index/gpt-6-astra/ read through Codex's
  search tool (the page returns 403 to a plain fetch), cross-checked
  against https://www.vellum.ai/blog/gpt-6-astra-benchmarks-explained
- Codex credit rates, https://help.openai.com/en/articles/20001106-codex-rate-card,
  read the same way
- July price cut, https://community.openai.com/t/announcing-a-major-price-drop-for-5-6-terra-and-luna-and-fast-mode-for-5-6-sol/1388484
- August Sol cut, https://www.explainx.ai/blog/openai-gpt-5-6-sol-api-price-cut-20-percent-august-2026
- Anthropic prices, `docs/subagent-routing.md`, checked 2026-09-01
- The local catalog, `codex debug models`
