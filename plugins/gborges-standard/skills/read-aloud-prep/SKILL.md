---
name: read-aloud-prep
description: >-
  Rewrite a document into spoken-English Markdown that an AI narrator reads aloud smoothly,
  preserving every fact. Use when the user wants a PDF, paper, Markdown file, or EPUB prepped
  for ElevenReader, Speechify, or any text-to-speech voice.
---

# Read-Aloud Prep

The rewrite is **lossless** and nothing else is protected. Every fact, claim, number, name, and technical term carries over exactly. Phrasing, structure, sentence boundaries, and order are yours to change as hard as the spoken version needs. A listener should finish holding every fact the source carried, heard in a form that was easy to follow.

Code, tables, figures, and long URLs are voiced rather than reproduced, since they cannot be read aloud as written. A description that carries their real content is still lossless.

Everything else in this skill serves **the ear**, the channel that catches what the page hides and misses what the page shows.

## Workflow

### 1. Read the source in full

- **Markdown, plain text, `.txt`:** read the file directly.
- **EPUB:** it is a zip of XHTML files. Unzip and pull the text from the chapter files in spine order.
- **PDF:** extract the text layer with `pdftotext -layout` or `pdfplumber`. Run `pdffonts` first. An empty font table means the PDF is scanned, so OCR or rasterize-and-read instead.

Text extraction is blind to equations and figures. A formula often comes out as garbage like `f(x)=Pn i=1 wixi` or vanishes, and a chart comes out as nothing. Rasterize any page carrying math or a figure (`pdftoppm -jpeg -r 150 -f N -l N`) and read the image. Saying the math correctly out loud depends on seeing it correctly first.

Done when every page has been read, and every page carrying math or a figure has been rasterized and viewed.

### 2. Survey the document and build the glossary

Skim the whole thing once. You are looking for three things.

- **Subject and domain.** This is what lets you expand acronyms correctly. "CLV" is "closing line value" in sports betting and "customer lifetime value" in marketing, and only the surrounding material tells you which.
- **Which hard elements are present.** Formulas, tables, code, heavy citations, a reference list at the end. Knowing this up front lets you plan how each is handled.
- **The glossary.** Every acronym, abbreviation, and symbol-heavy term, with its chosen spoken expansion written next to it. Decide which are initialisms spelled letter by letter (F B I, C L V), which are said as a single word (NASA, said "nassa"), and which are universal enough to need no expansion (USA, AI). Where the letters could expand two ways, the term matters, and context does not settle it, ask the user.

Done when every acronym, abbreviation, and symbol-heavy term in the document has a chosen expansion recorded.

### 3. Rewrite section by section

Load `references/normalization-guide.md` before rewriting the first section and keep it open. It carries the full catalog for math, symbols, numbers, units, dates, structure, and the artifacts PDF extraction leaves behind.

Invoke the `writing-voice` skill and apply its rules to the prose you produce. That skill is the source of truth for packaging, stand-in nouns, headers, and manufactured contrast. This skill adds only what the ear needs on top.

Read the way a narrator reads something cold. Anywhere the eye would decode a thing the ear cannot follow, convert it into words.

Done when every section of the source appears in the output, with nothing summarized away.

### 4. Review by ear

Read the output back as if hearing it, and fix what you find.

- Leftover symbols, LaTeX commands, or Markdown markup (`$`, `\frac`, `**`, `|`, `_`, backticks)?
- Bare numbers, dates, or ratios that should be spelled into words?
- An acronym never defined, or defined more than once?
- A code block, table, or URL still sitting raw instead of described?
- **Antithesis** left anywhere, a negated half setting up the positive that follows ("not X, it's Y," "X, not Y," "Sure, X. But Y")? Rewrite to lead with the positive alone.
- A list whose count or sequence matters but sits in silent Markdown markers? Move the enumeration into the words, or rejoin into prose with spoken ordinals.
- A colon that would clip? A colon inside a heading?
- A sentence carrying several numbers at once, or a two-decimal percentage? Split to one figure per sentence and round the awkward ones.
- A long subject cut off from its verb by a comma, leaving the verb stranded? Front-load the main clause.
- A heading that lands as a fragment rather than opening its section as speech?
- Does each sentence run in one breath?

Done when every item above has been checked against the full output.

### 5. Save and present

Write the result as a clean `.md` file to the outputs directory and present it. A sensible filename echoes the source, like `original-name-read-aloud.md`.

## Output conventions (locked)

Hold to these unless the user says otherwise.

1. **Clean Markdown.** Keep real structure so the app can navigate, and make every heading speakable. Strip anything a voice reads as a literal symbol: the `**` around bold, the `*` around italics, backticks, and table pipes. Lean toward prose over visual lists, since list markers are silent and a colon clips.

2. **Non-speakable content becomes plain spoken words, carrying its information.** A code block becomes a sentence or two saying what the code does. A table becomes prose that still carries the real numbers and the takeaway. A long URL becomes a short description of what it points to. A figure gets described from its caption and the surrounding text.

3. **Abbreviations: define once, then full words.** The first appearance states the full term and ties the abbreviation to it a single time, the way a speaker would: "closing line value, which analysts call C L V." Every later appearance uses the full words only. The glossary from step 2 is what keeps this consistent when the first mention and a later one sit chapters apart.

4. **Antithesis gets rewritten to lead with the positive.** A claim built as a negation that sets up a contrasting positive makes the synthesis voice land a finished, falling inflection on the negated half and read the break there as a full stop, so the real point arrives disconnected and flat. Rewrite every instance, including inside quotations, where a speaker's line becomes reported speech that leads with the positive. A plain factual negative like "no regulator backs your funds" is fine. Guide section 19 has the form catalog and the worked rewrites.

## Usually dropped

Remove these unless the user asks to keep them.

- Page numbers, running headers and footers, and "Page 4 of 12" lines.
- Tables of contents and indexes.
- The bibliography or reference list at the end. A closing line such as "The document ends with its list of references" is enough to mark that it was there.
- Inline citation markers and footnote numbers like "[12]" or superscript "¹." Where a citation carries meaning in the sentence, fold it in naturally ("according to Smith and colleagues in twenty twenty").
- Bare DOIs and tracking-laden URLs.

## Long documents

Process in sections, and carry the glossary forward across them. The glossary is what makes "define once" hold over a whole book, so a term introduced in the first section stays in full words when it reappears in the tenth.

## Interpretation

Verbalizing math and describing a table both involve a small act of interpretation. Say the formula the way its author would read it aloud, and describe the table the way its author would explain it. Add no claim the source does not make, and drop nothing a listener would want. When a formula is dense enough that a symbol-by-symbol reading would lose any listener, say what it computes in plain terms instead, since comprehension is the entire point of reading something aloud.
