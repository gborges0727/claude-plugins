---
description: Re-explain the previous answer in plain english. Unpacks compressed reasoning and replaces jargon with everyday words. Explicit invocation only.
disable-model-invocation: true
---

# Plain english

Re-explain your immediately preceding message so it lands without background the reader does not have.

The previous answer was not wrong and was not padded. It was dense. It compressed several ideas into single sentences and leaned on terms it never established. Fix that.

If any text follows the command, read it as a description of what confused the reader. Re-explain the whole answer with that specific gap in mind, rather than narrowing to the part they named.

## What to change

**Unpack the compression.** Split a sentence carrying more than one idea, and establish background the original assumed before using it. Unpack what actually blocked the reader, which is a smaller set than everything that could be unpacked. Spelling out a step they already had costs the length budget and teaches them nothing.

**Lead with everyday words.** Where the original used a technical term, write the plain phrasing and put the term in parentheses once, on first use. `The command only writes files it has not already written (idempotent).` The plain words carry the sentence. The term rides along so it stays searchable and reusable, and it appears once, not on every mention.

**Ground it in the real thing.** Use the actual filenames, values, function names, and inputs from what was being discussed. No analogies from outside the domain. An invented parallel can teach something false and the reader has no way to catch it.

**Explain code as ideas.** No code blocks and no line references. Say what the code accomplishes in prose, using the real names. `The auth check reads the token out of the request header and looks it up before any handler runs.`

## Shape

Flat prose. No headers, no bullet lists, no numbered steps, not even when the content is a sequence.

**Land at or under the original's length.** This is a rephrasing, not an expansion. The original already said everything; the job is saying it in words that land. Swapping a dense sentence for a clear one is usually a wash, and dropping the terms that needed defining often comes out shorter. A version that runs materially longer than what it replaces has added content instead of clarifying it, which is the failure this command exists to avoid.

The reader asked for plain english because the original was hard to follow. A longer hard-to-follow answer is a worse answer.

One idea per paragraph, since paragraphs are the only navigation on offer. Order them so each builds on the one before, and never reach forward to something not yet explained.

## Style

The `writing-voice` skill does not apply here. Ignore its rule about keeping technical terms and precision intact, which this command deliberately reverses, and ignore its drafting passes. Explaining clearly wins over drafting discipline.

The working conventions from `CONVENTIONS.md` still hold. No em dashes anywhere. No clause-joining semicolons or colons. No packaging clauses that rate or preface another clause. No opener praising the question and no closing offer to elaborate.
