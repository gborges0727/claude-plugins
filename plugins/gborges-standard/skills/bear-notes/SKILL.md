---
name: bear-notes
description: Bear note writing. Use when saving, importing, appending, overwriting, tagging, or attaching anything in Bear, when mirroring files or docs into Bear, or when the user says to put something in their notes.
---

# Writing to Bear

Bear reads its structure out of the note body. Tags, wikilinks, and the title all come from the text, so anything pasted in is **live**. Bear acts on it rather than showing it. An issue reference like `#144` sitting in a doc becomes a real entry in the global tag list. A `[[...]]` becomes a real wikilink and backlink. Both land outside the note being written, so a note that reads correctly can still have corrupted the database around it.

Make live markup **inert** before every write.

## Inert pass

`scripts/inert.py` runs the pass on stdin and covers the whole step:

```bash
python3 scripts/inert.py < doc.md | bearcli create "Title" --tags parent/child
```

Two forms are structural.

| Live form | Effect | Inert form |
|---|---|---|
| `#144`, `#95-flip`, `#123/#126` | Adds a global tag | Backticks |
| `[[anything]]` | Creates a wikilink and backlink | Backticks |

A `#` opening a word is live anywhere on the line, including after a slash, and Bear absorbs trailing punctuation into the tag name. Two of them on one line produce a single multi-word tag out of everything between, which is how one line of prose mints a tag like `99 per-row fields); live remainder = the`. Markdown headings, fenced blocks, and inline-code spans are safe already.

The rest of Bear's syntax (`==highlight==`, `~underline~`, `$math$`) changes display only, and the stored bytes round-trip either way. Bear drops setext headings, indented code blocks, and lazy continuation, so a doc built on 4-space code blocks arrives as plain paragraphs.

## Content through stdin

`bearcli create` and `bearcli overwrite` read the body from stdin when `--content` is absent. Piping keeps file bytes out of the context window, which is what lets a 178-file import cost about what a one-file import costs. `--content` also interprets `\n` and `\t`, so a body holding a literal backslash-n arrives corrupted.

## Deepest subtag alone

Bear rolls parents up. A note tagged `FairLine/architecture` already answers a `#FairLine` search, so passing both hangs a redundant tag on the note.

## Explicit titles

Pass the title rather than letting Bear take it from the first line, which otherwise promotes a source pointer or a shared `# Overview` heading into the title. Keep the id the write returns and address the note by id afterwards. `bearcli cat` and `bearcli overwrite` take an id positionally, so a title needs the `--title` flag.

## Tag-list diff

Read the global tag list before the write and again after. The write is clean when the difference is exactly the tags intended. Tag pollution never appears in the note that caused it, so reading the note back cannot catch it.

Junk tags clear when the content that minted them goes inert. Rewrite the offending notes rather than deleting the tags, since deleting a tag edits every note carrying it.

## Attachments

Bytes go in through `bearcli attachments add <note-id> --filename <name>` on stdin. The MCP `add_attachment_from_url` tool fetches https only and rejects `file://` and `data:`. Both paths insert a markdown link, and Bear renames on collision, so adding the same file twice leaves two copies and two links. External image links (`![](file:///…)`, `![](https://…)`) render as nothing.

## Bulk imports

Mirroring a directory adds a manifest, an idempotency rule, and a readback check: [BULK-IMPORT.md](BULK-IMPORT.md).
