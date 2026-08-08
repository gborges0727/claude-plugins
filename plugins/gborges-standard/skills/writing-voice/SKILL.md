---
name: writing-voice
description: Use when shipping a file deliverable longer than a few paragraphs, an audit, a spec, a plan doc, a PR body, an architecture doc. Runs two passes on a draft before it ships. Chat replies are covered by the Plain English output style and do not need this skill.
---

# Writing voice

The Plain English output style already shapes every sentence (it rides in the
system prompt of every session). This skill is the heavier ritual for
documents, because prose someone will read twice deserves two passes before
it ships.

## The ritual

1. Draft the document to a file.
2. **Pass 1, the mechanical scan.** Run `python3 <base>/scripts/check.py
   <draft>`, where `<base>` is this skill's base directory, printed when the
   skill loads. The script flags banned strings and overpacked sentences,
   each tagged with the rule it breaks. Every hit is a report, not a verdict:
   the rules carry carve-outs the script cannot evaluate, so read the rule in
   RULES.md before rewriting on its authority.
3. **Pass 2, the reading-effort scan.** Go sentence by sentence and name the
   new information each sentence delivers. A sentence delivering nothing new
   is padding: cut it. A sentence delivering two or more ideas is density:
   split it. Check that each sentence has a concrete verb and calls things by
   their real names. Do not scan for banned words in this pass; that is
   pass 1's job, and it returns "nothing found" on prose that is dense in
   other ways. When the pass ends, reread the question or task the document
   answers, and cut whatever answers something nobody asked.
4. Fix, re-run pass 1 until it comes back clean or every remaining hit has a
   carve-out you can state, then ship.

## References

- [RULES.md](RULES.md): the fourteen rules in full with their carve-outs,
  plus the cases where the passes do not run at all (quoted and code text, a
  rule that would delete the answer, an explicit instruction that outranks
  this skill).
- [EXAMPLES.md](EXAMPLES.md): before/after pairs for every rule, taken from
  real output.
