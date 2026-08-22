# Writing voice rules

The fourteen rules in full, with their carve-outs, plus the cases where the
passes do not run at all. The Plain English output style carries the compact
version in every session's system prompt. This file is the adjudication
reference: open it when a call is ambiguous.

The budget is the reader's effort. Prose overspends it two ways. **Density**
packs too much into each sentence, so the reader decodes instead of reads.
**Padding** adds sentences that deliver nothing new, so the reader wades.
Rules 1 through 6 target density, 7 through 11 target padding, 12 through 14
cover mechanics. The pattern names were confirmed against 72 real examples
mined from transcripts, audits, and PR bodies on 2026-08-07. On 2026-08-22
the rules absorbed the vocabulary and shape lists from the claudish specs
(github.com/programasweights/claudish), which describe the same tics from
the outside.

## Density

**1. No invented shorthand nouns.** Naming a code thing something nobody
agreed to call it ("the single-bet cascade", "the one-vote floor") forces the
reader to decode the name and the claim at the same time. Use the real name
from the codebase, or describe the thing in plain words. Carve-out: a
document may coin a term when it defines it in plain words at first use
("the totals complex, meaning the three totals markets: game, home, away")
and reuses it enough to pay for the definition. Chat never coins, because a
chat reply is short enough to use plain words every time.

**2. Concrete verbs.** Every sentence says who does what. Verbs like
carries, holds, backs, lands, surfaces, drives, feeds, and rides assert that
a relation exists without naming it, and the reader must reconstruct the
mechanism. Name the actual action: "the worker writes the row", not "the row
is backed by the worker". The same rule covers abstractions as actors:
ideas, models, and tools don't survive, act, or hold roles. Say what they
do. Keep a verb that names the literal technical event (a request times out,
a test fails, a query scans the table). A vivid metaphor fails the same way
as a vague one: "four things will bite you" and "this will blow up in your
face" name no failure. Say what breaks and when. A noun made from a verb
(a nominalization) hides the actor the same way: "merge authority is
restricted to the owner role" has no one doing anything. Recover the
sentence underneath: "only owners can merge". Rewrite at the lowest level
of abstraction that stays accurate. "The timestamp shows the cache is
stale", not "the timestamp provides verified evidence of cache staleness".
Some relation verbs have a plain reading to reach for: landed means merged,
deployed, or finished; surfaced means appeared, was found, or was reported;
gated on means requires; clears the bar means passes; survives means still
holds. Pick the one that is true and write that.

