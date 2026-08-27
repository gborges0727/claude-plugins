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
| "Four things will bite you." | "Four things break, all of them at import time." (then list them) |
| "Merge authority is restricted to the owner role." | "Only owners can merge." |
| "The timestamp provides verified evidence of cache staleness." | "The timestamp shows the cache is stale." |
| "The fix landed cleanly on the routing layer." | "The fix merged, and the request handler now routes by tenant id." |

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
| "The fix is structural." | "You reorder the items now instead of labelling one of them." |
| "The rest of the diff is cosmetic." | "The rest of the diff renames two variables." |

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
| "The envelope keeps decision 2's parallel tracks alive and survives a game-model slip." | "Pricing players as shares of team totals lets the two tracks build in parallel, and props still price if the game model slips." |
| "The attack on the envelope: its Week 1 game-script tilt is neutral." | "The team-totals approach is weak in Week 1. It projects pace from last season with no margin input, so props are priced blind to the matchup." |

Literal technical uses stay: "the happy path returns 200 and the error path
retries", "a back-of-the-envelope estimate".

## Rule 6, name the checkable thing (continued)

| Structure word | Named relation |
|---|---|
| "The release path is approval-gated." | "The release needs Alice's approval." |
| "Passing tests is a hard gate." | "Do not launch until the tests pass." |
| "The worker is the spine of the pipeline." | "Every stage reads its input from the worker's output table." |
| "The headline number survives scrutiny." | "The 12% figure held when we re-ran it on the holdout set." |

## Rule 7, packaging

| Cut | Keep |
|---|---|
| "Here's where I'd hold the line: do not launch until the tests pass. Green is the gate, not a suggestion." | "Do not launch until the tests pass." |
| "The key distinction is that the cache never invalidates." | "The cache never invalidates." |
| "The cache never invalidates. In other words, every read after the first is stale." | "Every read after the first returns the stale value, because the cache never invalidates." |
| "Only owners can merge. That distinction matters." | "Only owners can merge." |
| "Now I can explain it precisely. The pipeline re-prices at lineup lock." | "The pipeline re-prices at lineup lock." |
| "The single most important thing to know up front is that the close is immutable." | "The close is immutable once the game starts." |
| "Honest answer: the backtest doesn't support it." | "The backtest doesn't support it." |
| "The worker re-aligns at startup, and that's the key point." | "The worker re-aligns at startup." |
| "Why does this matter? Because the cache never invalidates." | "The cache never invalidates." |
| "The result? A 40x speedup." | "The dashboard loads in 0.5s instead of 20s." |
| "There are three problems here. First, ..." | "The parser drops trailing commas." (then the other two) |
| "Six items are open, and the company page is the one that matters." | "The company page is still open. I also filed five smaller questions." |
| "I found one critical bug and five minor ones. The critical one is the important one." | "The token refresh drops the session on retry. I also filed five smaller bugs." |
| "What really matters is the retry limit." | "The retry limit caps the job at 3 attempts." |

A question the reader must actually answer stays: "Should this rule live in
the hook or the skill?"

## Rule 8, manufactured contrast

| Contrast | Direct |
|---|---|
| "That's not a caching problem, it's a query problem." | "The query is doing a sequential scan." |
| "It's not just faster, it's cheaper." | "Faster and cheaper both." |
| "Sure, the tests pass. But the types don't check." | "The tests pass and the types don't check." |
| "This is less a bug than a design choice." | "The author chose this. The ticket that added it explains why." |
| "Not a caching problem but a query problem." | "The query does a sequential scan." |

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
| "No gimmicks. No hacks. No filler." | "The script only reports strings it matched." |
| "One check became five. Five became the whole suite." | "The suite grew from one check to twelve." |

## Rule 10, size and padding (continued)

| Mirrored | One claim |
|---|---|
| "Correctness landed; legibility did not." | "The output is correct and hard to read." |
| "The honest shape is asymmetric: the data is correct; the format is hard to read." | "The data is correct and the format is hard to read." |

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

## Rule 15, say what it does, then name it

| Name first | Plain first |
|---|---|
| "The change is in `remind-writing-rules.py`." | "The hook that re-sends the writing reminder on every message, `remind-writing-rules.py`, now reads the new section." |
| "The cache was stale." | "Redis, the shared cache, held the old price for 5 minutes." |
| "See `coupon.js` for the currency handling." | "`coupon.js` treats flat amounts as USD." |
| "The run took about as long as last time." | "The run took 3.2 seconds. Last time took 3.1." |
| "The rev needs bumping in the usual two places." | "The rev goes from 18 to 19 in `README.md` and `scripts/cloud-bootstrap.sh`." |

## Rule 16, where things stand

| Path | State |
|---|---|
| "I first checked the hook config, which looked fine, then ruled out the matcher, and finally found that the script path was relative." | "The hook script path was relative, so the hook never ran. It is absolute now." |
| Two bullets, "The build passes" and "The lint passes." | "The build and the lint both pass." |
| "All 214 tests in the pricing, checkout, and auth suites pass, with pricing taking 1.1s, checkout 1.4s, and auth 0.7s." | "All 214 tests pass in 3.2s." |
