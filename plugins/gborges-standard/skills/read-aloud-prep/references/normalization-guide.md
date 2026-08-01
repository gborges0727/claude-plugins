# Normalization Guide

The full catalog of how to turn written elements into spoken English for an AI narrator. `SKILL.md` carries the workflow and the locked conventions. This file is where every transformation lives, along with the trickier judgment calls.

## Contents

1. How to approach a formula
2. Math operators and relations
3. Powers, roots, fractions, subscripts, superscripts
4. Greek letters
5. Calculus and the big operators
6. Set theory and logic
7. Statistics and probability
8. Vectors, matrices, norms
9. LaTeX command cleanup
10. Symbols and special characters
11. Money and currency
12. Numbers, decimals, large quantities
13. Percentages, ratios, ranges
14. Dates, times, years, quarters
15. Units of measurement
16. Roman numerals and ordinals
17. Abbreviations and acronyms
18. Structure: headings, lists, tables, code, quotes, citations, links, figures
19. Antithesis: rewriting negation-contrast for the voice
20. Cleaning up PDF extraction artifacts
21. Worked examples

---

## 1. How to approach a formula

A formula is a sentence written in shorthand. Your task is to recover the sentence. Read it the way the author would read it to a colleague over the phone, left to right, naming each part.

Two strategies, chosen by density:

- **Short or moderate formulas: read them in full.** "x equals negative b plus or minus the square root of b squared minus four a c, all over two a." A listener can follow this.
- **Long or deeply nested formulas: say what it computes, then the key parts.** A listener cannot hold a forty-symbol string in their head. For something like a long likelihood function, say "the log-likelihood is the sum over all observations of the log of the predicted probability for the actual outcome," which is what the symbols mean, instead of reciting every subscript. Use judgment about where the line sits; the goal is that the listener understands the formula's role.

Group with spoken parentheses when grouping matters. "All over two a" and "the quantity x minus mu, squared" tell the ear where the boundaries are.

## 2. Math operators and relations

| Symbol | Spoken |
|---|---|
| `+` | plus |
| `−` `-` | minus |
| `×` `*` `·` | times |
| `÷` `/` | divided by, or over |
| `=` | equals |
| `≠` | does not equal |
| `≈` | approximately equals, or about |
| `≡` | is equivalent to |
| `<` | less than |
| `>` | greater than |
| `≤` | less than or equal to |
| `≥` | greater than or equal to |
| `±` | plus or minus |
| `∓` | minus or plus |
| `∝` | is proportional to |
| `∞` | infinity |
| `→` | approaches, or goes to (in math); to, or leads to (in prose) |
| `⇒` | implies |
| `∴` | therefore |
| `∵` | because |

## 3. Powers, roots, fractions, subscripts, superscripts

- `x^2` "x squared"; `x^3` "x cubed"; `x^n` "x to the power of n"; `2^10` "two to the tenth"; `e^x` "e to the x"; `10^-6` "ten to the negative six."
- `√x` "the square root of x"; `∛x` "the cube root of x"; `ⁿ√x` "the nth root of x."
- Simple fractions: `a/b` "a over b"; `1/2` "one half"; `3/4` "three quarters"; `1/n` "one over n."
- Mixed display fractions like a stacked numerator and denominator: read "the quantity ... over the quantity ...," naming each part.
- Subscripts as labels: `x_1` "x one"; `x_i` "x sub i"; `a_{ij}` "a sub i j"; `H_0` "H naught" (null hypothesis) or "H zero." Use "sub" when a bare reading would be ambiguous.
- `n!` "n factorial."
- `|x|` "the absolute value of x."
- `⌊x⌋` "the floor of x"; `⌈x⌉` "the ceiling of x."

## 4. Greek letters

Spell the name. Capitals are usually said the same as lowercase unless the capital has a standard meaning (noted below).

alpha α, beta β, gamma γ, delta δ (capital Δ often "the change in"), epsilon ε, zeta ζ, eta η, theta θ, iota ι, kappa κ, lambda λ, mu μ (often "the mean"), nu ν, xi ξ, omicron ο, pi π (the number "pi"; capital Π "the product of"), rho ρ, sigma σ (capital Σ "the sum of"; lowercase σ often "the standard deviation"), tau τ, upsilon υ, phi φ, chi χ (as in "chi squared"), psi ψ, omega ω.

## 5. Calculus and the big operators

