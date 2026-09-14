---
name: wayfinder
description: Plan work too big for one session as a map of open questions, then answer them one session at a time until the way to build it is clear. Explicit invocation only.
disable-model-invocation: true
---

# Wayfinder

An idea has arrived that is too big for one session, and the way from here
to done is not visible yet. This skill writes a map of the questions that
stand in the way, then answers them one session at a time. When every
question is answered, the map is done and someone can go and build the
thing.

The output is decisions, never the build itself. When you feel the pull to
start building, that is the end of the map. Stop and hand off. The map's
Notes can say otherwise for one effort, and only then does building happen
inside the map.

## The map

The map is one file, at the map path in the plugin's
[output-locations.md](../../reference/output-locations.md) (default
`docs/specs/<slug>/map.md`). Its body:

```markdown
## Destination

What done looks like: the spec, decision, or change this map leads to. One
or two lines. Every session reads this before picking a question.

## Notes

The area of the codebase, the skills every session should use, and any
standing preference for this effort.

## Decisions so far

- [<question title>](questions/NN-<slug>.md): one-line gist of the answer

## Not yet specified

Questions you can tell are coming but cannot phrase precisely yet, because
they depend on questions still open. Written loosely.

## Out of scope

Work ruled outside the destination, one line each, with the reason.
```

The map is an index. A decision lives in its question file, and the map
gives the gist and the link.

## Questions

Each open question is one file at `docs/specs/<slug>/questions/NN-<slug>.md`
(or the repo's configured folder), numbered from `01`:

```markdown
# <NN>: <Question title>

**Type:** research | prototype | grilling | task

**Blocked by:** the numbers of the questions that must be answered first,
or "None".

**Status:** open | answered

## Question

The decision or investigation this file resolves. Sized to one session.
```

A question is answered by appending an `## Answer` section, setting the
status, and adding one line to the map's Decisions so far.

The four types:

- **research**, done without the user. Read docs, a third-party API, or
  local material to find a fact the decision needs. Answered by the
  `research` skill.
- **prototype**, done with the user. Build something rough enough to react
  to when the question is how it should look or behave.
- **grilling**, done with the user. A conversation. The default type. Run
  the `grill` skill, which brings in `domain-modeling` when the repo has a
  glossary.
- **task**, with or without the user. Work that must happen before a
  decision can be made: sign up for a service, provision access, move data
  so its shape can be seen. The answer records what was done and any fact
  later questions need.

A question done with the user is answered only in that conversation. Never
answer the user's side yourself.

## Ticket or not yet

Write a question file when you can state the question precisely now, even
when you cannot act on it yet. Write a line under Not yet specified when
you cannot phrase it that sharply. Do not pre-split a vague area into
question-sized pieces. One vague line may become several questions later,
or none.

Work that lies past the destination goes under Out of scope, never under
Not yet specified. When an existing question is found to lie past the
destination, mark it answered with a one-line note, move its gist to Out of
scope, and leave it out of Decisions so far.

## Charting the map

The user invokes with a loose idea.

1. Name the destination. Run the `grill` skill to pin down what this map
   leads to. Settle this first, since it fixes the scope.
2. Find the open questions. Grill again, wide rather than deep, across the
   whole effort. When this turns up nothing that will not fit one session,
   there is no need for a map. Say so and ask how the user wants to
   proceed.
3. Write the map with Destination and Notes filled, Decisions so far empty,
   and the vague areas under Not yet specified.
4. Write the question files you can state now, then fill in each one's
   blockers.
5. For each research question, start a background `research` run at once.
6. Stop. Charting is one session's work.

## Working the map

The user invokes with the map's path, and optionally a question.

1. Read the map. Read a question file only when you need it.
2. Take the question the user named, or the lowest-numbered open question
   whose blockers are all answered.
3. Answer it. Read related question files as needed. Use the skills the
   map's Notes name. When in doubt, run `grill`.
4. Record the answer in the question file, set its status, and add the line
   to the map.
5. Write any new question the answer made precise, and remove its line from
   Not yet specified. Move anything the answer put outside the destination
   to Out of scope. Update or delete any question the answer invalidated.

Answer one question per session, except research questions, which can run
several at once.

When the repo's `tracker` is `github`, the map and each question also
exist as issues, the questions as sub-issues of the map, with GitHub's
blocking relation between them. Answering a question closes its issue with
the answer as a comment.
