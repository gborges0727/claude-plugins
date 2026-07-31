---
name: read-aloud-prep
description: >-
  Convert a document (PDF, Markdown, EPUB, or any text) into a clean, spoken-friendly version
  that an AI text-to-speech voice can read aloud smoothly. Use this skill whenever someone wants
  to prepare or clean up a document for narration apps like ElevenLabs Reader (Eleven Reader),
  Speechify, or any TTS voice, and especially when the source contains math formulas, LaTeX,
  acronyms or abbreviations, symbols, numbers and units, tables, code, citations, or stray
  formatting markup that a voice would mispronounce or stumble over. Trigger on requests like
  prep this PDF for ElevenReader, make this readable for text to speech, the AI voice keeps
  mangling the formulas in my paper, turn this into something I can listen to, or convert this so
  it reads aloud cleanly. The output keeps the full content of the original and rewrites only what
  does not speak well. Do not use this skill for summarizing, shortening, or translating a
  document; this skill rewrites for speakability while preserving everything.
---

# Read-Aloud Prep

Turn a source document into clean spoken-English Markdown that an AI narrator reads without tripping. The reader wants to *listen* to the whole thing, so the job is to translate the page into how a careful person would say it out loud, while keeping every bit of the actual content.

## The one rule that governs everything

Preserve every piece of information, and change everything else freely. Every fact, claim, number, name, and technical term carries over exactly, you never summarize the substance, and you never soften a technical claim into a vague one. Within that line, rewrite hard. Restructure paragraphs, merge or split sentences, reorder points into a logical order, and delete any sentence that carries no information, such as pure packaging, meta-commentary, and filler. Phrasing, structure, and emphasis are yours to change as much as the spoken version needs. Meaning is not. The only content that gets condensed into a short spoken description is the handful of elements that cannot be read aloud as written, such as code, raw tables, long URLs, and figures. So the standard is whether a listener ends up with every fact the source carried, said in a way that is easy to hear. You do not have to keep every original sentence to meet it.

## Voice and editing stance

Write the way a sharp person explains something to a friend sitting next to them. Make the point, give the reason in the same breath, and keep moving. Be interventionist about getting there. The source was written to be read on a page, and reading it aloud well usually means reshaping it.

Default to the shortest direct phrasing that keeps all the information. Prefer one idea per sentence. Turn passive into active. When two sentences say one thing, merge them. When a long nested sentence buries the point, split it and put the point first. When a sentence is pure packaging, delete it instead of rephrasing it.

Remove these AI habits wherever they appear:

- **Slogan-then-explain openings.** Lead with the plain point. "Closing line value is the north star" becomes "What predicts profit is closing line value."
- **Evaluative noun-phrase labels for an action.** Say what you actually do. "the foundational, accessible edges" or "the core repeatable workflow" becomes a description of the action itself.
- **Instrument and revelation metaphors**, such as "the signal," "the lever," "the smoking gun," "the north star," "the lens," "the unlock," "the key," "the playbook." State the plain thing.
- **Meta-commentary about the explanation**, such as "Now I can explain it precisely," "the single most important thing to know up front," or "let me be precise here." Delete the sentence and keep only the substance it was wrapping.
- **Importance announcements**, such as "it's worth noting," "importantly," "critically," or "there's an important flag here." State the content directly and let it carry its own weight.
- **Personified abstractions**, such as "the principle survives intact." Use a plain verb: "the principle still holds."
- **Ordinal-plus-label outline rhythm**, such as "First, X is the Y. Second, A and B are the C." Make the point first, and keep a label only when it carries information. This works with the spoken-ordinal guidance in Pacing: when a real sequence has to be heard, keep the ordinal, and still lead each item with its actual point rather than a label.

Antithetical constructions get the same treatment, set out in full as output convention four and in the guide. Manufactured contrast that negates one thing to set up another, including the concessive versions ("Sure, X. But Y," "While X is true, the real point is Y," "It's tempting to think X, but Y"), gets rewritten to lead with the positive claim by itself. Where both halves are true and both matter, state them as a pair ("X and Y both"). Keep a negation only when it corrects a real misconception or reports a genuine contrast, and cut it when it is there for emphasis alone.

