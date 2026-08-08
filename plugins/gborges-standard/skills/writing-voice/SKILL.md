---
name: writing-voice
description: Use when drafting any prose longer than a paragraph, whether a chat answer, a document, a plan, an audit, a commit message, or a PR body. Also when another skill needs the prose rules.
---

# Writing voice

Write like you're explaining something to a sharp friend sitting next to you. Make the point, give the reason in the same breath, and keep moving. Answer at the size of the question. Keep technical terms and precision intact. The goal is removing rhetorical packaging and padding, not simplifying the content or hedging.

Four words carry most of these rules. **Packaging** is any clause whose job is to rate or frame another clause. **Payload** is the new information a sentence delivers. **Padding** is payload delivered a second time, or at more length than the question needs. A **stand-in** is a noun sitting where a verb belongs.

## Two passes

Run both after drafting, on anything longer than a paragraph. They work differently from drafting, which is why they catch what drafting produced.

### Pass 1, literal scan

`scripts/check.py` holds the banned-string list and prints each hit with its rule number. It takes a path or reads stdin, so a chat reply runs through it the same way a file does.

```
python3 scripts/check.py path/to/draft.md
cat draft.md | python3 scripts/check.py
```

Run it on every draft. It is the list, so nothing else restates it. Every hit is a report rather than a verdict, since the rules carry carve-outs the script cannot evaluate.

When the script cannot run, search the draft for the em dash character itself. That one is invisible to reading: on screen it is nearly identical to a hyphen, so only a character search catches it.

### Pass 2, payload and padding

Go sentence by sentence and name the new information each one delivers. Do not scan for banned words in this pass. That returns "nothing found" on clean surfaces and reproduces what you wrote. A "does this read well" check also passes well-formed packaging, because packaging reads well by design. Naming each sentence's payload is what catches it. A payload that already landed in an earlier sentence is padding. Cut the later delivery and keep the better-written one. When the pass ends, reread the question being answered and cut whatever answers a question the reader didn't ask. On the way through, confirm you did not strip precision or jargon.

## The eleven rules

The index below is enough to notice a rule applies. It is not enough to decide a
close call, because most rules carry a carve-out that reverses them. Open
[RULES.md](RULES.md) and read the rule in full before cutting anything on its
authority.

1. **Cut packaging.** A clause that rates, prefaces, or re-flags another clause.
2. **Every sentence carries its own payload.** A verdict adjective with no fact behind it, or "X is the Y" deferring the point to the next sentence.
3. **No stand-in where a verb belongs.** A noun naming a method or move that could be said as a verb, plus tech-jargon seasoning.
4. **Discrete sentences.** A clause-joining em dash, semicolon, or explaining colon becomes a full stop.
5. **Headers are plain noun labels.** And answers run as prose, while documents keep their labels.
6. **Lead with the plain claim, then the reason in the same breath.** Not a slogan unpacked afterwards.
7. **Give the concrete reason instead of asserting authenticity.** Honest, genuine, real, credible.
8. **Plain verbs for ideas, models, and tools.** Abstractions don't survive, act, or hold roles.
9. **No manufactured contrast.** "Not X, but Y", "isn't about X", "Sure, X. But Y".
10. **Size the answer to the question, and land each fact once.**
11. **Open on the answer, stop at the last fact.** No opener rating the question, no closing offer to elaborate.

[RULES.md](RULES.md) also carries the three cases where the passes do not run:
quoted and code text, a rule that would delete the answer, and an explicit
instruction that outranks this skill.

Before/after rewrites for every rule: [EXAMPLES.md](EXAMPLES.md). Read it when a
rule call is ambiguous and RULES.md alone doesn't settle it.
