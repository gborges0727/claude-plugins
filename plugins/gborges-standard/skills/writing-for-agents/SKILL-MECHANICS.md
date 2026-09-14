# Skill mechanics

What changes when the document is a skill: the frontmatter, who may invoke
it, and a skill that only lists other skills. Everything else is in
[SKILL.md](SKILL.md).

## Who may invoke it

Two choices, trading the two costs in `SKILL.md`.

A **model-invoked** skill keeps its `description` in the agent's context
on every turn, so the agent can fire it on its own and other skills can
call it. The user can still type its name. The description is the skill's
pointer, always loaded, and its wording follows the pointer rules in
`SKILL.md`: trigger words first, one trigger per case. A model-invoked
skill that is all reference is also the one way to share reference between
skills, since another skill can call it. To make one, leave
`disable-model-invocation` out of the frontmatter.

A **user-invoked** skill hides its description from the agent. Only a
person typing its name can run it, and no other skill can. It costs no
context, and it costs the human remembering it exists. To make one, set
`disable-model-invocation: true`. The description then reads as one line
for the human, with no trigger list. For Codex, which ignores that field,
add `agents/openai.yaml` next to `SKILL.md` with
`allow_implicit_invocation: false`.

Pick model invocation only when the agent must reach the skill on its own,
or another skill must call it. A skill that only ever runs by hand is
user-invoked and costs nothing per turn.

Reference that two user-invoked skills both need cannot live in either,
since neither can call the other. Put it in a plain file outside the skill
system and point at it from both. This plugin keeps such files under
`reference/`.

## Splitting by invocation

Split off a model-invoked skill when a distinct trigger word you use in
your own prompts should fire it on its own, or when another skill must
call it. The new description costs context on every turn, so the
independent reach has to be worth that.

## A skill that lists other skills

When user-invoked skills grow past what one person can remember, one more
user-invoked skill can list them and say when to reach for each. It can
only point. It cannot fire them, since user-invoked skills have no
description for it to reach.
