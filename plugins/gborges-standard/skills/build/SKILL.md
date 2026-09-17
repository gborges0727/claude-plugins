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

## Where the work happens

Every build runs in its own git worktree, so the user's checkout stays as
they left it while files change and tests run. Make the worktree before
anything else in this skill, whoever runs the loop.

1. Clear out worktrees that earlier builds left behind. Run
   `git worktree list` and look at every path that contains `-build-`. A
   leftover is safe to remove when `git -C <path> status --porcelain`
   prints nothing and `git rev-list --count HEAD..<its branch>` is above
   zero, which means its work is committed on its branch. Remove each safe
   one with `git worktree remove <path>`. Leave the others, and name them
   and what they still hold in the reply. A clean worktree with no commits
   may belong to a build that another session just started.
2. Pick a short slug for the ask. From the repo's root, run
   `git worktree add ../<repo>-build-<slug> -b build/<slug>`. The branch
   starts from the current `HEAD` unless the invocation names another base.
3. Uncommitted changes in the user's checkout do not come along. When the
   ask builds on them, stop and tell the user.
4. A new worktree holds only tracked files. Run the repo's install command
   there, and copy in any untracked file the tests need, such as a `.env`.
   Keep a list of the files you copied in.
5. Do every later step inside the worktree: the loop, the suite runs, the
   review's diff, and the fixes.

Done when `git worktree list` shows the new path and the test command runs
there.

## Who runs the loop

When the ask is the conversation, run "Where the tests go" and "The loop"
in this session. A brief would have to retell the discussion, and a detail
it dropped would be built wrong.

When the ask is a spec file or an issue, hand those two sections to one
subagent, then do "Review" and "Finish" in this session. The ask already
stands alone, and this session needs the diff, not the test output that
led to it. Send the brief to `gborges-standard:opus-medium`. When
`~/.claude/gborges-standard.json` says `"codex": true`, send it through the
`codex-delegate` skill on the `sol-xhigh` rung instead.

The brief carries:

- the spec's path, or the issue number or URL
- the worktree's path, with the instruction to change files nowhere else
- the path to this file, which is `SKILL.md` in the base directory printed
  when this skill loaded, with the instruction to follow "Where the tests
  go" and "The loop" and stop after the full suite run. `tests.md` and
  `mocking.md` sit beside it.
- the commands that run the type checker and the tests, when you know them
- the instruction to leave the changes uncommitted in the worktree
- what to send back: the public functions the tests call, the files
  changed, and the full suite's pass and fail counts

When it returns, run the full suite once yourself, then go on to "Review".

A spec with tickets skips this section and follows
[many tickets](#many-tickets).

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

1. Commit the work on `build/<slug>` inside the worktree. Removing a
   worktree deletes whatever it holds uncommitted, so the commit comes
   first.
2. Leave the files you copied in out of that commit. Run
   `git -C <path> status --porcelain` and confirm it lists nothing but
   those files.
3. Run `git worktree remove <path>` from the repo's root. Git refuses when
   the copied-in files are untracked. Add `--force` then, and only when
   step 2 showed nothing else. Done when `git worktree list` no longer
   shows the path and `git log build/<slug>` shows the commit.
4. Describe the changes in the reply and name the branch.

Merge the branch into the one the user was on only when the invocation said
to ("build and commit", "build and merge"). Never push.

When the build stops early (a failing suite you could not fix, a question
for the user), leave the worktree in place, since it holds uncommitted
work. Give its path in the reply, with the `git worktree remove --force`
command that discards it.

## Many tickets

When the spec has tickets, each ticket is a thin slice through the whole app
that works end to end, and each names the tickets that must finish before
it can start.

1. Read the spec and every ticket. Note which tickets have no unfinished
   blockers.
2. Make the spec's branch and worktree as in
   [Where the work happens](#where-the-work-happens). Every merge below
   happens in that worktree.
3. For each ticket that can start, spawn a `gborges-standard:opus-medium`
   subagent in its own git worktree, on its own branch cut from the
   spec's branch. The brief carries
   the ticket file's path, the spec's path, this skill's loop and test
   rules, and the command that runs that ticket's tests. Start every
   startable ticket at once.
4. When a subagent finishes, merge its branch into the spec branch. Then
   start any ticket that merge unblocked.
5. A ticket whose check failed escalates once, to
   `gborges-standard:opus-xhigh`, with the same brief plus the exact
   failure output. Reread the brief for a mistake first. After a second
   failure, stop and report the ticket to the user, with the path of the
   worktree it left.
6. When every ticket is merged, run the review step on the whole spec
   branch and fix the findings. Remove every ticket's worktree and delete
   its merged branch, then follow [Finish](#finish) for the spec's
   worktree.
