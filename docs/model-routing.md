# Model routing across Claude and Codex

Which model takes which kind of delegated work, on both hosts, and the
prices and published scores behind each choice. The rules themselves live
in two places: the output style's Subagents section for the Claude ladder,
and the `codex-delegate` skill's table for the Codex ladder. This file
holds the numbers and the reasons, so those rules can stay short.

The `model-routing-review` skill rebuilds this file when either vendor
ships a model or moves a price. Every number carries its date and source
so the next review can tell what moved.

Last reviewed 2026-10-08 against Codex CLI 0.156.0. Anthropic shipped
Haiku 5.5 on 2026-10-07, and it took the Claude mechanical rung from
Sonnet 5.5. OpenAI shipped GPT-6.1 Sol on 2026-09-29, but this machine's
Codex CLI cannot name it yet, so this review did not score it and the
Codex side did not move. The review before ran on 2026-09-22, when Opus
5.5, GPT-6 Sol, and GPT-6 Luna moved the ladder, and Sonnet 5.5 replaced
Sonnet 5 on the mechanical rung on 2026-09-28.

## The two ladders

Each Claude rung has one Codex rung that takes the same kind of work. A
name states its model and effort, so the orchestrator sees the cost of a
dispatch in the name it types.

| Rung | Claude agent | Codex agent | Takes |
|---|---|---|---|
| mechanical | `haiku-medium` | `luna-xhigh` | An edit or a run whose brief names the exact change and a command that checks it. Parallel copies of one such task. Fetching a named doc page. On Claude, never a task that must hold more than 100K tokens in view |
| default | `opus-medium` | `sol-xhigh` | Any task that reads code to reach a conclusion (an investigation, a diagnosis, a review, a design choice). On Codex, also any brief that must read past 272K tokens |
| escalation | `opus-xhigh` | `astra-medium` | A task that failed once below it. One long dependent chain the orchestrator cannot split |
| summoned | `fable-xhigh` | `astra-xhigh` | Only when the user's own message names the model, in any form. On Codex, any Astra call above medium effort |

On Claude Code, a Codex rung is not a Claude agent. It is a `codex exec`
command with the rung's model and effort, run in the background through
the Bash tool, and the `codex-delegate` skill writes that command. In the
Codex CLI, the same four rungs are agent files under `~/.codex/agents`
that `setup.sh` writes.

## Which host takes a task

Codex on a machine set up per `docs/codex-parity.md` has the same tools,
MCP servers, and skills as the Claude Code session. The one thing a
delegated Codex call lacks is the conversation. So when the setup file
says Codex is on, two questions pick the host:

1. Does the brief stand alone from the conversation? A brief that leans
   on what was said in the session stays on Claude.
2. Does a command check the result? A test run, a build, or a diff that
   applies catches a failure at no cost in judgment. A task whose result
   is a conclusion nobody downstream checks stays on Claude, where Opus
   holds the better accuracy record. Artificial Analysis's Intelligence
   Index on 2026-09-22 put Opus 5.5 at 58 against GPT-6 Sol's 48, and
   the older rows put Opus 5 at 79.2 against GPT-5.6 Sol's 64.6 on
   SWE-Bench Pro.

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
(input, cache hit, output): GPT-6 Astra 250, 25, 1,250. GPT-6 Sol 50, 5,
250. GPT-6 Luna 2.5, 0.25, 12.5. Each rate is 25 times the model's API
price, so the API price is the plan burn rate too. The GPT-5.6 rates are
Sol 100, 10, 500, Terra 50, 5, 300, and Luna 5, 0.5, 30.

| Model | Input | Cache hit | Output | Long context (OpenAI past 272K input, Haiku 5.5 past 100K) | Source date |
|---|---|---|---|---|---|
| GPT-6 Luna | 0.10 | 0.01 | 0.50 | 0.20 / 0.02 / 0.75 | launched 2026-09-22, checked 2026-10-08 |
| GPT-6 Sol | 2 | 0.20 | 10 | 4 / 0.40 / 15 | launched 2026-09-22, checked 2026-10-08 |
| GPT-6.1 Sol | 2 | 0.10 | 10 | 4 / 0.20 / 15 | launched 2026-09-29, checked 2026-10-08, not on the ladder |
| GPT-5.6 Luna | 0.20 | 0.02 | 1.20 | 0.40 / 0.04 / 1.80 | 2026-07-30 cut, checked 2026-09-22, off the ladder since 2026-09-22 |
| GPT-5.6 Terra | 2 | 0.20 | 12 | 4 / 0.40 / 18 | 2026-07-30 cut, checked 2026-09-04 |
| GPT-5.6 Sol | 4 | 0.40 | 20 | 8 / 0.80 / 30 | 2026-08-21 cut, promised through 2026-11-21, off the ladder since 2026-09-22 |
| GPT-6 Astra | 10 | 1 | 50 | 20 / 2 / 75 | 2026-08 launch, checked 2026-10-08 |
| Claude Haiku 5.5 | 0.10 | 0.01 | 0.50 | 0.50 / 0.05 / 2.50 | launched 2026-10-07, checked 2026-10-08 |
| Claude Sonnet 5.5 | 2 | 0.10 | 10 | n/a | cache hit cut from 0.20 on 2026-10-07, checked 2026-10-08, off the ladder since 2026-10-08 |
| Claude Sonnet 5 | 2 | 0.20 | 10 | n/a | checked 2026-09-01, off the ladder since 2026-09-28 |
| Claude Opus 5.5 | 4 | 0.20 | 20 | n/a | launched 2026-09-22, checked 2026-10-08 |
| Claude Opus 5 | 5 | 0.50 | 25 | n/a | checked 2026-09-01, off the ladder since 2026-09-22 |
| Claude Fable 5.1 | 10 | 0.25 | 50 | n/a | checked 2026-10-08 |

