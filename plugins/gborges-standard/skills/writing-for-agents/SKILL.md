---
name: writing-for-agents
description: How to structure a document an agent reads (a skill, a CLAUDE.md or AGENTS.md, a doc reached by a pointer) so the agent follows it the same way every run. Use when creating or editing a skill, a CLAUDE.md, or an AGENTS.md.
---

# Writing for agents

The rules for any document an agent reads: a skill, a `CLAUDE.md` or
`AGENTS.md`, a doc another document points at. The packaging differs. The
writing does not. The aim is a document the agent runs the same way every
time.

For the parts specific to a skill (frontmatter, who may invoke it, a skill
that only lists other skills), read
[SKILL-MECHANICS.md](SKILL-MECHANICS.md). For the prose itself, the Plain
English style in the system prompt applies, and the draft goes through the
`writing-voice` passes before it ships.

## Pointers

A pointer is a line the agent always has in context that names some
material it does not, and says when to go and read it. A skill's
`description` is one. A line in `CLAUDE.md` naming a doc is another. The
pointer's wording decides whether the agent reaches the material, and how
reliably. When material the agent must read sits behind a weakly worded
pointer, the fix is the wording. Move the material into the main document
only when better wording does not work.

A pointer says what the material is, and lists the cases that should send
the agent to it. Every word of a pointer costs on every turn, so cut
harder than in the body:

- Put the word that triggers the pointer first.
- One trigger per case. Two synonyms for one case are the same case twice.
- Leave out what the body already says.

## Two costs

Every document and pointer spends one of two budgets. Material the agent
always has loaded (a `CLAUDE.md` line, a skill description) costs tokens
and attention on every turn whether it is used or not. Material the human
has to remember exists, and reach for by name, costs the human. The second
cost is not one to drive to zero. It is the price of the human choosing.
Spend it where the human's judgement matters and remove it where it does
not.

Material behind a pointer costs only the pointer's line per turn. Material
with no pointer costs only the human's memory.

## What goes where

A document has two kinds of content. Steps are the ordered actions the
agent performs. Reference is the definitions, rules, and facts it looks up
as needed. A document can be all steps (a recipe), all reference (a
review's rules, this file), or both.

Place each piece by how soon the agent needs it:

1. A step in the main file, in order. This is what the agent does.
2. Reference in the main file, read when needed. A flat set of rules is
   fine here.
3. Reference in a second file, reached by a pointer and loaded only when
   the pointer fires. It can be a sibling file in the skill folder or a
   doc anywhere.

Push too little into a second file and the main file bloats. Push too much
and the agent misses material it needed. The test is which cases need it:
what every run needs stays in the main file, and what only some runs need
goes behind a pointer. When reference that only some runs need sits among
the steps, it buries them, and the agent attends to them by chance.

Keep one concept's definition, rules, and exceptions under one heading.
Reading one part then brings the rest. Scattered pieces of one meaning
read like notes, not documentation. That is different from duplication,
which repeats one meaning in two places.

A document that is simply too long fails even when every line is live.
Attention thins across it, and every line is one more to keep current.
Move reference behind pointers, and split by case or by sequence so each
run loads only what it uses.

## Steps end on a check

Every step ends on the condition that says it is done. Two properties make
the condition work.

The agent must be able to tell done from not done. A vague condition
("understanding reached") invites the agent to stop early, pulled by the
steps it can see ahead. Sharpen the condition first, since that is cheap
and local. Only when it cannot be sharpened, and you have seen the agent
rush, hide the later steps by splitting the sequence across a real context
break (a handoff or a subagent). A skill called inline leaves the later
steps in context and hides nothing.

The condition must demand enough. "Every modified model accounted for"
forces thorough work where "produce a change list" does not. The demand
sets how much digging the agent does inside the step without a step of its
own for it. A body of rules gets the same treatment: "every rule applied"
demands as much of a checklist as "every step done" demands of a recipe.

The best conditions are both checkable and exhaustive.

## When to split

Splitting one document into two spends one of the two costs, so split only
when the cut pays for itself.

Split a run of steps when the steps after one tempt the agent to rush it.
Keeping them out of view makes the agent do more on the step in front of
it. Merging two sequences does the reverse. It shows each step the steps
after it and invites rushing.

For splitting a skill by who may invoke it, see
[SKILL-MECHANICS.md](SKILL-MECHANICS.md).

## Say what to do

State the behaviour you want. "Write one-line comments" gives the agent
something to do. "Do not write long comments" names the thing to avoid and
leaves the target unsaid. Write the positive form whenever it is as short.
Keep a ban only when it names a specific trap the agent falls into, and
put the positive target beside it, so the agent has both the thing to
avoid and the thing to do.

State a mechanism in plain words. "The test calls the public function and
checks what comes back" tells the agent what to do. A borrowed word for
the same idea ("test at the seam") saves a few tokens and asks the agent
to guess what the word covers here. Use a short term only when the
document defines it in plain words at first use and reuses it enough to
pay for the definition.

## Pruning

- **One home per meaning.** Changing a behaviour should be an edit in one
  place. The same meaning in two places costs tokens, drifts apart, and
  makes the meaning look more important than it is.
- **Do not copy what the environment already says.** A `package.json`
  script, a config file, the folder layout, and `--help` output are all
  readable. A document that restates them is a cache that goes stale.
  Write down what the agent cannot find by looking: the unwritten
  convention, the reason behind a choice, the trap no config mentions.
- **Check every line still matters.** A line stops mattering when it never
  bears on the task (exposition, or a case that belongs behind a pointer)
  or when the behaviour or world it describes has changed. Without this
  check, stale lines pile up, because adding feels safe and removing feels
  risky.
- **Cut lines the agent obeys anyway.** An instruction the model already
  follows by default costs tokens and changes nothing. The test is whether
  the line changes behaviour against the default, and two people who
  disagree settle it by running the document, not by arguing. When a line
  fails, delete the whole line. A word too weak to change behaviour ("be
  thorough" to an agent already thorough) fails the same test, and the fix
  is a stronger word or a sharper condition.
