---
name: handoff
description: Write the conversation up so a fresh session can continue the work, and start that session when asked. Explicit invocation only.
argument-hint: "What the next session is for, and where to put the handoff"
disable-model-invocation: true
---

# Handoff

Write a handoff document that lets a fresh session, with none of this
conversation, pick up the work.

## Where it goes

The handoff path in the plugin's
[output-locations.md](../../reference/output-locations.md), which is
`docs/handoff/<slug>.md` unless the repo's `.claude/gborges-standard.json`
names another docs folder. "In Bear" means the `bear-notes` skill. A path
in the argument means that path. Never the OS temp directory.

## What it says

Open with today's date and the one-line goal of the next session. When the
argument says what the next session is for, write the handoff for that.

Then, in whatever order reads best:

- where the work stands now, and what is left
- the decisions made, each with its reason
- what was tried and did not work, so it is not tried again
- the commands that check the work, quoted exact
- the skills the next session should use, by name
- open questions only the user can answer

Point at what already exists instead of restating it: a spec, a plan, a
decision record, an issue, a commit, a diff. Give the path or URL and one
line on what it holds.

Replace every secret (an API key, a password, a token, a personal detail)
with `<REDACTED>`.

Run the `writing-voice` passes on the file before you finish.

## Starting the next session

When the argument asks for it ("and start it", "kick it off"), launch a
background session with the handoff as its prompt after writing the file:

```sh
claude --bg --name "<short descriptive name>" "$(cat <handoff path>)"
```

It starts in the current directory and returns at once. The user manages
it with `claude agents`. Without that ask, print the path and stop.