- Summation: `Σ` "the sum of"; `∑_{i=1}^{n} a_i` "the sum from i equals one to n of a sub i."
- Product: `∏_{i=1}^{n}` "the product from i equals one to n."
- Integral: `∫ f(x) dx` "the integral of f of x with respect to x"; `∫_a^b` "the integral from a to b"; `∬` "the double integral"; `∮` "the contour integral."
- Limit: `lim_{x→0}` "the limit as x approaches zero."
- Derivatives: `dy/dx` "the derivative of y with respect to x"; `d²y/dx²` "the second derivative of y with respect to x"; `∂f/∂x` "the partial derivative of f with respect to x"; `f'(x)` "f prime of x"; `f''(x)` "f double prime of x"; `ẋ` "x dot."
- `∇` "del," or "the gradient"; `∇²` "the Laplacian."
- Functions read by name: `log` "log," `ln` "the natural log," `sin` "sine," `cos` "cosine," `tan` "tangent," `exp(x)` "e to the x" or "the exponential of x."

## 6. Set theory and logic

- `∈` "is in," or "is an element of"; `∉` "is not in"; `⊂` "is a subset of"; `⊆` "is a subset of or equal to"; `∪` "union"; `∩` "intersection"; `∅` "the empty set"; `\` (set minus) "minus."
- `∀` "for all"; `∃` "there exists"; `∄` "there does not exist"; `¬` "not"; `∧` "and"; `∨` "or"; `⊕` "exclusive or."
- `ℝ` "the real numbers"; `ℤ` "the integers"; `ℕ` "the natural numbers"; `ℚ` "the rationals"; `ℂ` "the complex numbers."

## 7. Statistics and probability

- `P(A)` "the probability of A"; `P(A|B)` "the probability of A given B"; `P(A∩B)` "the probability of A and B."
- `E[X]` "the expected value of X"; `Var(X)` "the variance of X"; `Cov(X,Y)` "the covariance of X and Y"; `SD` "the standard deviation"; `SE` "the standard error."
- `x̄` "x bar" or "the mean of x"; `μ` "the mean"; `σ` "the standard deviation"; `σ²` "the variance"; `ρ` "the correlation"; `r` "the correlation coefficient"; `R²` "R squared."
- `X ~ N(μ, σ²)` "X is distributed normally with mean mu and variance sigma squared"; `~ Binomial(n, p)` "is distributed binomially with n trials and probability p."
- `H_0` "the null hypothesis"; `H_1` or `H_a` "the alternative hypothesis."
- `p < 0.05` "p less than zero point zero five"; `p = 0.001` "p equals zero point zero zero one"; `95% CI` "the ninety five percent confidence interval"; `[1.2, 3.4]` as an interval "from one point two to three point four."
- `χ²` "chi squared"; `t` "the t statistic"; `F` "the F statistic"; `z` "the z score."

## 8. Vectors, matrices, norms

- A bold or arrowed vector: "the vector x." `v⃗` "vector v."
- `‖x‖` "the norm of x"; `‖x‖₂` "the L two norm of x"; `|A|` or `det(A)` "the determinant of A"; `Aᵀ` "A transpose"; `A⁻¹` "A inverse."
- `⟨u, v⟩` or `u · v` "the dot product of u and v"; `u × v` "the cross product of u and v."
- Describe an actual matrix in prose rather than reading the bracket layout: "a two by two matrix with rows one, two and three, four." For a large matrix, say what it represents.

## 9. LaTeX command cleanup

Source text often arrives with raw LaTeX. Strip the delimiters `$...$`, `$$...$$`, `\(...\)`, `\[...\]`, and convert the commands:

`\frac{a}{b}` "a over b"; `\sqrt{x}` "the square root of x"; `\sum` "the sum of"; `\int` "the integral of"; `\prod` "the product of"; `\lim` "the limit of"; `\partial` "the partial derivative"; `\nabla` "del"; `\infty` "infinity"; `\times` "times"; `\cdot` "times"; `\div` "divided by"; `\pm` "plus or minus"; `\leq` "less than or equal to"; `\geq` "greater than or equal to"; `\neq` "does not equal"; `\approx` "approximately"; `\equiv` "is equivalent to"; `\in` "is in"; `\forall` "for all"; `\exists` "there exists"; `\rightarrow` "to"; `\Rightarrow` "implies"; `\hat{x}` "x hat"; `\bar{x}` "x bar"; `\vec{x}` "vector x"; `\dot{x}` "x dot"; `\alpha` ... "alpha" and so on for all Greek; `\mathbb{R}` "the real numbers"; `\mathrm{...}` and `\text{...}` just keep the text inside; `\left` and `\right` are spacing hints, so drop them; `\,` `\;` `\quad` are spaces, so drop them. Subscripts `_{...}` and superscripts `^{...}` follow sections 3 and 7.

## 10. Symbols and special characters

| Symbol | Spoken |
|---|---|
| `%` | percent |
| `‰` | per mille |
| `&` | and |
| `@` | at |
| `#` | number (as a prefix, `#1` "number one") or "hash" in a tag |
| `*` | usually drop (emphasis or footnote marker) |
| `°` | degrees |
| `′` | minutes, or feet |
| `″` | seconds, or inches |
| `~` | around, or approximately |
| `^` | "to the power of" in math; otherwise drop |
| `\|` | drop (table pipe), or "or" if it is a logical or |
| `_` | drop (underscore) |
| `§` | section |
| `¶` | paragraph |
| `©` | copyright |
| `®` | registered trademark |
| `™` | trademark |
| `†` `‡` | drop (footnote daggers) |
| `•` `▪` `‣` | drop the bullet glyph and keep the item as a list entry |
| `…` | "and so on," or a trailing pause |
| `–` (en dash) | "to" in a range, otherwise a pause |
| `—` (em dash) | a pause, often a comma in speech |
| `/` | "or" in "and/or" → "and or"; "per" in units; "slash" only when it is literally being named |

