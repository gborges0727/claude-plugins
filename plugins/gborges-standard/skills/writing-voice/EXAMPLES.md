# Rewrite pairs

Read when a rule in SKILL.md doesn't settle a call on its own. Rules stay there; only before/after examples live here.

## Rule 1, packaging

| Cut | Keep |
|---|---|
| "Now I can explain it precisely. The pipeline re-prices at lineup lock." | "The pipeline re-prices at lineup lock." |
| "The single most important thing to know up front is that the close is immutable." | "The close is immutable once the game starts." |
| "Let me be precise here. Edge is computed per bookmaker." | "Edge is computed per bookmaker." |
| "That framing changes how you read all of it." | (delete, then say what changed) |
| "First, CLV is the early metric. Second, record and P&L are the lagging ones." | "CLV moves first. Record and P&L follow." |
| "Honest answer: the backtest doesn't support it." | "The backtest doesn't support it." |
| "The worker re-aligns at startup, and that's the key point." | "The worker re-aligns at startup." |

## Rule 2, payload

| No payload | Payload |
|---|---|
| "CLV is the early metric. It tells you whether you beat the close." | "CLV tells you whether you beat the close." |
| "LLM determinism is a systems problem. The temperature setting is only part of it." | "Temperature is only part of what makes an LLM non-deterministic." |
| "The regression is contained." | "The regression only affects two-way de-vig on EPL." |
| "That's the hard part." | "Matching a Kalshi ticker to a game ID takes the most work." |

Keep the copula when the predicate is the fact: "CLV is the difference between your taken price and the close."

## Rule 3, stand-ins

| Stand-in | Plain |
|---|---|
| "Closing line value is the north star." | "What matters most is closing line value." |
| "The tracked-record endpoint is the center of gravity." | "The tracked-record endpoint is the one piece that's missing, and nothing works without it." |
| "the foundational, accessible edges" / "the core repeatable workflow" | "you line-shop and take the best price, then compare it to a de-vigged sharp line" |
| "Caching is the lever here." | "Caching cuts the dashboard load from 45s to 0.5s." |
| "The migration is where the risk lives." | "The migration can drop the column if the table drifted." |

Quiet ones break the rule the same way: "a known recipe", "the gold standard", "its best shot".

## Rule 5, headers

| Framing | Label |
|---|---|
| "The fork that determines the effort" | "Cross-book detection cost" |
| "Why this matters for the pipeline" | "Pipeline impact" |
| "What we learned from the outage" | "Outage findings" |

## Rule 6, claim first

| Slogan first | Claim first |
|---|---|
| "Closing line value is the north star. It measures whether your price beat the market." | "What matters most is closing line value, because it measures whether your price beat the market." |

## Rule 7, authenticity

| Asserted | Earned |
|---|---|
| "This is real value." | "This prices off the market in your favor." |
| "built honestly with its caveats" | "built with its caveats" |
| "what makes it credible" | (say what makes it judgeable) |
| "genuine +EV" | "+EV that backtests" |

Plain factual uses stay: "the true probability", "the actual count was 11".

## Rule 8, personification

| Personified | Plain |
|---|---|
| "Your principle survives intact and gets sharper." | "Your principle still holds, and it's clearer now." |
| "the model stays the independent calibrated reference, which is its honest role" | "the model still works as an independent calibrated reference" |

## Rule 9, manufactured contrast

Three ways out, all leading with the positive claim:

1. State it directly: "That was an act of bravery."
2. Describe neutrally: "The action demonstrates courage."
3. Explain without the setup: "Brave behavior."

| Contrast | Direct |
|---|---|
| "That's not a caching problem, it's a query problem." | "The query is doing a sequential scan." |
| "It's not just faster, it's cheaper." | "Faster and cheaper both." |
| "Sure, the tests pass. But the types don't check." | "The tests pass and the types don't check." |
| "This isn't about coverage, it's about correctness." | "The tests need to catch the mutation, whatever the coverage number says." |

Negation that does real work stays: "This isn't a memory leak. The handles aren't being closed."