A few guardrails. Do not add hedging, filler, or summary the source did not have. Do not soften a technical claim into a vague one. Do not change a number, a name, or the meaning. And if a sentence is already plain and human, leave it alone.

## Output conventions (locked for this skill)

These were chosen deliberately. Hold to them unless the user says otherwise.

1. **Format: clean Markdown (`.md`).** Keep real structure that helps the app navigate, and make every heading speakable. Strip everything a voice would read as a literal symbol: the `**` around bold, the `*` around italics, backticks, and the pipe characters from tables. One catch matters for listening: a narrator does not read list markers, and it treats a colon as a clipped pause, so any count or sequence has to live in the words rather than in the formatting. Lean toward prose over visual lists for content meant to be heard. The pacing section below covers this.

2. **Non-speakable content: describe it in plain spoken words, and keep its information.** A code block becomes a sentence or two saying what the code does. A data table becomes prose that still carries the real numbers and the takeaway, so the listener keeps the content and simply does not hear a grid recited cell by cell. A long URL becomes a short description of what it points to. A figure or chart gets described from its caption and the surrounding text. The aim is for a listener to end up knowing what was in that element, conveyed the way a person would explain it aloud.

3. **Abbreviations and acronyms: define once, then full words.** The first time a term appears, state the full term and tie the abbreviation to it a single time, the way a speaker would: "closing line value, which analysts call C L V." Every appearance after that uses the full words only ("closing line value"). Build a glossary at the start so this stays consistent across the whole document, including long ones where the first mention and a later mention sit far apart.

4. **Rewrite negation-contrast phrasing so the voice reads it right.** A claim framed as a negation that sets up a contrasting positive, such as "the obstacle is not handicapping. It is that books limit you," or "marketing, not edge," or "not just X but Y," makes the synthesis voice land a finished, falling inflection on the negated half and read the period or comma there as a full stop, so the real point arrives disconnected and flat. Rewrite every such case to lead with the positive claim on its own. You have three moves: state the positive directly, describe neutrally, or, where the source escalates by playing one outcome down to raise another, name all the outcomes on equal footing. This holds inside quotations too: render a speaker's negation-contrast line as introduced or reported speech that leads with the positive. A plain factual negative, like "no regulator backs your funds," is fine and needs no change. The concessive versions count too, such as "Sure, X. But Y" and "While X is true, the real point is Y." The full catalog of forms and worked rewrites is in `references/normalization-guide.md`.

## Pacing for the voice

A few things the page hides but the ear catches. They came out of listening to real output through a synthesis voice, and they matter as much as getting the words right.

- **List markers are silent, so put the count in the words.** A narrator skips the "1." and "2." of a numbered list and pauses only briefly between items, so a run of findings or steps blurs together and the enumeration is lost. Lead each item with a spoken ordinal or transition ("First, ... Second, ..." or "The first finding is ..."), and prefer flowing prose over a visual list for anything a listener should track in order or by count. Keep the ordinal in front of the item's actual point, not a label, so it does not turn into the robotic outline rhythm flagged under Voice. A genuine sequence or a defined catalog earns the count; for a few loosely parallel points, a strong distinct opening on each one carries the boundary on its own. Bullets are silent the same way.
- **Colons clip, so use them sparingly.** The voice reads a colon as a pause shorter than a comma, which often sounds unnatural. Where a real pause belongs before an explanation or a list, end the sentence and start a new one: "Here is the logic. As kickoff approaches ..." instead of "The logic: as kickoff approaches ...". Keep colons out of headings too, with a comma or a rewording.
- **Break up dense runs of numbers, and round them.** Several figures in one sentence are hard to follow, because the listener is still holding the first when the next lands. Split them into short sentences, about one figure each, and round awkward percentages to a whole number with a hedge ("around nineteen percent," not "eighteen point six nine percent"). Keep an exact value only when it is the actual point, in a clean form like "just over fifty two percent." The guide's percentage section has the detail.
- **Keep the subject and verb together, and lead with the main clause.** A long windup before the verb, especially one closed off by a comma, makes the voice pause in the wrong place and strands the verb. The listener hears the whole subject, then a pause, then a dangling "is the workflow." Rewrite "Holding accounts, then comparing prices to find value, is the core workflow" as "The core workflow is to hold accounts, then compare prices to find value." State the claim first and let the detail follow.
- **Write headings that can be heard.** A heading is a visual cue the ear misses. The narrator reads the heading text inline, as one more line with a short pause on each side, so a bare label like "Details" or a stranded noun phrase like "Theory and Methods" lands as a fragment between sentences, and two stacked headings land as two fragments in a row. Write the heading text itself as a natural spoken transition that opens the section, such as "Now to the operational reality, the obstacles that make these edges hard to use," and let that one line carry the boundary instead of a separate transition sentence in the body. Drop pure structural wrappers that hold no spoken content. The heading still serves the page and the app; its words just need to read as speech.

