---
name: grill
description: Interview the user in rounds until a plan, design, or idea has no open decision left. Explicit invocation only.
disable-model-invocation: true
---

# Grill

Interview the user until the two of you agree on every decision the plan
needs. Every decision leads to further decisions that depend on it, so the
work is a tree. You walk it in rounds.

## Rounds

A round holds every question you can ask now without guessing at an answer
you have not heard yet. Ask all of them in one message, numbered, each with
your recommended answer. Then stop and wait for the user.

Format each question like this:

```
❓ **Q1** - **<question title>**: <question body, as many paragraphs as it needs, with the choices when there are choices>

➡️ <your recommended answer>
```

The user's answers settle some decisions and open the ones that depended on
them. Work out the new set of askable questions and send the next round. A
question whose answer depends on another question still open in this round
waits for a later round.

## Facts are your job

The user decides. You find facts. When a question needs a fact from the
filesystem, a tool, or the web, get it yourself before asking, or send a
subagent for it. A doc page or a single file lookup goes to
`gborges-standard:sonnet-medium`. Anything that reads code to reach a
conclusion goes to `gborges-standard:opus-medium`. A broad search goes to
`Explore`. Do not stop the round for it. Ask every question that does not
depend on the fact now, and ask the ones that do once the fact is back.

## Glossary and decisions

When the repo has a `CONTEXT.md` at its root, also run the
`domain-modeling` skill through the session. It challenges a term the user
uses against the glossary, writes the glossary entry the moment a term
settles, and offers a decision record when a decision is hard to reverse.
Skip this when the repo has no `CONTEXT.md` and the user has not asked for
one.

## Done

The session ends when no question remains, with every branch of the tree
visited and nothing assumed in silence. Then write the whole understanding
out in one message for the user to confirm. Do not act on it until they do.
