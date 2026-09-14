---
name: diagnosing-bugs
description: Find the cause of a hard bug or a slow path by first building a fast check that fails on this bug, then testing hypotheses against it. Use when the user says diagnose or debug, or reports something broken, throwing, failing, or slow.
---

# Diagnosing bugs

A method for a hard bug. Skip a phase only when you can say why.

Read `CONTEXT.md` when the repo has one, so you know the names of the parts
you are looking at, and read the decision records under `docs/adr/` for the
area.

## Redact first

This method has you show commands, outputs, and captured files. Replace
every secret with `<REDACTED>` before showing anything. Build the check
around environment variables so the credential stays in the environment
and out of what you show. A captured request carries auth headers, so
quote only the lines that matter. When the redacted output is not enough
to diagnose the bug, say so and ask the user.

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

Stop and say so. List what you tried. Ask the user for access to the
environment where it happens, or a redacted capture (a HAR file, a log
dump, a core dump, a screen recording with timestamps), or permission to
add temporary logging in production. Do not move on to hypotheses without
a check.

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
leaves fewer parts to suspect in Phase 3 and becomes the regression test in
Phase 5. Done when removing any one remaining part makes the check pass.

## Phase 3: List the suspects

Write three to five ranked hypotheses before testing any. One hypothesis
anchors you on the first plausible idea.

Each one must make a prediction: "If X is the cause, then changing Y makes
the bug go away" or "makes it worse". A hypothesis with no prediction is a
hunch. Sharpen it or drop it.

Show the ranked list to the user before testing. They often know something
that reorders it at once ("we deployed a change to number 3 yesterday").
Do not wait for them. Continue with your ranking if they are away.

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

## Phase 5: Fix, with a regression test first

Write the regression test before the fix, when there is a place to put it
that reaches the real bug. The test must reproduce the pattern the bug
occurs in at its real call site. When the only place a test can go is too
shallow (one caller when the bug needs several, a unit test that cannot
rebuild the chain that triggers it), a test there gives false confidence.

When no such place exists, that is a finding. Write it down. The code's
shape is stopping the bug from being pinned, and the cleanup phase should
note it.

When such a place exists:

1. Turn the shrunk scenario into a failing test there.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Rerun the Phase 1 check against the original, unshrunk scenario.

## Phase 6: Clean up

Before saying it is done:

- [ ] the Phase 1 check passes on the original scenario
- [ ] the regression test passes, or the note says why there is none
- [ ] every `[DEBUG-...]` line is gone (grep the prefix)
- [ ] every throwaway harness is deleted or moved somewhere marked as
      debug
- [ ] the hypothesis that turned out right is stated in the commit or PR
      message, so the next person learns it