## Workflow

### 1. Read the source in full

Get the complete, accurate text before transforming anything.

- **Markdown / plain text / `.txt`:** read the file directly.
- **EPUB:** it is a zip of XHTML files; unzip and pull the text from the chapter files in spine order.
- **PDF:** extract the text layer with `pdftotext -layout` or `pdfplumber`. Run `pdffonts` first; an empty font table means the PDF is scanned, so OCR or rasterize-and-read instead of running text extraction.

A point that matters a lot for this skill: **text extraction is blind to equations and figures.** A formula in a PDF often comes out as garbage like `f(x)=Pn i=1 wixi` or vanishes entirely, and a chart comes out as nothing at all. Whenever the document has math or figures that carry meaning, rasterize those pages (`pdftoppm -jpeg -r 150 -f N -l N`) and read the image so you capture the real formula and the real figure before you try to say them in words. Saying the math correctly out loud depends on seeing it correctly first.

### 2. Survey the document and build the glossary

Skim the whole thing once before rewriting. You are looking for three things:

- **Subject and domain.** This is what lets you expand acronyms correctly. "CLV" is "closing line value" in sports betting and "customer lifetime value" in marketing, and only the surrounding material tells you which. Knowing the domain also helps you handle technical terms and proper nouns sensibly.
- **Which hard elements are present.** Formulas? Tables? Code? Heavy citations? A reference list at the end? Knowing this up front lets you plan how each one will be handled.
- **The abbreviation and term glossary.** List every acronym, abbreviation, and symbol-heavy term, and write the chosen spoken expansion next to each. Decide which are initialisms to spell out letter by letter (F B I, C L V), which are acronyms said as a single word (NASA, said "nassa"), and which are so universal they need no expansion at all (USA, AI). For anything ambiguous and important where context does not settle it, ask the user rather than guess.

### 3. Rewrite section by section into speakable Markdown

Walk the document in order and rewrite each part. Load `references/normalization-guide.md` for the full catalog of how to verbalize math, symbols, numbers, units, dates, and the rest. The highest-frequency moves are summarized below so you rarely need to break flow to consult it.

Work through the text the way a thoughtful narrator reads something cold: anywhere the eye would have to decode a thing the ear cannot follow, convert it into words.

### 4. Review by ear

Read your output back as if you were hearing it. Catch anything that slipped through:

- Any leftover symbols, LaTeX commands, or Markdown markup (`$`, `\frac`, `**`, `|`, `_`, backticks)?
- Any bare numbers, dates, or ratios that should be spelled into words?
- Any acronym that was never defined, or one that got defined more than once?
- Any code block, table, or URL still sitting there raw instead of described?
- Any negation-contrast phrasing left, like a negated clause that sets up the next one ("not X, it's Y," "X, not Y")? Rewrite to lead with the positive.
- Any list whose count or sequence matters but sits in silent Markdown markers? Move the enumeration into the words, or rejoin into prose with spoken cues.
- Any colon that would clip, where a period and a fresh sentence would pause more naturally? Any colon inside a heading?
- Any sentence carrying several numbers at once, or a two-decimal percentage? Split it into one figure per sentence and round the awkward percentages.
- Any sentence with a long subject cut off from its verb by a comma, leaving the verb stranded? Front-load the main clause so the subject and verb arrive together.
- Does each major section open with a spoken transition, so the listener hears the boundary that the heading only shows on the page?
- Any leftover AI habits: a metaphor like "the north star," an evaluative label standing in for an action, an importance announcement ("critically," "importantly"), meta-commentary, or a packaging sentence carrying no information? Cut or rewrite them.
- Does it flow as speech, with sentences a person could say in one breath?

