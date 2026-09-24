---
name: investigate
description: Find the cause of a hard bug or a slow path and report it without fixing it. Builds a fast check that fails on the bug first, then tests hypotheses against it. Use when the user says investigate, diagnose, or debug, or hands over a bug ticket and wants the root cause.
---

# Investigate

A method for finding the cause of a hard bug. It ends with a report in
chat, not a fix and not a comment on the ticket. Skip a phase only when you can say why.

The ask is the conversation, or the ticket the user named. An issue number
or URL means that issue, with its comments.

## Who does it

The session that loads this skill runs none of the phases. It writes a
brief, sends it to a subagent, and writes the chat report from what comes
back. The phases produce command output, probe results, and logs, and this
session needs only the report.

Send the brief to `gborges-standard:opus-medium`. When
`~/.claude/gborges-standard.json` says `"codex": true`, or the user asked
for Codex in this session, send it through the `codex-delegate` skill on
the `sol-xhigh` rung instead.

## The brief

The subagent sees none of the conversation and cannot reach the user. The
brief carries:

- the ask, in the user's words, or the issue number or URL
- everything the user said that bears on the bug: what they tried, what
  changed recently, where it happens
- the repo's path
- the path to this file, which is `SKILL.md` in the base directory printed
  when this skill loaded, with the instruction to follow it from "The
  method" to the end
- what to send back: the six items of the Phase 5 report, or, when no
  check could be built, what it tried and what it needs from the user

## When it returns

Run the report's reproducing command once and confirm it fails with the
symptom the report quotes. Run `git status` and confirm the working tree
holds only what the report says it left. Then give the user the report in
the chat reply, in the Phase 5 order.

When the subagent could not build a check, ask the user for what it needs.
Send the answer to the same subagent so it continues from where it
stopped.

The report goes in the chat reply and nowhere else. Do not post it to the
issue, the ticket, a PR, a note, or a file, and do not draft a comment for
any of those. Once the user has read it, they may ask for it to be posted
somewhere, and only then does it go there.

## The method

Everything from here down addresses the subagent that runs the
investigation.

Read `CONTEXT.md` when the repo has one, so you know the names of the parts
you are looking at, and read the decision records under `docs/adr/` for the
area.

## Redact first

This method has you show commands, outputs, and captured files. Replace
every secret with `<REDACTED>` before showing anything. Build the check
around environment variables so the credential stays in the environment
and out of what you show. A captured request carries auth headers, so
quote only the lines that matter. When the redacted output is not enough
to diagnose the bug, say so in what you send back.

## Phase 1: Build the check

This phase is the method. Everything after it is routine. A check is one
command that fails on this bug and passes once it is fixed. With one,
bisection, hypotheses, and logging all have something to run against.
Without one, reading code produces theories and no answers.

Spend more effort here than feels reasonable. Try each of these, roughly in
order, until one fails on the bug:

1. A failing test, at whatever level reaches the bug: unit, integration,
   end to end.
2. A curl or HTTP script against a running dev server.
3. A CLI run with a fixture input, diffing stdout against a known-good
   output.
4. A headless browser script (Playwright, Puppeteer) that drives the UI and
   checks the DOM, console, or network.
5. A replay. Save a real request, payload, or event log to disk and push it
   through the code on its own.
6. A throwaway harness. Start the smallest part of the system that reaches
   the bug (one service, dependencies mocked) and call the one function.
7. A random-input loop, when the output is "sometimes wrong". Run 1,000
   random inputs and look for the failure.
8. A bisection script, when the bug appeared between two known states
   (commit, dataset, version). Script "start at state X, check, repeat" so
   `git bisect run` can drive it.
9. A differential run. Push one input through the old and new version, or
   two configs, and diff the outputs.
10. A script that drives a human, as the last resort. When someone must
    click, copy `scripts/hitl-loop.template.sh` from this skill's folder,
    edit its steps, and run it. The user follows the prompts and the script
    prints what they saw for you to read.

### Make it fast and sharp

