---
name: pair-debate
description: Put Claude Fable 5.1 and GPT-6 Astra, both at xhigh, in a room to argue a hard problem to a solution. Explicit invocation only.
disable-model-invocation: true
---

# Pair debate

Two architects, Fable 5.1 at xhigh and GPT-6 Astra at xhigh, work one problem as peers. Each
writes a draft without seeing the other's. They argue until they agree on a written
definition of done. The user approves it. Then they alternate turns in one shared worktree
until both agree the work is finished. The deliverable is whatever the brief asks for, a
design document or a verified build.

You are the scrum master, not a third architect. `scripts/debate.py` in this skill's folder
runs the conversation. Your job is to write the brief, start the script, watch its events,
report to the user, run the one checkpoint, and verify the result at the end.

Invoking this skill is the user's naming of Fable and Astra. The hooks that refuse either
model unasked record the invocation as the ask, so nothing here needs a workaround.

## Step 1: Write the brief

Write the user's ask to `<scratch>/<topic>.brief.md`, where `<topic>` is a short kebab-case
slug. The brief is all either architect knows, so it carries the problem, the repo, the
constraints, and what kind of deliverable the user wants. A build ask says so, and names the
metric if the user gave one. A "not based on anything" ask names the paths the architects
must not read. Do not show the brief to the user first. The checkpoint in step 3 catches a
misread ask, with both architects' reading attached.

The step is done when the brief file names the deliverable kind and every constraint the
user stated.

## Step 2: Start the run

Run `command -v codex` first. When Codex is missing, stop and say so. This skill has no
single-model fallback.

Start the script in the background:

```sh
python3 <base>/scripts/debate.py start \
  --repo /absolute/path/to/repo --topic <topic> --brief <scratch>/<topic>.brief.md
```

`--out <rel>` moves the room folder from its default of `docs/rooms/<topic>` when the user
asked for another place. The script makes a worktree at `<repo>-pair-debate-<topic>` beside
the repo on branch `pair-debate/<topic>`, and keeps its state under
`~/.claude/gborges-standard/pair-debate/<topic>/`. Its `events.jsonl` there is what you
watch, and `status --state <dir>` prints the run's state.

Then arm a Monitor on the events file so the user hears about progress while the script
runs:

```sh
tail -n +1 -f ~/.claude/gborges-standard/pair-debate/<topic>/events.jsonl \
  | grep --line-buffered -E '"event": "(drafts-done|checkpoint|check-first-pass|agreed|error|missing-status)"'
```

Mark it persistent. Every line it emits is one event to report.

The step is done when the background command is running and the Monitor is armed.

## Step 3: Report on events, and run the checkpoint

Tell the user one or two sentences per event, in plain words, as each lands. `drafts-done`
means both blind drafts are in the room folder. `check-first-pass` means an architect ran the
agreed check and it passed for the first time. `missing-status` means a reply ended without
its status line, and the script counted it as continue. `error` means a turn failed, and the
`detail` field names the log to read. Nothing else in the transcript needs relaying. The
user reads `transcript.md` in the room folder when they want the argument itself.

`checkpoint` is the one place the run waits for the user. The script has exited with phase
`awaiting-approval`. Read `definition-of-done.md` and `check.sh` from the room folder, tell
the user what the architects agreed finished means and what command checks it, and ask
whether to proceed. Wait for the answer however long it takes. When the user adds a note,
write it to `<scratch>/<topic>.note.md` and pass it with `--note`. Then resume in the
background, and re-arm the Monitor if it has stopped:

```sh
python3 <base>/scripts/debate.py resume \
  --state ~/.claude/gborges-standard/pair-debate/<topic> [--note <scratch>/<topic>.note.md]
```

The step is done when the run reaches `agreed` or `error`.

## Step 4: Verify and report

`agreed` is both architects' claim, not a result. In the worktree, run `bash <room>/check.sh`
yourself and read `git log` from the branch point. Then report the branch and worktree
path, the definition of done in a sentence, the check's exit code and last lines, and the
disagreements the transcript records that did not get resolved into the work. Leave the
branch unmerged. Merging is the user's call.

An `error` run stops where it failed. Read the log the event names, say what broke, and
leave the worktree in place. A run resumes from `awaiting-approval` or `work` only, so a
failure in the draft or define phase starts over under a new topic.

The step is done when the user has the check output and the branch name.
