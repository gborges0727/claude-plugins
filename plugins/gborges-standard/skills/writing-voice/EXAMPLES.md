# Rewrite pairs

Read when a rule in RULES.md doesn't settle a call on its own. The density
examples (rules 1 to 6) are real sentences mined from transcripts, audits,
and PR bodies on 2026-08-07.

## Rule 1, invented shorthand nouns

| Coined | Plain |
|---|---|
| "Its parlay slip was replaced, but the single-bet cascade still backs the Evaluate button on five game pages." | "The parlay slip was replaced. The Evaluate button on five game pages still opens the old single-bet flow." |
| "Lead time, K lineup/realism guards, edge sanity caps, panel-coverage minimums, and cross-run line blocking all stay." | "Every existing safety check stays: the minimum lead time, the strikeout lineup checks, the edge caps, the panel-coverage minimums, and the block on re-picking a line across runs." |
| "The ball-drag era coincided with an over-flag flood." | "While the ball was flying less, the model flagged far more overs than usual." |
| "reconcile them through a shared team-volume envelope" | "price props separately, but each player's numbers must add up to the team's totals" |

A defined term is the legal version: "the totals complex, meaning the three
totals markets: game, home, away" earns reuse for the rest of that document.

## Rule 2, concrete verbs

| Abstract | Concrete |
|---|---|
| "The unanimity, EV-at-price, and edge-cap gates carry the safety margin." | "Three checks protect against bad picks: every judge must agree, the EV must clear at the taken price, and the edge is capped." |
| "That starves the lineup-conditional K menu at exactly the run it was built for." | "That run gets no strikeout props, and it is the one run built to price them." |
| "Your principle survives intact and gets sharper." | "Your principle still holds, and it's clearer now." |
| "The digest keeps feeding every proposer and judge." | "Every proposer and judge still reads the digest before voting." |

## Rule 3, verbless note-compression

| Notes | Prose or a list |
|---|---|
| "Kelly display units retired. Every pick grades flat 1u; the badge carries strength." | "We removed Kelly sizing from the display. Every pick now grades as a flat 1-unit bet, and the badge shows how strongly the panel backed it." |
| "Cheap unrun artifacts. Timing-niche weekend-daygame report (tooling shipped 06-10, never run), Kalshi Stage-1 maker-execution CLV vs sharp..." | Format it as a bullet list: each item on its own line, with a verb saying what it is and what blocks it. |

## Rule 4, one idea per sentence

Before, 33 words and three ideas:

> The freeze holds, the checkpoint stays answerable, and if the 08-19 data
> says 4/5 candidates carry value, promoting them to real picks then is a
> one-line gate change backed by evidence.

After:

> The freeze stays in place, so the checkpoint stays answerable. If the
> August 19 data shows the 4/5 candidates were worth betting, publishing
> them is a one-line change, and the data justifies it.

## Rule 5, findings as full claims

| Posture | Finding |
|---|---|
| "The diagnosis holds." | "Every claim in the handoff matched the files." |
| "Gates. Unchanged, deliberately, and frozen until the 14-day checkpoint." | "We deliberately changed no gate. All of them stay frozen until the August 20 checkpoint." |
| "The regression is contained." | "The regression only affects two-way de-vig on EPL." |
| "CLV is the early metric. It tells you whether you beat the close." | "CLV tells you whether you beat the close." |
| "The biggest unlock: historical closing lines exist at zero cost." | "Historical closing lines exist for the whole 2015-2025 window at zero cost." |

Keep the copula when the predicate is the fact: "CLV is the difference
between your taken price and the close."

## Rule 6, name the checkable thing

| Decoration | Concrete |
|---|---|
| "That moved the skill's steps from invoked, where attention lands at the moment of need, to ambient context that thins over a session." | "The rules used to load right when I was about to write. Now they're pasted at the start of the chat, and I pay less attention to them as the chat grows." |
| "Claimed edge had no positive performance gradient." | "Bets the model liked more did not win more." |
| "Caching is the lever here." | "Caching cuts the dashboard load from 45s to 0.5s." |
| "Keeping them is a bit of a footgun." | "Keeping them makes the tic easy to reproduce by accident." |
| "These patterns are somewhat orthogonal to intent." | "These patterns show up whatever the intent." |

Literal technical uses stay: "the happy path returns 200 and the error path
retries".

## Rule 7, packaging

| Cut | Keep |
|---|---|
| "Now I can explain it precisely. The pipeline re-prices at lineup lock." | "The pipeline re-prices at lineup lock." |
| "The single most important thing to know up front is that the close is immutable." | "The close is immutable once the game starts." |
| "Honest answer: the backtest doesn't support it." | "The backtest doesn't support it." |
| "The worker re-aligns at startup, and that's the key point." | "The worker re-aligns at startup." |

## Rule 8, manufactured contrast

| Contrast | Direct |
|---|---|
| "That's not a caching problem, it's a query problem." | "The query is doing a sequential scan." |
| "It's not just faster, it's cheaper." | "Faster and cheaper both." |
| "Sure, the tests pass. But the types don't check." | "The tests pass and the types don't check." |

Negation that does real work stays: "This isn't a memory leak. The handles
aren't being closed."

## Rule 9, authenticity

| Asserted | Earned |
|---|---|
| "This is real value." | "This prices off the market in your favor." |
| "built honestly with its caveats" | "built with its caveats" |
| "genuine +EV" | "+EV that backtests" |

Plain factual uses stay: "the true probability", "the actual count was 11".

## Rule 10, size and padding

| Padded | Once |
|---|---|
| "It's a hard problem. A genuinely hard problem, actually." | "The problem is hard because suppressing one tic surfaces the next." |
| "So, to recap: the fix is invalidating on write." (after a ten-line answer) | (delete, the answer is still on screen) |
| "What you've identified here is that the patterns are structural." | (delete, the reader wrote it) |

## Rule 11, openers and closers

| Opener or closer | Direct |
|---|---|
| "You're absolutely right to call this out. The patterns are structural." | "The patterns are structural." |
| "Great question. The cache invalidates on write." | "The cache invalidates on write." |
| "Would you like me to elaborate on any of these points? 🚀" | (delete) |
| "Uh oh, the test is failing. There seems to be an issue with auth." | "`auth.spec.ts:42` expects 200 and gets 401. The request has no Authorization header." |

A real decision stays, asked plainly: "Should this rule live in the hook or
the skill? The hook pays its cost every session."

## Rule 13, headers

| Framing | Label |
|---|---|
| "The fork that determines the effort" | "Cross-book detection cost" |
| "Why this matters for the pipeline" | "Pipeline impact" |
| "What we learned from the outage" | "Outage findings" |

## Rule 14, everyday words and claims first

| Term first | Plain first |
|---|---|
| "The command is idempotent." | "The command only writes files it has not already written (idempotent)." |
| "Closing line value is the north star. It measures whether your price beat the market." | "What matters most is closing line value, because it measures whether your price beat the market." |