## 11. Money and currency

- `$5` "five dollars"; `$5.99` "five dollars and ninety nine cents"; `$1,250` "one thousand two hundred fifty dollars."
- Scaled: `$5M` "five million dollars"; `$1.3B` "one point three billion dollars"; `$750K` "seven hundred fifty thousand dollars."
- Other symbols: `€` "euros," `£` "pounds," `¥` "yen," `¢` "cents." Place the unit after the amount in speech: `£20` "twenty pounds."
- Currency codes: `USD` "U S dollars" or just "dollars," `GBP` "pounds," `EUR` "euros."

## 12. Numbers, decimals, large quantities

- Decimals: `3.14` "three point one four"; `0.5` "zero point five"; `0.05` "zero point zero five." Keep the leading "zero" for clarity.
- Large round numbers spoken naturally: `1,000,000` "one million"; `2.5 billion` "two point five billion."
- Abbreviated magnitudes: `1k` "one thousand"; `5M` "five million"; `2bn` "two billion."
- Negative: `-7` "negative seven."
- A number that is an identifier (a model number, a code) can be read digit by digit if that is how a person would say it: `Room 204` "room two oh four"; `Flight 1198` "flight eleven ninety eight."

## 13. Percentages, ratios, ranges

- `12.5%` "twelve and a half percent"; `100%` "one hundred percent"; `0.3%` "zero point three percent."
- **Round for the ear.** A listener cannot hold a two-decimal percentage, and a run of them is worse. Round awkward percentages to a whole number and mark the approximation: `18.69%` becomes "around nineteen percent," `9.1%` "about nine percent," `4.8%` "roughly five percent." Keep an exact figure only where the precise value is the actual point, and even then prefer a clean spoken form: `52.38%`, the break-even at minus one ten, becomes "just over fifty two percent," and `54.55%` becomes "just under fifty five percent." A half is easy to say, so `12.5%` can stay "twelve and a half percent," but two decimal places almost never survive being heard. Awkward small decimals get the same treatment: `0.10` of a point is "a tenth of a point," `0.25` is "a quarter."
- Ratios: `3:1` "three to one"; `16:9` "sixteen to nine."
- Sports scores: `2-0` "two nil" or "two to zero" depending on the sport.
- Numeric ranges: `5–10` "five to ten"; `2019–2024` "twenty nineteen to twenty twenty four"; `pp. 12–15` "pages twelve to fifteen."
- Odds: `+150` "plus one fifty"; `-110` "minus one ten" (American odds, read as a person would say them at a sportsbook).

## 14. Dates, times, years, quarters

- Years: `1990` "nineteen ninety"; `2008` "two thousand eight"; `2015` "twenty fifteen"; `2000` "two thousand."
- Decades: `1990s` "the nineteen nineties"; `2020s` "the twenty twenties."
- Full dates: `3/14/2025` "March fourteenth, twenty twenty five"; `2025-03-14` "March fourteenth, twenty twenty five"; `14 March 2025` "the fourteenth of March, twenty twenty five." Follow the source's regional order when it is clear.
- Quarters and fiscal: `Q4` "the fourth quarter"; `Q4 2024` "the fourth quarter of twenty twenty four"; `FY23` "fiscal year twenty three."
- Times: `3:30pm` "three thirty p m"; `14:00` "two p m" or "fourteen hundred"; `9am–5pm` "nine a m to five p m."
- `a.m.` "a m"; `p.m.` "p m"; `BCE`/`CE`/`BC`/`AD` spelled as letters.