The OpenAI long-context row applies to the whole request once its input
passes 272K tokens. Input and cache double, and output goes up by half.
Haiku 5.5's higher row applies the same way once a prompt passes 100K
tokens, and it costs five times the lower row on every price.
Every GPT-6 and GPT-5.6 model lists a 1,050,000-token window and a
128,000-token output cap on the API. The GPT-6 model pages add a
cache-write price of 1.25 times input, and Codex does not charge it. The
Codex CLI catalog reports a 272,000-token working window and an
872,000-token maximum for the same models.

Rung for rung, the Codex side costs the same as the Claude side on the
mechanical rung, half as much on the default rung, and more on the
escalation rung.

| Rung | Claude, in / out | Codex, in / out | Codex as a share of Claude |
|---|---|---|---|
| mechanical | Haiku 5.5, 0.10 / 0.50 | GPT-6 Luna, 0.10 / 0.50 | 100% / 100% |
| default | Opus 5.5, 4 / 20 | GPT-6 Sol, 2 / 10 | 50% / 50% |
| escalation | Opus 5.5, 4 / 20 | Astra, 10 / 50 | 250% / 250% |
| summoned | Fable 5.1, 10 / 50 | Astra, 10 / 50 | 100% / 100% |

The mechanical row's prices apply only while the prompt stays under 100K
tokens.
Past that, Haiku 5.5 bills its higher row and Luna stays at its base price
until 272K, so Luna costs a fifth of Haiku there. The Claude rung takes no
such brief.

GPT-6 Sol costs half what Opus 5.5 costs on the default rung, at its
list price with no promotion behind it. The two questions above still
pick the host. Price only makes Codex the cheaper place for a task that
passes both.

Astra pays two and a half times Opus 5.5's price per token and five
times GPT-6 Sol's, and it gets some of that back in tokens. Artificial
Analysis measured Astra at max using a third of GPT-5.6 Sol's tokens on
its coding harness, and on this repo's three briefs Astra at medium spent
29% fewer tokens than GPT-5.6 Sol at max.

Astra's cache hit costs 1.00 against Fable's 0.25 and Opus 5.5's 0.20,
so a long many-turn Astra session pays four times Fable's rate and five
times Opus 5.5's on the tokens it resends. Per-token price is an input
to the ranking, not the ranking. The ranking is cost per finished task,
which counts the retry a cheap failure causes and the orchestrator
tokens spent writing the brief again.

## Published scores

All OpenAI numbers ran at the model's maximum effort unless noted. Scores
compare safely only when the benchmark, the harness, and the effort match,
and the vendor tables mix all three, so treat a gap under three points as
noise. Every Claude row in the first two tables is from before
2026-09-22. No independent Opus 5.5 score had been published on that date,
so the Opus 5 rows stay as the Claude side's record, and Anthropic's own
Opus 5.5 claims sit in the "Why the ladder changed on 2026-09-22, Opus
5.5" section. Haiku 5.5 has its own table below, from 2026-10-07.

The first two tables hold the rows from the 2026-09-04 review, where
Luna, Terra, and Sol are the GPT-5.6 models. OpenAI published none of
those rows for GPT-6 Sol or Luna, so their rows sit in a third table.

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

OpenAI's launch post for GPT-6 Sol and Luna reports a different set of
benchmarks and plots each one at five efforts. It has no Terminal-Bench,
SWE-Bench Pro, BrowseComp, long-context recall, or security row.
Artificial Analysis rescaled its indexes between the two reviews, so its
2026-09-22 numbers compare only with each other. It now puts GPT-5.6 Sol
at 47 on the Intelligence Index, where the 2026-09-04 snapshot said 58.9.