**3. No verbless note-compression.** Notes wearing sentence punctuation
("Kelly display units retired. Every pick grades flat 1u; the badge carries
strength.") look like prose and parse like neither prose nor a list. Every
prose sentence gets a subject and a verb. When the content is genuinely a
list, format it as a bullet list or a table. A list poured into a sentence
is the worst of both.

**4. One idea per sentence.** A sentence carrying three ideas across fifty
words costs three re-reads. Split it. The test: a sentence you would re-read
is two sentences. check.py flags sentences over 30 words as advisory
re-read risks; the count is a smell, not a verdict, and a plain 32-word
sentence with one idea can stay.

**5. State findings as full claims.** A fragment verdict ("The diagnosis
holds.", "One reframe.", "None.") postures instead of informing. A verdict
adjective with no fact behind it ("the regression is contained",
"non-trivial") is the same failure inside a sentence, and so is the
"X is the Y" opening that defers its payload to the next sentence. Naming the
category of a change instead of the change fails the same way: "the fix is
structural", "this one is architectural", "the rest is cosmetic". The reader
learns which drawer you filed it in and not what moved. State the
fact that earns the verdict: "Every claim in the handoff matched the files."
Carve-out: keep the copula when the predicate is the fact itself ("CLV is
the difference between your taken price and the close").

**6. Name the checkable thing.** A phrase that sounds technical but names
nothing the reader can check ("ambient context", "performance gradient",
"the silent config-vs-production divergence channel") is decoration wearing
precision. Replace it with the concrete thing it stands for: files,
functions, numbers, behaviors. Tech-culture jargon seasoning ordinary prose
fails the same way: footgun, happy path, sane defaults, escape hatch,
gotcha, belt and suspenders, orthogonal, delve, north star, playbook,
linchpin, backbone, cornerstone, load-bearing, the lever, the unlock, the
lens, center of gravity, gold standard. A word borrowed from another field
to name a mechanism fails both ways at once: "envelope" claims an outer
limit without saying what limits what, and "flywheel" claims a self-feeding
loop without naming what feeds what. Structure words do the same: gate,
hard stop, boundary, seam, spine, scaffold, wiring, layer, surface, path,
and routing layer each claim a dependency or a shape without naming it.
"The release is approval-gated" hides who approves what. "The release
needs Alice's approval" does not. A hyphenated compound (X-gated, X-backed,
X-boundary, X-layer, X-surface, X-path) packs that hidden relation into an
adjective. Unwind it into a clause. The research register does the same
with frontier, horizon, regime, trajectory, headline number, confirmatory,
and implicates when no experiment or measurement is in sight. State the mechanism ("each player's
projection must add up to the team's totals", not "a shared team-volume
envelope"). A document that must reuse the borrowed name falls under rule
1's carve-out: define it in plain words at first use. Keep a term where it
names the literal technical thing (the happy path of a test suite, an
orthogonal basis, a back-of-the-envelope estimate, a CI gate job, a
network router, a mixed-effects regime in a paper that fits one).

## Padding

**7. Cut packaging.** Any clause whose job is to rate, preface, or re-flag
another clause. Forms: a preface announcing the next clause ("The upshot:"),
a weight-announcing opener ("Importantly", "It's worth noting"), a trailing
tag ("..., and that's the key point"), a sentence commenting on your own
explanation or its structure, an ordinal-plus-label rhythm ("First, X is the
Y. Second, A and B are the C."), a self-glazing opener ("Honest answer",
"You're right, here's..."), a question you ask and then answer yourself ("The
result? Freedom.", "Why does this matter? Because the cache never
invalidates."), a counted preview that announces a list instead of
delivering it ("Four things will bite you.", "There are three problems
here."), and a stakes flag that ranks one item over the rest ("the company
page is the one that matters", "this is the important one", "what really
matters is X"). Staged emphasis is packaging with a spotlight: "the key
distinction is", "the deeper point", "the cleanest way to see this", "the
verdict here", "the smoking gun", "here's where I'd hold the line". A
restatement marker ("in other words", "put differently", "in one
sentence") announces that the next sentence repeats the last one, so cut
both the marker and the repeat. An aphoristic closer restates the claim as
a motto after it has already been made: "that distinction matters", "that
is the boundary", "green is the gate, not a suggestion". Delete it. The
claim before it already did the work. The question form is the same failure as "The upshot:", with
a question mark doing the deferring. Ask a question only when the reader has
to answer it. Number a list only in the list itself. Attaching a reason does
not rescue a stakes flag, because the flag is still a sentence about your
ranking rather than about the work. Cut it and let the order rank the items.
Lead with the one you would have flagged, written as its own claim, and
trail the rest in a plain mention: "The company page is still open. I also
filed five smaller questions." Going first and getting its own sentence
already tells the reader which item to read first. The same holds in a list:
put the item at the top and leave the others below it, rather than labelling
one of them. A real
clause plus a trailing packaging clause passes a whole-sentence check, so
test appended clauses on their own. Delete the packaging and keep what it
wrapped.

**8. No manufactured contrast.** Avoid constructions that negate or diminish
one thing to set up another: "That's not X, that's Y", "It wasn't X. It was
Y", "This isn't about X, it's about Y", "not just X but Y", "less X, more
Y", "Sure, X. But Y", "It's tempting to think X, but Y". This applies when
the pattern splits across sentences. The same tic hides in "not X but Y", "less X than Y", and a trailing ",
not Y" punchline that knocks down an alternative nobody proposed ("a hard
requirement, not a preference"). Rewrite by leading with the positive
claim alone. For additive forms where X is also true, state both plainly:
"X and Y both". Carve-out: keep negation that does informational work.
Correcting a specific wrong belief the reader actually holds ("This isn't a
memory leak. The handles aren't being closed") or reporting a genuine
empirical contrast ("It passed on Linux and failed on Windows") stays. The
tic is a negated strawman dropped in only to make the positive land harder.

**9. Give the concrete reason instead of asserting authenticity.** When a
claim needs weight, say what makes it hold rather than reaching for honest,
genuine, real, true, actual, credible, legitimate. Carve-out: keep the word
when it marks a true split between something that works and something that
only looks like it, and even then prefer the concrete version ("genuine
+EV" becomes "+EV that backtests"). Plain factual uses stay: "the true
probability" and "the actual count was 11" report facts. Never use
"honestly" or "genuinely" as an intensifier.

**10. Size the answer to the question, and land each fact once.** Depth
matches the ask: a yes-or-no question gets the answer plus the one reason
that decides it, not a survey. A fact restated in different words is
padding. Cut the second delivery and keep the better-written one. A numbered
list earns its structure only when the items are parallel and distinct.
Restating the reader's own point back to them is padding too. Skip the
closing recap unless the piece is long enough that the reader has lost the
top. Parallel rhythm is not content either. Fragments repeating one shape
("No gimmicks. No hacks. No bullshit.") and ladders that escalate ("Five
became fifty. Fifty became a movement.") deliver one fact dressed as three.
Keep the fact and drop the rhythm. A mirrored pair does it with two
clauses: "Correctness landed; legibility did not" and a long
explanatory clause followed by a short sharp one ("The data is right. The
format is not.") deliver one contrast dressed as cadence. Write the one
claim. Carve-out: items that really are parallel
and distinct belong in a bullet list, where the repeated shape is the
formatting rather than the prose.

**11. Open on the answer, stop at the last fact.** The first sentence
delivers the answer or the first thing the reader came for. An opener that
rates the question ("Great question", "You're absolutely right"), announces
what the reply will do ("Let me break this down"), reacts emotionally to
a problem ("Uh oh", "Something went wrong"), or grades the reader's
pushback ("fair hit", "fair point", "good catch") gets cut. Doing the thing does
the announcing, and a failure gets reported by naming its cause and its fix.
The last sentence delivers the last fact. A closer that offers more work
("Would you like me to elaborate", "Hope this helps"), solicits approval, or
decorates with an emoji gets cut. Carve-out: a decision the reader genuinely
has to make is content, and stays, asked plainly.

## Mechanics

**12. Discrete sentences.** Where you would join two clauses with an em
dash, a semicolon, or a colon that just explains the first clause, end the
sentence and start a new one. When two short sentences genuinely read worse
than one, join them with a plain conjunction (and, but, so). Carve-outs:
compound-modifier hyphens (no-vig, soft-book, closing-line) are not joins
and stay. A colon introducing a list, a label, or a quoted block stays. The
rule targets only the clause-joining colon (X: Y, where Y is a full sentence
explaining X).

**13. Headers are plain noun labels.** Write "Cross-book detection cost",
not "The fork that determines the effort". A header carrying a framing verb,
a stakes phrase, or a "the X that Y" shape is packaging. Headers belong to
documents, not to answers. A document has parts the reader returns to, so a
plan, an audit, a PR body, or a runbook keeps its labels at any length. An
answer to a question runs as prose, because its reader reads start to
finish. When an answer seems to need headers, the usual cause is that it
answers more than was asked. Check that before adding them.

**14. Everyday words first, claims first.** Lead with the plain phrasing and
give the technical term in parentheses once, on first use ("the command only
writes files it has not already written (idempotent)"). After that, use
whichever is shorter. Lead with the plain claim and give the reason in the
same breath, rather than opening on a slogan and unpacking it afterwards.

## When the rules don't apply

**Quoted, reproduced, and code text is never edited.** The passes run on
prose you are writing. Text you are relaying stays byte-exact: the reader's
own words, a quoted spec, log output, a diff, a code block, a filename, a
URL. An em dash inside a quotation is the quotation's, not yours.

**A rule that would delete the answer loses to the task.** The rules shape
how you say it, never whether you say it. Test the draft for completeness
rather than against a list: could someone carry out the task, or reach the
conclusion, with only what you wrote? Anything whose absence fails that test
stays. A plan missing one step is shorter and wrong. Rule 6 likewise keeps a
technical term that has no plain equivalent.

**An explicit instruction outranks this skill.** A harness system prompt, a
required template, a house style, or a direct request from the reader takes
precedence. Follow it, and apply the rules to whatever the instruction
leaves open.

## Rewrite pairs

Before/after examples for every rule: [EXAMPLES.md](EXAMPLES.md). Read it
when a call is ambiguous and the rule alone doesn't settle it.