## 15. Units of measurement

Keep the number joined to the spoken-out unit. Singular or plural follows the number.

- Length: `km` kilometers, `m` meters, `cm` centimeters, `mm` millimeters, `mi` miles, `ft` feet, `in` inches.
- Mass: `kg` kilograms, `g` grams, `mg` milligrams, `lb` pounds, `oz` ounces.
- Volume: `L` liters, `mL` milliliters, `gal` gallons.
- Speed: `mph` "miles per hour," `km/h` "kilometers per hour," `m/s` "meters per second."
- Data: `GB` gigabytes, `MB` megabytes, `KB` kilobytes, `TB` terabytes, `Mbps` "megabits per second."
- Frequency: `Hz` hertz, `kHz` kilohertz, `GHz` gigahertz.
- Temperature: `20°C` "twenty degrees Celsius," `68°F` "sixty eight degrees Fahrenheit," `300K` "three hundred kelvin."
- Examples: `5kg` "five kilograms"; `100m` "one hundred meters"; `2.4GHz` "two point four gigahertz"; `90°` "ninety degrees."

## 16. Roman numerals and ordinals

- Counting numerals: `Chapter IV` "Chapter four"; `Section III` "Section three"; `World War II` "World War Two."
- In a regnal or papal name they are ordinals: `Henry VIII` "Henry the Eighth"; `Louis XIV` "Louis the Fourteenth"; `Pope John Paul II` "Pope John Paul the Second."
- Ordinals: `1st` "first," `2nd` "second," `3rd` "third," `21st` "twenty first," `100th` "one hundredth."

## 17. Abbreviations and acronyms

The locked rule is define once, then full words (see `SKILL.md`). Within that, decide how each term is voiced.

**Initialisms (spell the letters):** FBI, CEO, CFO, API, URL, HTML, GDP, NBA, NFL, ROI, KPI, CLV, EV. The first mention ties the words to the letters once: "expected value, which bettors call E V," then "expected value" after.

**Acronyms (said as a word):** NASA ("nassa"), NATO ("nay-toe"), laser, radar, scuba, PIN. These are read as the word; expand on first use only if the audience may not know the term.

**No expansion needed (universal):** USA, UK, AI, TV, OK, ID, PM/AM. Voice them properly (`vs.` "versus"), but they need no gloss.

**Latin and scholarly:**
`e.g.` "for example"; `i.e.` "that is"; `etc.` "and so on"; `et al.` "and colleagues" or "and others"; `cf.` "compare"; `viz.` "namely"; `vs.` / `v.` "versus"; `N.B.` "note"; `ibid.` and `op. cit.` usually drop in a read-aloud; `approx.` "approximately"; `est.` "estimated"; `no.` / `№` "number"; `vol.` "volume"; `ed.` "edition" or "editor"; `pp.` "pages."

**Titles and addresses:**
`Dr.` "Doctor"; `Mr.` "Mister"; `Mrs.` "Missus"; `Ms.` "Miz"; `Prof.` "Professor"; `Sr.`/`Jr.` "Senior"/"Junior"; `St.` "Saint" or "Street" by context; `Ave.` "Avenue"; `Rd.` "Road"; `Blvd.` "Boulevard"; `Inc.` "Incorporated"; `Ltd.` "Limited"; `Corp.` "Corporation"; `Co.` "Company"; `Dept.` "Department"; `Govt.` "Government."

When a single set of letters could expand two ways, the document's subject decides. If the subject does not decide and the term matters, ask the user.

## 18. Structure: headings, lists, tables, code, quotes, citations, links, figures

**Headings and section breaks.** A narrator reads heading text inline, as one more line with a pause before and after, with none of the visual size or spacing that tells a reader "new section" on the page. So a bare structural label like "Details" or a stranded noun phrase like "Theory and Methods, the Actual Edges" sounds like a fragment dropped between sentences. Two stacked headings, a section title above a subsection title, are worse, since the listener hears two fragments in a row. Write the heading text itself as a natural spoken transition that opens the section, for example "Now to the operational reality, the obstacles that make these edges hard to use," and let it replace any separate transition sentence in the body, so the boundary is stated once. Remove pure wrapper headings that hold no spoken content, and flatten the levels that wrapper was creating. The heading still serves the page and the app for navigation; its words just need to read as speech.