Fix what you find. This pass is where a strong output pulls ahead of a rough one.

### 5. Save and present

Write the result as a clean `.md` file to the outputs directory and present it. A sensible filename echoes the source, like `original-name-read-aloud.md`.

## Highest-frequency transformations (quick reference)

Full detail lives in `references/normalization-guide.md`. The common cases:

- **Math operators:** `=` "equals," `+` "plus," `−` "minus," `×` "times," `/` "over" or "divided by," `<` "less than," `>` "greater than," `≈` "approximately," `±` "plus or minus."
- **Powers and roots:** `x^2` "x squared," `x^n` "x to the power of n," `√x` "the square root of x."
- **Sums and integrals:** `Σ` "the sum of," `∫ f(x) dx` "the integral of f of x with respect to x," `Π` "the product of."
- **Greek and stats:** `μ` "mu" or "the mean," `σ` "sigma," `π` "pi," `Δ` "delta" or "the change in," `P(A|B)` "the probability of A given B," `x̄` "x bar," `R²` "R squared."
- **Symbols:** `%` "percent," `$` "dollars" (`$5M` "five million dollars"), `&` "and," `@` "at," `#1` "number one," `°` "degrees," `~` "around," `/` "per" inside units (`km/h` "kilometers per hour").
- **Numbers and dates:** `1990` "nineteen ninety," `2008` "two thousand eight," `Q4 2024` "the fourth quarter of twenty twenty four," `3/14/25` "March fourteenth, twenty twenty five," `3:1` "three to one," `12.5%` "twelve and a half percent," `1st` "first."
- **Percentages for the ear:** round multi-decimal percentages to a whole number with a hedge, so `18.69%` becomes "around nineteen percent" and `9.1%` "about nine percent." Keep an exact value only when it is the point, in a clean form like "just over fifty two percent." Split a sentence carrying several numbers into one figure per sentence.
- **Units:** keep the number with the spoken unit, `5kg` "five kilograms," `20°C` "twenty degrees Celsius."
- **Latin abbreviations:** `e.g.` "for example," `i.e.` "that is," `etc.` "and so on," `et al.` "and colleagues," `vs.` "versus."
- **Markdown markup:** drop `**`, `*`, backticks, `~~` and keep the words inside; `[text](url)` keeps "text" and the link gets described or dropped.
- **Negation-contrast phrasing:** rewrite "not X, it's Y," the bare "X, not Y," and "not just X but Y" to lead with the positive claim, since the voice mis-inflects on the negated half. The full list is in the guide.

## Things that are usually dropped

Some elements exist for the eye on the page and add nothing for a listener. Remove these unless the user asks to keep them:

- Page numbers, running headers and footers, and "Page 4 of 12" lines, which are extraction artifacts.
- Tables of contents and indexes.
- The bibliography or reference list at the end, since reading a list of citations aloud serves no one. A single closing line such as "The document ends with its list of references" is enough if you want to mark that it was there.
- Inline citation markers and footnote numbers like "[12]" or superscript "¹." Where a citation carries meaning in the sentence, fold it in naturally ("according to Smith and colleagues in twenty twenty"); where it is just a bracketed number, drop it.
- Bare DOIs and tracking-laden URLs.

## Long documents

For anything long, process in sections so quality stays high, and carry the glossary forward across them. The glossary is what makes "define once" work over the whole document: a term introduced in the first section stays in full words when it reappears in the tenth. Keep the running list as you go so you never re-introduce a term or leave a later one undefined.

## A note on faithfulness to meaning

Verbalizing math and describing a table both involve a small act of interpretation, and that is expected. Say the formula the way its author would read it aloud, and describe the table the way its author would explain it. The line to hold is to add no claims that are absent from the source and to quietly drop nothing a listener would want. Rewriting a negation-contrast into a direct positive sits inside this line: it carries the same claim and changes only the framing, which is what keeps the narration clean. When a formula is so dense that a symbol-by-symbol reading would lose any listener, say what the formula computes in plain terms instead (the guide shows how), because comprehension is the entire point of reading something aloud.
