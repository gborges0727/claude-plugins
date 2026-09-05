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
| default | `opus-medium` | `sol-xhigh` | Any task that reads code to reach a conclusion (an investigation, a diagnosis, a review, a design choice). On Codex, also any brief that must read past 272K tokens |
| escalation | `opus-xhigh` | `astra-medium` | A task that failed once below it. One long dependent chain the orchestrator cannot split |
| summoned | `fable-xhigh` | `astra-xhigh` | Only when the user's own message names the agent. On Codex, any Astra call above medium effort |

On Claude Code, a Codex rung is not a Claude agent. It is a call to the
`mcp__codex__codex` tool with the rung's model and effort, and the
`codex-delegate` skill makes that call. In the Codex CLI, the same four
rungs are agent files under `~/.codex/agents` that `setup.sh` writes.

## Which host takes a task

Codex on a machine set up per `docs/codex-parity.md` has the same tools,
MCP servers, and skills as the Claude Code session. The one thing a
delegated Codex call lacks is the conversation. So when the setup file
says Codex is on, two questions pick the host:

1. Does the brief stand alone from the conversation? A brief that leans
   on what was said in the session stays on Claude.
2. Does a command check the result? A test run, a build, or a diff that
   applies catches a failure at no cost in judgment. A task whose result
   is a conclusion nobody downstream checks stays on Claude, where Opus 5
   holds the better accuracy record (63.0 against Sol's 58.9 on the
   Intelligence Index, 79.2 against 64.6 on SWE-Bench Pro).

Two yeses send the task to the Codex rung that mirrors the Claude rung it
would have taken. A failure escalates inside the host that ran the task,
so the escalated brief keeps the same tools and the same failure output.

The Codex side spends ChatGPT plan allowance, which also feeds the user's
own Codex sessions, and Codex exposes no command that reports how much
is left. When the allowance runs out, the call fails and the task goes to
the Claude rung with the same brief.

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

Rung for rung, the Codex side is cheaper than the Claude side on the two
lower rungs and dearer on the escalation rung:

| Rung | Claude, in / out | Codex, in / out | Codex as a share of Claude |
|---|---|---|---|
| mechanical | Sonnet 5, 2 / 10 | Luna, 0.20 / 1.20 | 10% / 12% |
| default | Opus 5, 5 / 25 | Sol, 4 / 20 | 80% / 80% |
| escalation | Opus 5, 5 / 25 | Astra, 10 / 50 | 200% / 200% |
| summoned | Fable 5.1, 10 / 50 | Astra, 10 / 50 | 100% / 100% |

The escalation rung pays double per token and gets it back in tokens.
Artificial Analysis measured Astra at max using a third of Sol's tokens
on its coding harness, and on this repo's three briefs Astra at medium
spent 29% fewer tokens than Sol at max.

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

The vendor rows put Terra one to two points under Sol. Independent runs
on long-horizon work do not:

| Source | Measured | Sol | Terra | Luna | Claude |
|---|---|---|---|---|---|
| CodeRabbit, 100+ long-horizon coding tasks, five languages | pass rate | 63.7% | 40.7% | | |
| same run | output tokens per completed task | 20,968 | 55,594 | | |
| CodeRabbit, review of production PRs | lift over their baseline | +7.4 points | -8.6 points | | |
| Arena.ai Agent Arena, crowd-judged agentic sessions | rank | top 2 | 15 | 17 | |
| Arena.ai Image-to-WebDev | Elo | 1,581 | 1,531 | 1,497 | Opus 5 at max 1,669 |
| Artificial Analysis Intelligence Index, 2026-09-04 | score | 58.9 | 55.0 | 51.2 | Fable 5.1 65.7, Opus 5 63.0, Sonnet 5 55.3, Astra 61.2 |
| Artificial Analysis | cost per index task at max | $1.04 | $0.55 | $0.21 | |
| Sonar, 4,444 Java tasks at medium | pass rate | 82.0% | 80.0% | | |
| Sonar | code smells per thousand lines | 17.6 | 23.3 | | |
| BuildFast, 700K-token retrieval | citations | all correct | missed 2 past 500K | stopped citing at 300K | |

