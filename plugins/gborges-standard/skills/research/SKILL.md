---
name: research
description: Send a background agent to answer a question from primary sources (official docs, source code, specs) and write the findings to a cited Markdown file in the repo. Use when the user wants a topic researched, docs or API facts checked, or reading delegated so the session can keep working.
---

# Research

Send a background agent to do the reading, so this session keeps working
while it reads.

## Who does it

The agent reads to reach a conclusion, so it runs on
`gborges-standard:opus-medium`. When `~/.claude/gborges-standard.json`
says `"codex": true`, send it through the `codex-delegate` skill on the
`sol-xhigh` rung instead, since the brief stands alone and the output file
checks it. Either way, run it in the background.

## The brief

The brief carries the question, exactly as the user put it, and these
rules:

1. Answer from primary sources, meaning the official docs, the source
   code, the spec, or the first-party API. A blog post about the docs is
   not a source. Follow every claim back to the page or file that owns it.
2. Write one Markdown file. Open with the question and a short answer.
   Then the findings, each with a link or path to its source and the date
   the source was read. Say plainly when a claim could not be verified.
3. Save it at the research path in the plugin's
   `reference/output-locations.md`, which is `docs/research/<slug>.md`
   unless the repo's `.claude/gborges-standard.json` names another docs
   folder. When the repo already keeps such notes somewhere else, match
   that.
4. Report the file's path and the short answer.

## When it returns

Read the file. Relay the short answer to the user with the path. Do not
restate the whole file.
