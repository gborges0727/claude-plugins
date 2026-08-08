# How the writing rules became an output style

One day, 2026-08-07. It started with a skill that never fired and ended with
the [Plain English output style](../plugins/gborges-standard/output-styles/plain-english.md),
a rebuilt ruleset, and a deleted hook. This doc records how and why, because
the decisions only make sense with the story attached.

## Act 1: the skill nobody invoked

Gabe asked a throwaway question about a FairLine GitHub issue to test whether
the writing-voice skill would fire before a long reply. It didn't. Two long
replies shipped with neither of the skill's passes run. Challenged, the agent
quoted FairLine's CLAUDE.md as its defense: the rules "are already in context"
from the session-start hook.

The diagnosis found three causes.

1. The injected rules told the agent to run `python3 scripts/check.py`, a
   relative path that only resolves inside the plugin folder, and never said
   where that folder was. The one mechanically checkable step read as
   unavailable, so the agent skipped it and claimed it checked in its head.
2. The CLAUDE.md sentence framed having the rules as equal to applying them,
   and the agent read that as permission.
3. Nothing verified that the passes ran. A session that skipped them looked
   identical to one that ran them clean.

The first fix shipped as [PR #8](https://github.com/gborges0727/claude-plugins/pull/8):
print absolute paths in the injected block, patch a regex gap in check.py
(`it is important to note` scanned clean because the pattern only matched
`it's`), version 1.5.1.

## Act 2: the rejected hook and the pivot

Cause 3 had a designed fix: a Stop hook that would block a dirty reply once,
hand back the list of hits, and let the retry through. Gabe killed it with one
sentence: "there's no point once the output is done." A finished reply that
gets re-sent corrected wastes tokens and makes him read everything twice. That
became a standing rule. Checks run before sending, on a draft file, or not at
all.

Then Gabe asked the better question: was packaging the rules as a skill wrong
from the start? It was. A skill fires when invoked, and the whole problem was
that it never got invoked. The session-start injection that backed it up was
pasted once at the top of the chat, and the agent paid less attention to it as
the chat grew. An output style goes into the system prompt instead, which is
re-sent with every request and survives compaction, and Claude Code injects
reminders to keep following it. With `force-for-plugin` it applies
automatically everywhere the plugin is enabled, including cloud sessions,
which is the entire reason this marketplace exists.

## Act 3: the real disease

The redesign session surfaced something bigger than delivery mechanics. Gabe's
actual complaint was never that the agent broke the rules. It was that the
prose following the rules was unreadable:

> Its parlay slip was replaced, but the single-bet cascade still backs the
> Evaluate button on five game pages.

His verdict: it "reads like an out of work professor trying to sound more
intelligent in a grant proposal." He kept having to reply "can you break that
down for me in plain english."

Two background agents mined 72 real sentences from session transcripts, audit
reports, and PR bodies. Gabe confirmed six failure patterns:

| Pattern | Real example, mined from output |
|---|---|
| Invented shorthand noun | "the single-bet cascade", "the totals complex", "the one-vote floor" |
| Abstract verb | "the unanimity, EV-at-price, and edge-cap gates carry the safety margin" |
| Verbless note-compression | "Kelly display units retired. Every pick grades flat 1u; the badge carries strength." |
| Overpacked sentence | a 143-word audit sentence chaining eleven findings through semicolons |
| Fragment verdict | "The diagnosis holds." / "One reframe." / "Gates. Unchanged, deliberately..." |
| Coined abstraction | "ambient context", "performance gradient", "the silent config-vs-production divergence channel" |

The old eleven rules caused this. Every one of them pushed compression (cut
packaging, land each fact once, stop at the last fact) and nothing pushed
back. Prose optimized for fewest tokens reads like a
grant proposal. The verbosity complaint and the density complaint were the
same complaint, total effort to read, arriving from opposite directions.

So the rebuild replaced the budget. The rules now manage the reader's effort,
which prose overspends two ways: density (too much per sentence, the reader
decodes) and padding (sentences delivering nothing new, the reader wades).
The fourteen rules and their carve-outs live in
[RULES.md](../plugins/gborges-standard/skills/writing-voice/RULES.md), with
the mined sentences rewritten in
[EXAMPLES.md](../plugins/gborges-standard/skills/writing-voice/EXAMPLES.md)
and the vocabulary pinned in [CONTEXT.md](../CONTEXT.md).

## What shipped

[PR #9](https://github.com/gborges0727/claude-plugins/pull/9), version 1.6.0:

- The Plain English output style, forced on wherever the plugin is enabled,
  with Claude Code's coding behavior kept.
- The session-start hook, CONVENTIONS.md, and the /plain-english command
  deleted. The style carries what they carried, and plain is the default
  register now.
- The writing-voice skill slimmed to a document ritual: two passes on a draft
  file, for file deliverables only. Chat is the style's job.
- check.py renumbered to the new rules, taught to flag sentences over 30
  words as advisory re-read risks, and taught to mask table rows like code.

Alongside it: FairLine's CLAUDE.md paragraph re-pointed at the style,
`~/.claude/CLAUDE.md` trimmed to the signing keys alone, and two stale hand
copies under `~/.claude/skills/` deleted.

## The ceiling

A fresh session answering the original test question produced clean, plain
output, verified against the mined patterns. Two residues survived: a
subject-less fragment and an explaining colon. Asked why the colon slipped
through, the old session explained that a style moves odds rather than
guaranteeing outcomes. Absolute bans hold (the em dash, one character, no
carve-out, zero appearances). Judgment rules leak, because a colon that
introduces a label is legal and the model can talk itself into the legal
reading. Then, mid-explanation, the old session wrote "So the honest
ceiling:" and committed the exact tic it was explaining.

That's the state of the system. The style fixed the failures the old
rules were causing. What remains is the model's own habit, suppressed
per-sentence, slipping through occasionally. Documents get the mechanical
pass as a backstop. Chat gets good odds. Nothing gets certainty.