What the rows say, one model at a time:

- Luna sits two to four points under Sol on short coding and terminal
  work, holds on short briefs with a check (six of six on this repo's
  briefs, and Arena's effort sweep puts Luna at xhigh a hair above Terra
  at medium), and collapses on long context. Its recall past 256K tokens
  is 41%. So Luna takes narrow, fully specified work with a short brief,
  and nothing that must hold a large codebase in view.
- Terra matches Sol on short tasks and loses by 23 points on long-horizon
  ones while spending 2.6 times the output tokens. At list prices that is
  about $0.67 of output per CodeRabbit task against $0.42 for Sol. So on
  the work the default rung sends, Terra is both less accurate and dearer
  per finished task, and on the short work it does well Luna costs a
  quarter as much. Terra has no rung.
- Sol is the default worker. It ties Opus 5 on Terminal-Bench 2.1 (88.8
  against 89.1) and on DeepSWE resolves a task for $8.39 against Opus 5's
  $11.84 at the same rate. Opus 5 leads it on the Intelligence Index (63.0
  against 58.9), SWE-Bench Pro (79.2 against 64.6), and Terminal-Bench
  4.0 (52.3 against 37.3), which is why the Claude escalation rung stays
  on Opus rather than moving to Sol.
- Astra leads every OpenAI benchmark it appears on and beats Fable 5.1 on
  the agentic coding and math rows, while Fable 5.1 leads on Humanity's
  Last Exam with tools. On Terminal-Bench 4.0 OpenAI estimates Astra's API
  cost per task at 9% under Sol's and 63% under Fable 5.1's, because it
  spends fewer tokens to finish. At medium it is the Codex escalation
  rung. Above medium it is the summoned rung.

## Effort

OpenAI's Codex docs say to start at a lower effort and raise it when the
work needs it: low for quick well-scoped tasks, medium as the balance,
high and xhigh for multi-step work, max for the hardest single problem
"when depth matters more than speed or usage", and ultra to split a task
across internal subagents. The docs add that "most tasks do not need Max
or Ultra". Ultra exists only inside Codex, and the API tops out at max.

Luna, Sol, and summoned Astra run at xhigh, for two reasons. A delegated
call is one shot with no conversation to correct it, so the effort that
avoids a retry is the cheap one. And the Codex catalog itself sets the
effort for its own multi-agent workers to xhigh on Astra.

The escalation rung runs Astra at medium, not Sol at max. Artificial
Analysis measured Astra's whole effort range at four index points, 57 at
low to 61 at max, with the step from xhigh to max adding nothing and
costing 40% more. Sol's curve is as flat. At medium it beats Fable 5 on
Agents' Last Exam at a quarter of the cost. So Sol at max is the model
that just failed, thinking longer, for 30% more.

Astra at medium is a different model. Its lead over Sol on the agentic
rows (20 points on Terminal-Bench 4.0, 41 points lower hallucination
rate) is five times its own effort spread. That leaves xhigh, where
Astra's published scores live, for the user to summon when a medium
escalation also fails.

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

The same three briefs then ran on Luna, Sol, Sol at max, and Astra at
medium through Codex, and on Opus 5 through the plugin's `opus-medium`
and `opus-xhigh` agents. All twenty-four runs passed. Token totals are what each host billed for the three runs, so
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
| Sol, max | 126,622 | 235 | $0.91 |
| Astra, medium | 89,632 | 112 | $1.61 |
| Opus 5, medium | 128,054 | 71 | $1.15 |
| Opus 5, xhigh | 137,221 | 108 | $1.23 |