| Benchmark | GPT-6 Luna | GPT-6 Sol | Other models, same source | Source |
|---|---|---|---|---|
| AA Coding Agent Index, max | 41 | 57 | GPT-5.6 Luna 43, GPT-5.6 Sol 55 | Artificial Analysis |
| AA Intelligence Index, max | 37 | 48 | GPT-5.6 Luna 37, GPT-5.6 Sol 47, Astra 53, Opus 5.5 58 | Artificial Analysis |
| AA cost per Intelligence Index task, max | $0.07 | $1.06 | GPT-5.6 Luna $0.18, GPT-5.6 Sol $1.99 | Artificial Analysis |
| AA-Omniscience hallucination rate, max, lower is better | 77 | 60 | GPT-5.6 Luna 93, GPT-5.6 Sol 92 | Artificial Analysis |
| OSWorld 2.0 | 52.7 at max | 60.5 at xhigh, 64.4 at max | Astra 72.6 from its own launch | OpenAI |
| DeepSWE v1.1 | 66.6 at max | 66.6 at xhigh, 68.8 at max | Astra 74.1 and GPT-5.6 Sol 72.7 from Astra's launch, Fable 5 69.9 | OpenAI |
| Agents' Last Exam V1, max | 50.9 | 56.4 | | OpenAI |
| FrontierCode 1.1, max | 42.4 | 49.3 | Fable 5.1 50.3, Opus 5 53.4 at medium | OpenAI |
| AutomationBench 1.0.6 | 5.4 points over GPT-5.6 Luna, at high | 33.2 at xhigh | Astra 30.3 at low, Opus 5 26.9 at max | OpenAI |

OpenAI's launch post returns 403 to a fetch. Codex read it with web
search, and its coding rows match The Decoder, Kingy, and HandyAI.

Anthropic's Haiku 5.5 system card runs every Haiku row at max effort
unless a row says otherwise. The medium rows come from the effort charts
in Anthropic's launch post. Artificial Analysis ran Haiku 5.5 the day it
shipped, and its rows are the only independent ones so far.

| Benchmark | Haiku 5.5 | Sonnet 5.5 | Other models, same source | Source |
|---|---|---|---|---|
| SWE-Bench Pro, max | 64.8 | 81.3 | | Anthropic system card |
| Terminal-Bench 4.0, max | 39.2 | 70.6 | Opus 5.5 66.4 at xhigh, GPT-6 Luna 16.4 | Anthropic system card and launch post |
| Terminal-Bench 4.0, medium | 20.3, $0.68 per task | 28.8, $0.68 per task | | Anthropic launch post |
| OSWorld 2.1, max | 72.4 | 83.9 | GPT-6 Luna 48.9 | Anthropic launch post |
| OSWorld 2.1, medium | 53.3, $0.13 per task | 66.0, $0.93 per task | GPT-6 Luna 37.5, $0.13 per task | Anthropic launch post |
| ProgramBench, long-context coding | 82.0 | 79.7 | Opus 5.5 91.2 | Anthropic system card |
| Long-context recall past 256K tokens | not published | not published | | |
| ExploitBench, share of flags captured, plain arm | 38% | | | Anthropic system card, the authors' harness, not comparable with the ExploitBench row above |
| AA Intelligence Index, max | 43 | 56 | GPT-6 Luna 38 | Artificial Analysis, 2026-10-07 |
| AA Intelligence Index, high | 38 | | | Artificial Analysis |
| AA Terminal-Bench 4.0, max | 33 | | GPT-6 Luna 13 | Artificial Analysis |
| AA-Omniscience hallucination rate, max, lower is better | 40 | | GPT-6 Luna 77 | Artificial Analysis |
| AA cost per Intelligence Index task, max | $0.21 | | GPT-6 Luna $0.07 | Artificial Analysis |

Artificial Analysis has published no Coding Agent Index or long-context
row for Haiku 5.5. Its Haiku run spent about 162K output tokens per index
task at max and about 55K at high, against about 50K for GPT-6 Luna at
max.

What the rows say, one model at a time:

- Haiku 5.5 takes the Claude mechanical rung. Every published row puts it
  under Sonnet 5.5, by 8.5 to 12.7 points at medium and by 13 on the
  Intelligence Index at max. On Terminal-Bench 4.0 at medium the two cost
  the same per task, because long tasks push Haiku's prompts past its
  100K-token price line. The rung takes neither long nor unchecked work,
  and on this repo's briefs Haiku tied Sonnet at 8% of the cost, as the
  2026-10-08 section below shows. It scores above GPT-6 Luna on every
  benchmark both appear in, and costs three times as much as Luna per
  index task at max.