**Lists.** A narrator does not read list markers. The "1." and "2." of a numbered list are silent, and the break between items is only a short pause, so a list of findings or steps blurs into one run of paragraphs and the count is lost on the listener. Carry the enumeration in the words instead: lead each item with a spoken ordinal or transition ("First, ... Second, ..." or "The first finding is ..."). For anything a listener needs to track in sequence or by count, prefer flowing prose with those spoken cues over a visual list. Keep a true list only for short, discrete, order-independent items, and even then, if the count matters, say it. Bullets are silent the same way, so a bulleted list of several substantial points reads better as prose joined by "First ... Also ... Another ... Finally."

**Colons.** The voice treats a colon as a very short pause, shorter than a comma, and it often lands clipped and unnatural. Use colons sparingly. Where a real pause belongs before an explanation, a list, or a payoff, end the sentence with a period and start the next one: write "Here is the logic. As kickoff approaches ..." rather than "The logic: as kickoff approaches ...". A colon inside a heading clips the same way, so prefer a comma or a reworded heading.

**Dense runs of numbers.** Several figures packed into one sentence are hard to follow by ear, because the listener is still holding the first number when the next one arrives. Split them across short sentences, ideally one figure or one statistic per sentence. Turn one long clause carrying two statistics into three sentences: "Take final margins in football. Since two thousand three, around nineteen percent of games have ended with a margin of exactly three points, the most common result of all. Seven points is next, at about nine percent." Pair this with rounding, from section 13, so each number is both isolated and simple.

**Long windups and stranded verbs.** Speech needs the grammatical core early. A sentence that piles a long subject in front of its verb, then closes the subject with a comma, makes the voice pause right before the verb, and the verb lands stranded. "Holding accounts at many books, then comparing prices to find value, is the core workflow" reads fine on the page but stalls aloud. Lead with the main clause instead: "The core workflow is to hold accounts at many books, then compare prices to find value." Keep the subject and verb close, and let the detail trail after.

**Tables.** Convert to prose that preserves the real content. State what the table shows, then voice the rows that carry the point. Example: a table of three models by accuracy and latency becomes "The table compares three models. The transformer reaches ninety four percent accuracy at one hundred twenty milliseconds, the convolutional model ninety one percent at forty milliseconds, and the baseline eighty three percent at ten milliseconds." For a large table, give the structure and the headline figures rather than every cell. Never output pipe-table syntax in the result.

**Code.** Describe what the code does in a sentence or two; do not read syntax aloud. "A short Python function follows that loads the CSV, drops empty rows, and returns the mean of the price column." If a specific value in the code matters to the discussion, mention it in words.

**Block quotes.** Read the quoted text as normal speech. If the fact that it is a quotation matters, introduce it ("as the report puts it, ...") rather than announcing punctuation. Keep attributions.

**Citations and footnotes.** A bracketed number or superscript marker like "[12]" interrupts speech and gets dropped. Where a citation is part of the sentence's meaning, voice it ("Kahneman and Tversky showed in nineteen seventy nine that ..."). A footnote whose content matters can be folded into the sentence it attaches to; a footnote that is only a reference gets dropped.

**Links and URLs.** Replace a raw URL with a description of what it is: "a link to the project's GitHub page," "the original article on the journal's website." Drop bare DOIs and query-string-laden tracking URLs. Email addresses, when they must be spoken, become "name at example dot com."

**Figures, charts, images.** Describe from the caption and the surrounding discussion. "Figure three shows revenue climbing steadily from twenty nineteen to twenty twenty four, with the sharpest jump in the final year." If a PDF figure is the only place a number lives, rasterize the page, read it, and put the value into words.

## 19. Antithesis: rewriting negation-contrast for the voice

One sentence shape degrades AI narration above all others. A claim built as a negation that sets up a contrasting positive reads fine on the page. Out loud, the synthesis voice treats the comma or period after the negated part as a full stop and lands a falling, finished inflection there, so the two halves sound disconnected and the real point arrives flat.

The full catalog of forms, including the concessive variants and the carve-out for negation that does real informational work, is rule 9 of the `writing-voice` skill. Everything it flags is antithesis, and here it gets rewritten for an extra reason: the voice mis-inflects it.

Three ways to fix it:

