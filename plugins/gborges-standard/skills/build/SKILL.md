---
name: build
description: Build the work under discussion test-first, one failing test at a time, then review the diff against the ask. Explicit invocation only.
disable-model-invocation: true
---

# Build

Build what was asked, test-first, and review the result before handing it
back.

## What to build

The ask is the conversation so far, unless the invocation names something
else. "/build let's do it" after a discussion means build what was
discussed. A path means that spec file. An issue number or URL means that
issue, with its comments. A spec whose folder has a `tickets/` subfolder
turns on the [many tickets](#many-tickets) mode below.

Read `CONTEXT.md` when the repo has one, so names in tests and code match
the project's words. Read the decision records under `docs/adr/` for the
area you are changing and keep to them.

## Where the tests go

Before the first test, decide which public functions, endpoints, or
commands the tests will call. Prefer ones that exist. Prefer the fewest that
cover the behaviour, and the ones furthest from the implementation, so a
test still passes when the code underneath is rewritten. Say the list in one
line and start. The user can redirect you afterwards if the list was wrong.

A test calls the public interface and checks what comes back or what the
next public call can see. It never reads a private field, calls a private
method, or queries the database to check what a function did. The rules and
examples are in [tests.md](tests.md). Mock only at the edges of the system,
as in [mocking.md](mocking.md).

## The loop

1. Write one test that fails because the behaviour is missing.
2. Write the smallest code that makes it pass. Add nothing for a test you
   have not written yet.
3. Run the type checker and that one test file.
4. Repeat with the next behaviour.

Write tests and code in turns, never all the tests first. A test written
before the code that passes it teaches you the next test. Twenty tests
written up front test a shape you imagined.

Refactoring happens after the loop, in the review step, never inside a
cycle.

When every behaviour has its test, run the full suite once.

## Review

Dispatch a review to `gborges-standard:opus-medium`. The brief carries:

- the diff to review, as `git diff <base>...HEAD` plus any uncommitted
  changes, and the commit list
- the ask, quoted or by path
- the repo's own review instructions, when it has any: a `CODE_REVIEW.md`,
  a `CONTRIBUTING.md`, a review section in `CLAUDE.md`, or a pull request
  template. The repo's instructions win wherever they and this skill
  differ.
- this skill's own check, on top of the repo's: list what the ask wanted
  that the diff does not do, what the diff does that the ask did not want,
  and what looks done but wrong. Quote the ask for each finding.

Fix what the review finds. Run the full suite again when anything changed.

## Finish

Leave the changes in the working tree and describe them in the reply. Commit
only when the invocation said to ("build and commit"). Never push.

## Many tickets

When the spec has tickets, each ticket is a thin slice through the whole app
that works end to end, and each names the tickets that must finish before
it can start.

1. Read the spec and every ticket. Note which tickets have no unfinished
   blockers.
2. Create a branch for the whole spec.
3. For each ticket that can start, spawn a `gborges-standard:opus-medium`
   subagent in its own git worktree on its own branch. The brief carries
   the ticket file's path, the spec's path, this skill's loop and test
   rules, and the command that runs that ticket's tests. Start every
   startable ticket at once.
4. When a subagent finishes, merge its branch into the spec branch. Then
   start any ticket that merge unblocked.
5. A ticket whose check failed escalates once, to
   `gborges-standard:opus-xhigh`, with the same brief plus the exact
   failure output. Reread the brief for a mistake first. After a second
   failure, stop and report the ticket to the user.
6. When every ticket is merged, run the review step on the whole spec
   branch, fix the findings, and delete the worktrees.