- GPT-6 Luna takes the mechanical rung. It scores within two points of
  GPT-5.6 Luna on both Artificial Analysis indexes at 39% of the cost
  per task, and its hallucination rate fell from 93 to 77. OpenAI
  published no long-context recall for it, so the rung keeps its
  272K-token brief cap from GPT-5.6 Luna's record below.
- GPT-6 Sol takes the default rung. It leads GPT-5.6 Sol by 2 points on
  the Coding Agent Index at 53% of the cost per task, and its
  hallucination rate fell from 92 to 60. It trails Opus 5.5 by 10 points
  on the Intelligence Index, so a task whose conclusion nobody checks
  still stays on Claude.
- GPT-5.6 Luna sits two to four points under Sol on short coding and
  terminal work, holds on short briefs with a check (six of six on this
  repo's briefs, and Arena's effort sweep puts Luna at xhigh a hair
  above Terra at medium), and collapses on long context. Its recall past
  256K tokens is 41%. So Luna takes narrow, fully specified work with a
  short brief, and nothing that must hold a large codebase in view.
- Terra matches Sol on short tasks and loses by 23 points on
  long-horizon ones while spending 2.6 times the output tokens. At list
  prices that is about $0.67 of output per CodeRabbit task against $0.42
  for Sol. So on the work the default rung sends, Terra is both less
  accurate and dearer per finished task, and on the short work it does
  well Luna costs a quarter as much. Terra has no rung.
- GPT-5.6 Sol was the default worker until 2026-09-22. It tied Opus 5 on
  Terminal-Bench 2.1 (88.8 against 89.1) and on DeepSWE resolves a task
  for $8.39 against Opus 5's $11.84 at the same rate. Opus 5 leads it on
  the Intelligence Index (63.0 against 58.9), SWE-Bench Pro (79.2
  against 64.6), and Terminal-Bench 4.0 (52.3 against 37.3), which is
  why the Claude escalation rung stays on Opus rather than moving to
  Sol. Opus 5.5 succeeds Opus 5 on both Claude rungs at Sol's price, so
  that record now costs no premium.
- Astra leads every OpenAI benchmark it appears on and beats Fable 5.1
  on the agentic coding and math rows, while Fable 5.1 leads on
  Humanity's Last Exam with tools. On Terminal-Bench 4.0 OpenAI
  estimates Astra's API cost per task at 9% under GPT-5.6 Sol's and 63%
  under Fable 5.1's, because it spends fewer tokens to finish. At medium
  it is the Codex escalation rung. Above medium it is the summoned rung.

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

OpenAI's launch post for GPT-6 Sol and Luna plots score against cost per
task at each effort. Rule 5 of the review lowers an effort only when the
lower level costs at most half for at most two points less, and no step
on either curve passes it.

| Model, benchmark | high | xhigh | max |
|---|---|---|---|
| GPT-6 Sol, DeepSWE | 65.3, $0.64 | 66.6, $1.00 | 68.8, $2.74 |
| GPT-6 Sol, OSWorld 2.0 | 58.3, $1.64 | 60.5, $2.21 | 64.4, $3.25 |
| GPT-6 Luna, DeepSWE | 59.3, $0.084 | 61.3, $0.11 | 66.6, $0.22 |
| GPT-6 Luna, OSWorld 2.0 | 41.4 | 46.7 | 52.7 |

Sol at high costs 64% of xhigh for 1.3 points less on DeepSWE, which
misses the half-cost bar. Luna at high loses 2 to 5 points. Both stay at
xhigh.

Anthropic's Haiku 5.5 launch post plots score and cost per task at all
five efforts. Haiku 5.5 starts at `medium`, the effort Sonnet 5.5 ran at
on this rung.

| Haiku 5.5, benchmark | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| Terminal-Bench 4.0 | 12.7, $0.42 | 20.3, $0.68 | 24.8, $1.04 | 31.5, $1.75 | 39.2, $2.64 |
| OSWorld 2.1 | 42.0, $0.07 | 53.3, $0.13 | 61.3, $0.18 | 67.6, $0.28 | 72.4, $0.61 |
| Humanity's Last Exam, no tools | 30.9, $0.003 | 35.5, $0.007 | 39.7, $0.02 | 44.1, $0.06 | 45.9, $0.21 |

Low costs 62%, 54%, and 43% of medium on the three rows for 7.6, 11.3,
and 4.6 points less, so no row passes rule 5. High gains 4 to 8 points for
38% to 186% more cost per task. On this repo's briefs high passed the same
checks as medium and took 47% longer, so the rung stays at medium and a
failure climbs to Opus rather than to a higher Haiku effort.