Every model finished every brief, so these briefs cannot rank the models
on accuracy. They rank them on cost and speed for work all of them can
do: Luna costs 3% of Opus at medium, Terra at xhigh costs 29%, Sol costs
60%, and Opus finishes fastest. The Codex costs land on the ChatGPT plan allowance,
not the API bill. Ranking on the hard tenth of tasks still rests on the
published scores above, where Opus 5 leads Sol by 15 points on
Terminal-Bench 4.0.

The orchestrator never sets max or ultra. Ultra spawns subagents inside
the call, which multiplies the allowance one call spends. Only Pro and
Business Premium plans draw Astra from the full Codex allowance. Plus
holds a limited Astra allowance, so on Plus an escalation can hit that
cap before the 5-hour limit does.

## Why the ladder changed on 2026-09-04

Before this review the Codex side ran Luna at xhigh as the default worker
and Luna at medium for mechanical work, with Terra as the escalation and
Sol as the summoned rung. The review first moved to Luna, Terra, Sol,
Astra, and then, on the independent runs above, to Luna, Sol, Astra at
medium, Astra at xhigh. The facts that moved it:

- OpenAI's Codex docs position Luna for "clear, repeatable tasks", and
  the long-context row above shows why it stays on the mechanical rung.
- CodeRabbit's long-horizon run and the Arena agentic sessions put Terra
  far under Sol on exactly the default rung's work, and dearer per
  finished task. Two Codex users report Terra draining a 5-hour limit in
  minutes and a weekly Plus allowance in six hours while forgetting
  instructions. Terra leaves the ladder.
- The Codex catalog marks Luna `multi_agent_version` v1 while Sol and
  Astra are v2, so a Sol orchestrator in the Codex CLI refuses a spawn
  that names Luna by model. Sol as the default spawn avoids the question.
- Astra shipped at Fable's price and above Fable on the agentic rows. Its
  effort curve is flat enough that medium already carries most of its
  lead over Sol, so medium is the escalation the orchestrator may pick
  and xhigh is what the user summons.

## Open questions

- No effort curve is published for any GPT-5.6 model or for Astra. The
  Claude side runs Opus at medium because Anthropic published that curve.
  The three-brief Terra measurement above is one run per cell. A repeat on
  ten briefs with three runs each would give a curve worth acting on.
- Sol's price reverts on or after 2026-11-21 unless OpenAI extends it. At
  5 / 30 Sol still sits under Opus.
- Astra at medium has no published score on the agentic rows. The case
  for it rests on Astra's four-point effort spread against its 20-point
  lead at max. Ten hard briefs that Sol at xhigh fails, rerun on Astra at
  medium and at xhigh, would show whether medium keeps that lead.
- The Codex CLI's own subagent tool (openai/codex issue 31814) still
  drops the model field under a Sol orchestrator, so the `luna-xhigh`
  agent file there needs `hide_spawn_agent_metadata = false` under
  `[features.multi_agent_v2]` in `~/.codex/config.toml`.

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
- CodeRabbit run, https://www.coderabbit.ai/blog/gpt-5-6-sol-and-terra-benchmark
- Sonar run, https://www.sonarsource.com/blog/openai-gpt-5-6-sol-and-terra/
- Arena.ai agent and WebDev ranks, https://x.com/arena/status/2081848778324320354
  and https://x.com/arena/status/2083596490539511856
- Artificial Analysis index snapshot, https://benchlm.ai/benchmarks/artificialanalysis
- Artificial Analysis on Astra, https://artificialanalysis.ai/articles/benchmarking-gpt-6-astra
- BuildFast hands-on, https://www.buildfastwithai.com/blogs/gpt-5-6-sol-terra-luna-review-2026
- Codex quota reports, https://github.com/openai/codex/issues/32606 and
  https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726
- Codex subagent model field, https://github.com/openai/codex/issues/31814
- Opus 5 against Sol, https://www.datacamp.com/blog/claude-opus-5-vs-gpt-5-6-sol
