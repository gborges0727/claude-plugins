---
name: routine
description: Grill the user into a spec for one recurring routine (a daily check, a weekly report, a step on every new issue) that an agent could build unasked. Explicit invocation only.
argument-hint: "A routine to design, or nothing to go find one"
disable-model-invocation: true
---

# Routine

Run a `grill` session whose only output is a spec for a recurring routine.
Ask in rounds, with a recommended answer on each question, and create,
edit, or delete spec files as the answers settle things.

## What a routine is

A routine is something the user does again and again: every morning, every
week, every time an email or an issue arrives. Looking at a week as a set of
routines shows how predictable much of it is, and a predictable routine can
be handed to an agent or a script. Use that view to find routines worth
specifying, and propose ones the user has not noticed.

A routine spec lives at the routine path in the plugin's
[output-locations.md](../../reference/output-locations.md) (default
`docs/routines/<slug>.md`). The spec is the source of truth for that
routine.

## Words the spec may use

Reach for these only when the routine calls for them. A routine needs no
AI, no human check-in, and no schedule unless the grilling shows it does.

- **Trigger.** What starts each run: an event (a new email, a new issue) or
  a schedule (every morning at 7). An event usually costs less than a
  schedule that polls.
- **Check-in.** A point where the run stops and asks the user to verify or
  decide. Some routines have none and run on their own.
- **Push the check-in late.** Do as much as possible before asking the
  user, so they are asked once, near the end, with everything prepared.
- **Brief.** What a check-in shows: a short, decision-ready summary of what
  was produced and why, with a link to the thing itself. Never the raw
  output. The user must be able to decide in seconds.

## Done

A routine spec is done when an agent could build it without asking a single
question. Keep grilling until then.

## Notes about the user's world

Keep `docs/routines/NOTES.md` (or the configured folder) with what you
learn about the user's tools, the channels they process, and their own
words for both. When it is empty or thin, interview them about their world
before specifying anything. When a fuzzy term comes up, settle it and
record it here.
