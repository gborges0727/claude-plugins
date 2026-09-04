---
name: model-routing-review
description: Re-check which model takes which rung of the delegation ladder, on Claude Code and on Codex, after a vendor ships a model or moves a price. Rebuilds docs/model-routing.md and lists every file the ladder change touches.
disable-model-invocation: true
---

# Model routing review

The delegation ladder has four rungs (mechanical, default, escalation,
summoned) and each rung names one Claude model and one OpenAI model. This
skill re-derives that table from today's catalog, prices, and published
scores, and rewrites the places that carry it. It runs by hand, when
Anthropic or OpenAI ships a model or changes a price.

The record of the last review is `docs/model-routing.md` in the
claude-plugins repo. Read it first. Every step below compares against it,
and the review is done when that file describes today and every file in
the checklist agrees with it.

## Step 1: Read the local catalog

Run the catalog script from this skill's folder:

```sh
python3 <base>/scripts/catalog.py
```

It prints one line per model the Codex CLI can name, with the slug, the
default effort, the accepted efforts, the context windows, the multi-agent
backend version, and any retirement date. Note each slug that is new since
the last review, each slug that gained a retirement date, and each model
whose accepted efforts changed. A model marked `multi_agent_version` v1
cannot be the default spawn under a v2 orchestrator in the Codex CLI.

The Claude side has no catalog command. The `claude-api` skill lists the
current Claude model ids and prices. Load it and note any new id.

The step is done when every slug in the catalog is either in the last review's table
or on your list of new ones, and the same for Claude model ids.

## Step 2: Fetch prices

Fetch these pages and record input, cache hit, output, and any
long-context surcharge, in dollars per million tokens, with today's date:

- https://developers.openai.com/api/docs/pricing
- one model page per OpenAI slug on the ladder, at
  `https://developers.openai.com/api/docs/models/<slug>`, for the context
  window, the output cap, and the accepted efforts
- the Claude prices from the `claude-api` skill

A vendor page that returns 403 to a fetch is quoted through the vendor's
developer forum post or two independent write-ups that agree. Say which in
the source list. A promotional price gets its end date in the table.

The step is done when every model on the ladder, plus every new model from step 1,
has a full price row dated today.

## Step 3: Fetch scores

For each new model, fetch the vendor's launch post and one independent
review, and record the rows for these benchmarks where they exist:
Terminal-Bench (the newest version), SWE-Bench Pro, the Artificial
Analysis Coding Agent Index, OSWorld, BrowseComp, MRCR long-context recall,
and one security row. Record the effort each number ran at. Vendor tables
run at maximum effort unless they say otherwise.

For a model already in the table, keep last review's rows unless a source
reports a rerun.

The step is done when every new model has at least a coding row and a long-context
row with a source and an effort, or the table says the row was not
published.

## Step 4: Decide rung by rung

Work down the four rungs and, for each host, keep the incumbent or name a
replacement. These rules decide it, in order:

1. A retired or retiring model leaves its rung. Its vendor's named
   successor takes the rung unless rule 3 says otherwise.
2. The summoned rung is the vendor's most capable model at its highest
   list price. The orchestrator never picks it, so its price is not a
   reason to leave it off the ladder.
3. A model replaces an incumbent on the mechanical, default, or escalation
   rung only when it beats the incumbent by three points or more on the
   rung's task class at the same or a lower price, or costs at most half
   as much within three points. Under three points is noise across
   different harnesses.
4. The mechanical rung never takes a model whose long-context recall past
   256K tokens is under 60%, and its brief cap stays at the vendor's
   surcharge line.
5. Effort stays at the value the last review set unless a published effort
   curve for the model says another level costs at most half for at most
   two points. Write the curve's numbers into the doc.

Write one sentence of reason per rung, even when nothing changed.

The step is done when all eight cells of the ladder (four rungs, two hosts) have a
model, an effort, and a dated reason.

## Step 5: Rewrite the doc

Update `docs/model-routing.md` in place: the ladder table, the price
tables and the "share of Claude" arithmetic, the score table, the effort
section, a new "Why the ladder changed on <date>" section (or a line
saying nothing moved), the open questions, and the sources. Set the "Last
reviewed" line to today and the Codex CLI version from `codex --version`.

## Step 6: Carry the change into every file that names the ladder

When any cell changed, edit each of these so they agree with the doc.
When nothing changed, confirm each still matches and say so.

| File | What it carries |
|---|---|
| `plugins/gborges-standard/output-styles/plain-english.md`, Subagents section | The Claude rung names and the Codex bullet |
| `plugins/gborges-standard/agents/*.md` | One Claude agent per rung, with its model and effort |
| `plugins/gborges-standard/skills/codex-delegate/SKILL.md`, "Pick the rung" | The Codex rung table and the context numbers |
| `plugins/gborges-standard/scripts/setup.sh` | The four `write_agent` calls, the `[agents]` default, and its `assert` |
| `tests/test_setup.py` | The `AGENTS` dict and the default-model asserts |
| `plugins/gborges-standard/hooks/route-spawns.py` | `FABLE_TYPES`, `FALLBACK_TYPE`, `DEFAULT_TYPE` for the Claude summoned, escalation, and default rungs |
| `plugins/gborges-standard/hooks/route-codex.py` | `ASTRA_MODELS` and the deny reason's fallback model for the Codex summoned rung |
| `plugins/gborges-standard/hooks/plugin_config.py` | The mention words for the summoned models |
| `README.md` | The component table rows for the agents and `codex-delegate`, and the Codex table |
| `docs/codex-parity.md` | The Codex agent table and the model slug check |
| `docs/subagent-routing.md` | The Claude ladder, its prices, and the setup-file paragraph |

Then run the suite from the repo root and paste its last three lines:

```sh
python3 -m unittest discover -s tests
```

Run the `writing-voice` passes on the doc and on every skill or README
file you edited.

The step is done when the test suite passes and a grep for each retired slug across
the repo finds only the "why the ladder changed" history in the doc.

## Step 7: Report

Reply with the ladder table as it stands now, one line per cell that
moved with its reason, the list of files edited, and the test tail. Do not
commit. The user decides whether the change ships.