The escalation rung runs Astra at medium, not Sol at max. Artificial
Analysis measured Astra's whole effort range at four index points, 57 at
low to 61 at max, with the step from xhigh to max adding nothing and
costing 40% more. GPT-6 Sol's curve is flat at the top too. Max adds 2.2
points over xhigh on DeepSWE and costs 2.7 times as much. So Sol at max
is the model that just failed, thinking longer, for 2.7 times the cost.

Astra at medium is a different model. Its lead over GPT-6 Sol is smaller
than its lead over GPT-5.6 Sol was, which was 20 points on
Terminal-Bench 4.0. OSWorld 2.0 puts it 8 points ahead (72.6 against
64.4, both at max), and the Intelligence Index 5 points ahead. Both gaps
pass the review's three-point bar, so the escalation stays a model step.
That leaves xhigh, where Astra's published scores live, for the user to
summon when a medium escalation also fails.

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

The same three briefs then ran on GPT-5.6 Luna, GPT-5.6 Sol, GPT-5.6 Sol
at max, and Astra at medium through Codex, and on Opus 5 through the
plugin's `opus-medium` and `opus-xhigh` agents, which pinned Opus 5
until 2026-09-22. All twenty-four runs passed. Token totals are what
each host billed for the three runs, so the Codex figures include
Codex's own system prompt and the Opus figures include Claude Code's
plus the writing rules the spawn hook appends. The API-equivalent cost
takes 80% of tokens at the input price and 20% at the output price.

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
do: Luna costs 3% of Opus 5 at medium, Terra at xhigh costs 29%, Sol costs
60%, and Opus finishes fastest.

At Opus 5.5's prices the same token counts
would cost $0.92 at medium and $0.98 at xhigh, so Sol's share rises to
75%, and Anthropic reports Opus 5.5 finishing agentic coding tasks in
about half the tokens, which would cut those figures again. The Codex
costs land on the ChatGPT plan allowance, not the API bill. Ranking on the
hard tenth of tasks still rests on the published scores above, where Opus
5 leads GPT-5.6 Sol by 15 points on Terminal-Bench 4.0.

The orchestrator never sets max or ultra. Ultra spawns subagents inside
the call, which multiplies the allowance one call spends. Only Pro and
Business Premium plans draw Astra from the full Codex allowance. Plus
holds a limited Astra allowance, so on Plus an escalation can hit that
cap before the 5-hour limit does.

## Why the ladder changed on 2026-10-08, Haiku 5.5

Anthropic shipped Haiku 5.5 (`claude-haiku-5-5`) on 2026-10-07. On
2026-10-08 it took the Claude mechanical rung from Sonnet 5.5 at the same
effort, `medium`, and the agent became `haiku-medium`. Sonnet 5.5 has no
retirement date, so rule 1 of the review does not decide it. Rule 3 does,
on this repo's own briefs. The facts:

- Price. Below 100K tokens of prompt, Haiku 5.5 lists at 0.10 / 0.01 /
  0.50 (input, cache hit, output), which is 5%, 10%, and 5% of Sonnet
  5.5's 2 / 0.10 / 10. Past 100K the whole request pays 0.50 / 0.05 /
  2.50, which is 25%, 50%, and 25%. Rule 4 sets the brief cap at that
  line, so `haiku-medium` takes no task that must hold more than 100K
  tokens in view.
- The trial. On 2026-10-07 five briefs ran twice each on three arms, in
  scratch worktrees of this repo, as headless Claude Code sessions with
  the old `sonnet-medium` prompt. The briefs were a test file for `strip()`
  in `strip-attribution.py`, checked by a mutation the tests had to catch,
  a one-line bug planted in `route-codex.py` with the failing test named,
  a rename of `read_mention` and `write_mention` across three hook files,
  the Claude pricing page fetched into a table, and four questions about
  the hooks answered with file and line references. A separate check
  scored every run.

| Arm | Briefs 1 to 4 passed | Hook questions right | Cost | Seconds |
|---|---|---|---|---|
| Sonnet 5.5, medium | 8 of 8 | 8 of 8 | $1.31 | 199 |
| Haiku 5.5, medium | 8 of 8 | 8 of 8 | $0.10 | 202 |
| Haiku 5.5, high | 8 of 8 | 8 of 8 | $0.12 | 297 |

- What the trial shows. Haiku tied Sonnet on every check at 8% of the
  cost, or 13% counting only the runs where Sonnet's prompt cache was
  already warm. It took two to three times Sonnet's turns and tokens, so
  its faster output bought no wall time. That passes rule 3, which asks
  for half the cost within three points.
- Reports. Haiku's report misstated the work in 4 of its 20 runs, though
  the work itself passed. One report left out the test result the brief
  asked for, and three miscounted or invented edits in the rename. In 3
  runs Haiku ran the writing-voice passes on a Python test file. Sonnet's
  10 reports had no errors, and no run in any arm claimed a check passed
  that had failed. The `haiku-medium` prompt now includes the verification
  paragraph from Anthropic's Haiku 5.5 prompting guide, asks for the
  check's last lines and `git diff --stat` in the report, and tells the
  agent the writing-voice passes skip code.