Once you have any check, improve it. Make it faster by caching setup,
skipping unrelated startup, and narrowing the test. Make it check the
exact symptom, not "did not crash". Make it give the same answer every run: pin the clock,
seed random numbers, isolate the filesystem, freeze the network. A flaky
30-second check is barely better than none. A 2-second check that always
agrees with itself is what you want.

### A bug that only sometimes happens

Aim for a higher failure rate, not a clean reproduction. Loop the trigger
100 times, run in parallel, add load, narrow the timing window, inject
sleeps. A bug that fails one run in two can be diagnosed. One in a hundred
cannot, so keep raising the rate.

### When no check can be built

Stop and send back what you have. List what you tried. Say which of these
would let you build one: access to the environment where it happens, a
redacted capture (a HAR file, a log dump, a core dump, a screen recording
with timestamps), or permission to add temporary logging in production. Do
not move on to hypotheses without a check.

### Done when

You can name one command that you have already run at least once (show the
command and its redacted output), and it:

- [ ] runs the code path the bug is in and checks the user's exact symptom,
      so it fails on this bug and passes once fixed
- [ ] gives the same answer every run (for a flaky bug, fails at a pinned,
      high rate)
- [ ] finishes in seconds
- [ ] runs without a human, except through the script in item 10

When you catch yourself reading code to form a theory before this command
exists, stop. That is the mistake this method prevents.

## Phase 2: Reproduce and shrink

Run the check and watch it fail. Confirm three things. It fails the way the
user described, not a nearby failure. It fails on repeated runs, or at a
high enough rate. You have captured the exact symptom (the error text, the
wrong output, the timing) so you can later confirm the fix addressed it.

Then shrink the scenario to the smallest one that still fails. Remove
inputs, callers, config, data, and steps one at a time, rerunning the check
after each cut, and keep only what the failure needs. A small scenario
leaves fewer parts to suspect in Phase 3 and is what the report hands to
whoever writes the fix. Done when removing any one remaining part makes the check pass.

## Phase 3: List the suspects

Write three to five ranked hypotheses before testing any. One hypothesis
anchors you on the first plausible idea.

Each one must make a prediction: "If X is the cause, then changing Y makes
the bug go away" or "makes it worse". A hypothesis with no prediction is a
hunch. Sharpen it or drop it.

Rank the list with what the brief says changed recently ("we deployed a
change to number 3 yesterday" moves number 3 to the top). Keep the ranked
list as you wrote it before testing, since the report quotes it.

## Phase 4: Probe

Each probe tests one prediction from Phase 3. Change one thing at a time.

Use a debugger or a REPL when the environment has one. One breakpoint
beats ten log lines. Otherwise add a log at the points that tell two
hypotheses apart. Never log everything and grep.

Tag every debug log with one unique prefix, such as `[DEBUG-a4f2]`, so
cleanup is one grep. Untagged logs get left behind.

For a performance regression, logs are the wrong tool. Measure a baseline
first (a timing harness, `performance.now()`, a profiler, a query plan),
then bisect. Measure before you change anything.

## Phase 5: Report

Stop once one hypothesis has held up under its probe. Do not fix the bug.
Whoever fixes it starts from this report, so it carries everything they
need and nothing they must redo.

Before writing it, remove every `[DEBUG-...]` line (grep the prefix) and
delete every throwaway harness, or leave it in a folder marked as debug
and say where. Leave the working tree as you found it, apart from the
check when it is a test file worth keeping.

The report says, in this order:

1. The cause, in one or two sentences, with the file and function.
2. The evidence. Which probe confirmed it, what it showed, and which other
   hypotheses failed their probes and how.
3. The reproducing command from Phase 1, quoted exact, with its redacted
   output.
4. The shrunk scenario from Phase 2, so a fix can be tested against the
   smallest case.
5. Where a regression test could go. Name the public function or endpoint
   a test would call. When no place reaches the real bug (one caller when
   the bug needs several, a unit test that cannot rebuild the chain that
   triggers it), say so, since that is a finding about the code's shape.
6. What a fix would touch, as a sketch, without writing it.

Send the report back as your final message and nowhere else. Do not post
it to the issue, the ticket, a PR, a note, or a file, and do not draft a
comment for any of those.
