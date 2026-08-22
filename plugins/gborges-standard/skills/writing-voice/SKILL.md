---
name: writing-voice
description: Use before sending or shipping any prose longer than 200 characters, code blocks excluded. That covers ordinary chat replies of more than about three sentences, and every file deliverable, audit, spec, plan doc, PR body, architecture doc, handoff summary, status writeup, and review verdict. Runs two passes on a draft before it ships. Only a reply of a couple of sentences or less skips it.
---

# Writing voice

The Plain English output style already shapes every sentence (it rides in the
system prompt of every session). That is one pass, written and sent. This
skill is the second pass, and a second pass catches what a first pass cannot,
because writing and revising are different jobs.

## When it runs

Run it on any prose you are about to send or ship that is longer than 200
characters, counting only the prose. Exclude fenced code blocks and their
contents, and do not count whitespace. Two hundred characters is roughly
three sentences, so the count rarely needs doing by hand. A reply that runs
past a short paragraph qualifies.

The threshold applies to chat replies and to files alike. A one-line answer,
a yes or no, a single sentence confirming a command ran, all skip the ritual
and rely on the output style alone.

The threshold is a floor, not the only trigger. Anything a person will read
twice gets the ritual regardless of length: a PR body, a commit message
longer than its subject line, a document heading into a repo.

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
   carve-out you can state, then ship. A fix changes wording, never scope.
   "Required" does not become "sufficient", "not tested" does not become
   "incorrect", and "do X if Y" does not become "X only when Y".

## Replies

A reply past the threshold gets the same treatment as a file. Draft it to a
file in the scratchpad, run both passes, and send the fixed text as the
reply. The reader gets the checked version and never sees the passes run.

Do not announce the ritual, apologize for the delay, or mention the draft
file. The reply arrives as a reply.

## Subagents

The output style and this skill load in the main conversation only. A
spawned subagent runs its own system prompt and gets neither. When a
subagent will write prose a person reads (a PR body, a commit message, a
comment, a doc), its prompt must carry the writing rules and the
instruction to run this ritual on anything it ships. When the subagent can
return a draft instead of publishing it, do that, and run the passes in the
main conversation before shipping.

## References

- [RULES.md](RULES.md): the fourteen rules in full with their carve-outs,
  plus the cases where the passes do not run at all (quoted and code text, a
  rule that would delete the answer, an explicit instruction that outranks
  this skill).
- [EXAMPLES.md](EXAMPLES.md): before/after pairs for every rule, taken from
  real output.
