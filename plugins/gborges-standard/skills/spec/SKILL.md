---
name: spec
description: Write the conversation up as a spec file, and split it into tickets only when the work is too big for one session. Explicit invocation only.
disable-model-invocation: true
---

# Spec

Turn what has been discussed into a spec. Do not interview the user. Write
down what you already know, and mark the gaps as open questions inside the
spec.

## Step 1: Gather

Work from the conversation. When the invocation names a path, an issue
number, or a URL, read that too, comments included. When you have not yet
read the code the spec touches, read it now. Use the words in `CONTEXT.md`
when the repo has one, and keep to the decision records under `docs/adr/`
for the area.

## Step 2: Write the spec

Write it to the spec path in the plugin's
[output-locations.md](../../reference/output-locations.md), which reads
the repo's `.claude/gborges-standard.json` and falls back to
`docs/specs/<slug>.md`. A path or place the user named wins.

Use this template:

```markdown
# <Title>

## Problem

What the user is running into, from their point of view.

## Solution

What changes for the user once this is built.

## Decisions

Each decision made in the discussion, one bullet each. Modules to build or
change, what each exposes, schema changes, API contracts, and the reason
when the choice was not obvious. Name files and functions freely.

## What the tests call

The public functions, endpoints, or commands the tests will go through,
and any existing test in the repo to copy the shape of.

## Out of scope

What this spec does not cover, so nobody builds it by accident.

## Open questions

Anything the discussion left unsettled, one bullet each. Delete the section
when there are none.
```

Write the file, then run the `writing-voice` passes on it.

## Step 3: Offer tickets

Most specs are one session of work and need no tickets. Offer to split only
when the spec would not fit one session, or when the user asked for tickets.
Say why in one line and wait for a yes.

## Step 4: Split into tickets

Each ticket is one thin slice through every part of the app that works end
to end: schema, API, UI, and tests for that slice, all in one ticket. Never a
ticket per layer. A finished ticket can be demonstrated on its own, and one
ticket fits one fresh session.

Each ticket names the tickets that must finish before it can start. A ticket
with none can start at once.

One mechanical change that touches the whole codebase at once (renaming a
column, changing a shared type) does not fit a slice. Split it into three
kinds of ticket instead. First add the new form beside the old, so nothing
breaks. Then move the callers over in batches, one ticket per package or
folder, each blocked by the add. Last, delete the old form, blocked by every
batch.

Before writing the files, show the list: title, blocked by, and the
end-to-end behaviour each ticket delivers. Ask whether the size is right and
whether the blockers are the real ones. Adjust until the user approves.

Then write one file per ticket at the tickets path from
`output-locations.md` (default `docs/specs/<slug>/tickets/NN-<slug>.md`),
numbered from `01` with blockers first:

```markdown
# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from
the user's side.

**Blocked by:** the numbers and titles of the tickets that must finish
first, or "None".

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2
```

When the repo's `tracker` is `github`, also open one issue per ticket in
the same order, with the blocking issue linked in each body, and one issue
for the spec that links them all.