- Published scores. Every published row puts Haiku 5.5 under Sonnet 5.5,
  as the score table above shows. Anthropic's launch post says the same,
  "Sonnet 5.5 and Opus 5.5 remain better choices for complex agentic
  coding tasks like those measured by Terminal-Bench 4.0". The trial
  briefs all passed on every arm, as the 2026-09-04 briefs did, so they
  cannot rank accuracy. The published rows measure long, open-ended work,
  which the rung never takes.
- Cost per finished task. The rung takes only work a command checks, so
  a Haiku failure costs one `opus-xhigh` retry, about $0.33 at Opus 5.5
  prices from the 2026-09-04 token counts. Haiku saves about $0.06 a
  brief against Sonnet with a warm cache. It stays cheaper per finished
  task unless about one brief in five fails on Haiku that would have
  passed on Sonnet.
- Claude Code. Version 2.1.293 is the first to run Haiku 5.5. It resolves
  the `haiku` alias to Haiku 5.5 on the Anthropic API only, and Bedrock,
  Google Cloud, and Claude Platform on AWS still resolve it to Haiku 4.5.
  The agent pins `claude-haiku-5-5`.
- Refusals. The Haiku 5.5 system card says it "over-refused more than any
  other model we tested", and Haiku 5.5 has no server-side fallback. A
  refusal reaches the orchestrator as an agent that could not finish,
  which escalates to `opus-xhigh` like any other failure.

Each cell of the ladder, with its reason on 2026-10-08:

| Rung | Host | Model, effort | Reason |
|---|---|---|---|
| mechanical | Claude | Haiku 5.5, medium | It tied Sonnet 5.5 on every check of this repo's briefs at 8% of the cost, which passes rule 3, and its brief cap sits at its 100K-token price line |
| mechanical | Codex | GPT-6 Luna, xhigh | No new Luna shipped and its price did not move |
| default | Claude | Opus 5.5, medium | No new Opus shipped and its price did not move |
| default | Codex | GPT-6 Sol, xhigh | GPT-6.1 Sol shipped on 2026-09-29 at the same list price, but Codex CLI 0.156.0 cannot name it and this review gathered no score for it, so rule 3 has nothing to compare |
| escalation | Claude | Opus 5.5, xhigh | No new Opus shipped and its price did not move |
| escalation | Codex | GPT-6 Astra, medium | No new Astra shipped and its price did not move |
| summoned | Claude | Fable 5.1, xhigh | Fable 5.1 is still Anthropic's most capable model at its highest list price, so rule 2 keeps it |
| summoned | Codex | GPT-6 Astra, xhigh | Astra is still OpenAI's most capable model at its highest list price, so rule 2 keeps it |

## Why the ladder changed on 2026-09-22, GPT-6 Sol and Luna

OpenAI shipped GPT-6 Sol (`gpt-6-sol`) and GPT-6 Luna (`gpt-6-luna`) on
2026-09-22. They took the default and mechanical Codex rungs at the same
efforts. GPT-5.6 Sol and Luna have no retirement date, so rule 1 of the
review does not decide it. Rule 3 does, since each new model costs half
what its predecessor costs and scores within three points of it on the
independent index. The facts:

- Price. GPT-6 Sol lists at 2 / 0.20 / 10 (input, cache hit, output)
  against GPT-5.6 Sol's promotional 4 / 0.40 / 20. GPT-6 Luna lists at
  0.10 / 0.01 / 0.50 against 0.20 / 0.02 / 1.20. On the Codex rate card
  each spends half the allowance its predecessor spent.
- Scores. On Artificial Analysis's Coding Agent Index, GPT-6 Sol leads
  GPT-5.6 Sol by 2 points at 53% of the cost per task, and GPT-6 Luna
  trails GPT-5.6 Luna by 2 points at 39%. Both hallucinate less, 60
  against 92 for Sol and 77 against 93 for Luna. OpenAI's DeepSWE row
  puts GPT-6 Sol 3.9 points under the GPT-5.6 Sol figure from Astra's
  launch a month earlier. This review weighs the independent index over
  that comparison across two vendor posts, as the 2026-09-04 review did
  for Terra.
- Spawning. The Codex catalog marks GPT-6 Luna `multi_agent_version` v2,
  where GPT-5.6 Luna was v1. A Sol orchestrator in the Codex CLI can now
  spawn Luna by model name.
