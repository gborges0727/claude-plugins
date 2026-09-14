---
name: domain-modeling
description: Keep the project's glossary (CONTEXT.md) and decision records (docs/adr/) sharp while a design is discussed. Use when a term is fuzzy or conflicts with the glossary, when writing or editing CONTEXT.md or CONTEXT-MAP.md, or when a decision deserves an ADR.
---

# Domain modeling

Sharpen the words the project uses while the design is being discussed, and
write them down the moment they settle. Reading `CONTEXT.md` for the right
word is something every skill does on its own. This skill is for changing
the glossary, or recording a decision.

## Files

Most repos have one glossary at the root and one folder of decision
records:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

A repo with several distinct areas of language has a `CONTEXT-MAP.md` at
the root that lists them, and one `CONTEXT.md` per area next to that area's
code. The map's format is in [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md). Read
the map first when it exists, then the glossary for the area the current
topic belongs to. Ask when the area is unclear.

Create a file only when there is something to write in it. The first
settled term creates `CONTEXT.md`. The first decision record creates
`docs/adr/`.

## During the session

**Challenge a term against the glossary.** When the user uses a word in a
way that conflicts with its entry, say so at once: "The glossary defines
cancellation as X, and you seem to mean Y. Which is it?"

**Sharpen a fuzzy term.** When a word could mean two things, propose the
precise one: "By account, do you mean the Customer or the User? Those are
different things here."

**Test the model with a concrete case.** When two concepts are being
related, invent a specific scenario that sits on the line between them and
ask the user which side it falls on.

**Check the code.** When the user states how something works, read the code
that does it. When the code disagrees, say so: "The code cancels whole
Orders, and you said partial cancellation is possible. Which is right?"

**Write the glossary entry at once.** When a term settles, update
`CONTEXT.md` right then, in the format in
[CONTEXT-FORMAT.md](CONTEXT-FORMAT.md). Do not batch entries for later.
The glossary holds definitions only. No implementation detail, no spec
text, no decision belongs in it.

**Offer a decision record only when all three hold.** The decision is hard
to reverse, a future reader would wonder why it was made, and it came from
a real choice between alternatives. When any one is missing, skip the
record. The format and the tests are in [ADR-FORMAT.md](ADR-FORMAT.md).