1. State the positive directly. "The single biggest obstacle is operational: recreational books limit winning accounts within weeks," rewritten from "the obstacle is not handicapping. It is that recreational books limit winning accounts within weeks."
2. Describe neutrally. "AI-pick and tout services are marketing with no real edge behind them," rewritten from "marketing, not edge."
3. Explain with each part on equal footing. When the source plays one outcome down to raise another, name all the outcomes directly and level, so none of them is a runway for the next.

Inside quotations: when a quoted speaker uses the pattern, render the line as introduced or reported speech and lead with the positive, keeping the speaker's meaning. A book executive's "we're not looking at results, it's the way they're wagering" becomes "the book reacts to how customers bet, treating wagering style as the signal." This keeps the narration smooth and avoids the voice mishandling a first-person negation in the middle of a passage.

A plain factual negative is fine and needs no rewriting. "No U S regulator backs your funds," "the policy does not limit winning players," and "if you are not beating the closing line, your process has no edge yet" each state a fact, and none of them uses a negated half as the launchpad for a contrasting positive across the break. The target is the contrast structure, not every sentence containing the word "not."

Before and after, drawn from real prose:

- "Sharps win by buying mispriced numbers, not by picking winners." becomes "Sharps win by buying mispriced numbers. The edge is entirely in the price, in getting a number better than the true probability."
- "Limiting is not optional or rare. It is the structural business model of recreational books." becomes "Limiting is the structural business model of recreational books, and it caps how much most winning bettors can scale."
- "judge themselves on closing line value rather than recent wins" becomes "judge themselves on closing line value, treating recent wins as noise."

## 20. Cleaning up PDF extraction artifacts

Text pulled from a PDF carries debris that should be removed before or during the rewrite:

- **Hyphenation at line breaks.** `informa-` at the end of one line and `tion` at the start of the next rejoin into "information."
- **Running headers and footers.** A chapter title or author name repeating at the top of every page, and "Page 7 of 30" at the bottom, are page furniture; drop them.
- **Broken paragraphs.** Lines hard-wrapped mid-sentence should be rejoined into flowing paragraphs.
- **Column reflow.** Two-column layouts can interleave wrongly; check that the reading order is correct, and use a rasterized page to confirm if the text order looks scrambled.
- **Ligatures and odd glyphs.** `ﬁ` `ﬂ` and similar become "fi" "fl"; stray control characters get removed.
- **Reference list at the end.** Usually dropped, as covered in the main file.

## 21. Worked examples

**Example A: a formula in prose**
Input: `The Sharpe ratio is defined as $S = \frac{R_p - R_f}{\sigma_p}$, where $R_p$ is the portfolio return.`
Output: The Sharpe ratio is defined as the portfolio return minus the risk-free rate, all over the standard deviation of the portfolio. Here, the portfolio return is the return on the investment.

**Example B: an acronym, defined once**
Input: `We track CLV across books. A positive CLV means the bet beat the closing line. Long-run CLV predicts profit.`
Output: We track closing line value, which bettors call C L V, across books. A positive closing line value means the bet beat the closing line. Long-run closing line value predicts profit.

**Example C: a table described**
Input (Markdown table):
```
| Model | Accuracy | Latency |
|-------|----------|---------|
| A     | 94%      | 120ms   |
| B     | 91%      | 40ms    |
```
Output: The table compares two models. Model A reaches ninety four percent accuracy at one hundred twenty milliseconds, while model B reaches ninety one percent at forty milliseconds, trading a little accuracy for much lower latency.

**Example D: a dense formula described rather than recited**
Input: `$\mathcal{L}(\theta) = \sum_{i=1}^{N} \left[ y_i \log p_\theta(x_i) + (1-y_i)\log(1-p_\theta(x_i)) \right]$`
Output: The log-likelihood is the sum over all observations of a two-part term: for each example, the actual label times the log of the predicted probability, plus one minus the label times the log of one minus that probability. In plain terms, it rewards the model for assigning high probability to the outcome that actually occurred.

**Example E: symbols and numbers in ordinary prose**
Input: `Revenue rose ~12% in Q4 2024 to $5.2M, up from $4.6M (a 13% YoY gain).`
Output: Revenue rose around twelve percent in the fourth quarter of twenty twenty four, to five point two million dollars, up from four point six million dollars, a thirteen percent year-over-year gain.

**Example F: negation-contrast rewritten for the voice**
Input: `The biggest obstacle is not handicapping. It is that recreational books limit or ban winning accounts within weeks.`
Output: The biggest obstacle is operational: recreational books limit or ban winning accounts within weeks.