- CLI version. Codex CLI 0.155.0 is the first to list the two models.
  Version 0.153.3 answers either name with "The 'gpt-6-sol' model is not
  supported when using Codex with a ChatGPT account." The orchestrator
  line `setup.sh` writes names `gpt-6-sol`, so `setup.sh` now warns when
  the CLI is older.
- Astra stays on both upper rungs. GPT-6 Sol at max trails it by 8
  points on OSWorld 2.0, and rule 3 needs a replacement within three
  points at half the price. Astra now costs five times Sol per token, up
  from two and a half.
- Terra has no GPT-6 version and stays off the ladder.

The Claude side did not move in this change.

## Why the ladder changed on 2026-09-22, Opus 5.5

Anthropic shipped Opus 5.5 (`claude-opus-5-5`) on 2026-09-22 as the
successor to Opus 5, and it took both Claude rungs Opus 5 held, at the
same efforts. Rule 1 of the review decides it, because the vendor's named
successor takes the rung. Rule 3 agrees on its own, since the price fell
and the vendor's numbers rose. The facts:

- Price. Opus 5.5 lists at 4 / 0.20 / 20 (input, cache hit, output)
  against Opus 5's 5 / 0.50 / 25, so 20% less on input and output and 60%
  less on cache hits. Fast mode is 8 / 40. Batch is 2 / 10.
- Effort. The API default is `medium` where Opus 5 defaulted to `high`,
  and the plugin's agents set the effort explicitly, so the change
  reaches neither rung. Anthropic's testing has Opus 5.5 at `medium`
  matching or beating Opus 5 at `high` on multistep coding in a real
  codebase, in fewer steps and with about half the tokens, and `low`
  close behind on several coding evaluations. At a given effort it thinks
  more per turn than Opus 5, most of all at `xhigh` and `max`, so
  `opus-xhigh` turns run longer.
- Behavior. Thinking cannot be turned off, forced tool choice returns an
  error, thinking blocks are bound to the model and the conversation, and
  computer use runs only through the 2026-08-01 toolset. Claude Code
  keeps the conversation prefix intact, so none of those reach a spawned
  agent. The agent files pin `claude-opus-5-5` by id rather than the
  `opus` alias, so a machine on an older Claude Code build that still
  resolves the alias to Opus 5 runs the same model as every other.
- Scores. No independent Opus 5.5 row was published on 2026-09-22. The
  claims above are Anthropic's migration guide's, run in its own harness.

The OpenAI side moved the same day, in the section above.

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

- GPT-6.1 Sol shipped on 2026-09-29 at GPT-6 Sol's list price with half
  its cache price, and Codex's changelog calls it "near-Astra". Codex CLI
  0.161.0, released 2026-10-07, makes it the default model. This machine
  runs 0.156.0, which cannot name it. A review on 0.161.0 or later should
  score it against GPT-6 Sol on the default rung, and against Astra at
  medium on the escalation rung, where rule 3 would take it at a fifth
  of the price if it scores within three points of Astra.
- The Haiku 5.5 trial ran two runs per brief on briefs every arm passed,
  so it cannot rank accuracy. Ten harder mechanical briefs, three runs
  each on `haiku-medium` and on Sonnet 5.5 at medium, would show whether
  the published gap reaches this rung's work.
