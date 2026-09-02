---
name: writing-voice
description: Use before shipping any artifact, whatever its length. An artifact is prose that lives on after the turn: a repo file, a PR body, a commit message, a comment, a doc, a note, a spec, a plan. Runs two passes on a draft before it ships. Chat replies never get it, since the output style alone shapes them.
---

# Writing voice

The Plain English output style already shapes every sentence (it sits in the
system prompt of every session). That is one pass, written and sent. This
skill is the second pass, and a second pass catches what a first pass cannot,
because writing and revising are different jobs.

## When it runs

Run it on every artifact, whatever its length. An artifact is prose that
lives on after the turn and that a person may read more than once: a file
written into a repo, a PR body, a commit message past its subject line, a
comment on a PR or a ticket, a doc, a note, an audit, a spec, a plan, a
handoff summary. A one-line commit subject and a one-line comment get the
ritual too, because a short artifact is read as often as a long one.

A chat reply never gets the ritual. The output style shapes it as it is
written, and that is the whole treatment. Drafting a reply to a file for
checking doubles its cost and, measured over a session, catches only long
sentences the style already forbids.

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

The output style alone shapes a chat reply. When a reply carries an
artifact inside it (a PR body pasted for approval, a comment to be posted),
run the ritual on the artifact and paste the checked text.

Do not announce the ritual, apologize for the delay, or mention the draft
file. The artifact arrives as an artifact.

## Subagents

The output style and this skill load in the main conversation only. A
spawned subagent runs its own system prompt and gets neither. When a
subagent will write an artifact (a PR body, a commit message, a
comment, a doc), its prompt must carry the writing rules and the
instruction to run this ritual on anything it ships. When the subagent can
return a draft instead of publishing it, do that, and run the passes in the
main conversation before shipping.

## References

- [RULES.md](RULES.md): the sixteen rules in full with their carve-outs,
  plus the cases where the passes do not run at all (quoted and code text, a
  rule that would delete the answer, an explicit instruction that outranks
  this skill).
- [EXAMPLES.md](EXAMPLES.md): before/after pairs for every rule, taken from
  real output.