- Haiku 5.5 misstated its own work in 4 of 20 trial reports. The
  `haiku-medium` prompt now asks for the check's output and `git diff
  --stat`. A rerun of the rename brief would show whether that stops it.
- Nobody has published Haiku 5.5's recall past 256K tokens. The
  100K-token cap keeps the rung well under that, but the cap rests on
  price, not on a recall measurement.
- The Codex catalog lists a hidden slug, `gpt-reserve`. Community reports
  describe it as a model with its own weekly quota that lets Plus and Pro
  accounts keep working after their regular Codex allowance runs out. In
  September it ran GPT-5.6 Luna. OpenAI publishes no price for it, and it
  is not a rung candidate.
- Opus 5.5 has no independent score on any row of the table above and no
  point-by-point effort curve. Anthropic's claim that `medium` beats
  Opus 5 at `high` in half the tokens is the whole case for keeping
  `medium`. The three briefs above, rerun on Opus 5.5 at `medium` and at
  `xhigh`, would give the first measured token counts on this repo's
  work.
- No effort curve is published for any GPT-5.6 model or for Astra. The
  Claude side ran Opus 5 at medium because Anthropic published that
  curve, and Opus 5.5 keeps it on the vendor's word. The three-brief
  Terra measurement above is one run per cell. A repeat on ten briefs
  with three runs each would give a curve worth acting on.
- GPT-6 Sol has no Terminal-Bench, SWE-Bench Pro, or long-context recall
  row. GPT-6 Luna now has a Terminal-Bench 4.0 row (16.4 in Anthropic's
  Haiku 5.5 launch, 13 from Artificial Analysis) but still no recall
  row. The Codex mechanical rung's 272K-token cap rests on
  GPT-5.6 Luna's 41% recall past 256K tokens. The three briefs above,
  rerun on both models, would give this repo's first measured token
  counts for them.
- OpenAI's DeepSWE row puts GPT-6 Sol at 68.8 against 72.7 for GPT-5.6
  Sol, a gap past the three-point bar. The two figures come from posts a
  month apart. A rerun of GPT-5.6 Sol in the GPT-6 post's harness would
  settle whether GPT-6 Sol regressed on that benchmark.
- GPT-6 Luna at max gains 5.3 points on DeepSWE and 6 on OSWorld 2.0
  over xhigh for twice the cost, still a fifth of what Sol costs at
  xhigh. Rule 5 only lowers an effort, so Luna stays at xhigh. A run of
  mechanical briefs at max would show whether the gain reaches this
  rung's work.
- Astra at medium has no published score on the agentic rows. The case
  for it rests on Astra's four-point effort spread against its lead at
  max, which is 8 points over GPT-6 Sol on OSWorld 2.0. Ten hard briefs
  that Sol at xhigh fails, rerun on Astra at medium and at xhigh, would
  show whether medium keeps that lead.
- The Codex CLI's own subagent tool (openai/codex issue 31814) dropped
  the model field under a Sol orchestrator, so the `luna-xhigh` agent
  file there needed `hide_spawn_agent_metadata = false` under
  `[features.multi_agent_v2]` in `~/.codex/config.toml`. GPT-6 Luna runs
  on v2, and nobody has checked whether it still needs the setting.

## Sources

- OpenAI API pricing, https://developers.openai.com/api/docs/pricing
- Model pages: https://developers.openai.com/api/docs/models/gpt-6-sol,
  https://developers.openai.com/api/docs/models/gpt-6-luna,
  https://developers.openai.com/api/docs/models/gpt-6-astra,
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
- Anthropic prices, https://platform.claude.com/docs/en/about-claude/pricing,
  checked 2026-10-08
- Haiku 5.5 launch post and effort charts, https://www.anthropic.com/claude-haiku-5-5
- Haiku 5.5 system card, https://www.anthropic.com/document/claude-haiku-5-5-system-card
- Haiku 5.5 prompting guide, https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5
- Haiku 5.5 in Claude Code, https://code.claude.com/docs/en/model-config
- Artificial Analysis on Haiku 5.5, https://artificialanalysis.ai/articles/claude-haiku-5-5
- Sonnet 5.5 on Artificial Analysis, https://artificialanalysis.ai/models/claude-sonnet-5-5
- GPT-6.1 Sol release, https://learn.chatgpt.com/docs/changelog (entry of
  2026-09-29) and https://www.datacamp.com/blog/gpt-6-1-sol for its price,
  since https://openai.com/index/introducing-gpt-6-1-sol/ returns 403 to a
  plain fetch
- Codex CLI 0.161.0 default model, https://github.com/openai/codex/releases
- OpenAI retirement dates, https://developers.openai.com/api/docs/deprecations,
  checked 2026-10-08
- `gpt-reserve` reports, https://github.com/can1357/oh-my-pi/issues/10632 and
  https://github.com/steipete/CodexBar/issues/3502
- The Haiku 5.5 trial, five briefs run 2026-10-07 in this session's
  scratch worktrees, results in the 2026-10-08 section above
- Opus 5.5 prices, effort default, and the `medium` against `high`
  claims, Anthropic's Opus 5.5 migration guide as shipped in Claude
  Code's `claude-api` skill, read 2026-09-22
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
- GPT-6 Sol and Luna launch, https://openai.com/index/introducing-gpt-6-sol-and-luna/
  read through Codex's search tool (the page returns 403 to a plain
  fetch), cross-checked against
  https://the-decoder.com/openais-gpt-6-sol-and-luna-cut-prices-in-half-but-barely-move-the-needle-on-performance/,
  https://kingy.ai/blog/gpt-6-sol-luna-specs-benchmarks-pricing-comparison/
  (the effort curves), and
  https://handyai.substack.com/p/model-drop-gpt-6-sol-and-gpt-6-luna
- Artificial Analysis on GPT-6 Sol and Luna,
  https://artificialanalysis.ai/articles/gpt-6-sol-and-luna-push-the-cost-efficiency-frontier
- GPT-6 availability in Codex,
  https://community.openai.com/t/announcing-gpt-6-sol-and-gpt-6-luna-in-the-api-codex-and-chatgpt/1399925
- Codex CLI version needed for the GPT-6 names,
  https://github.com/NousResearch/hermes-agent/issues/119412, confirmed
  on this machine with 0.153.3 and 0.156.0 on 2026-09-22
