# Bulk import

Mirroring a directory into Bear. The [inert pass](SKILL.md#inert-pass) applies to every file here.

## Manifest first

Build `path <TAB> tag <TAB> title` for the whole set before writing anything. A manifest makes the tag layout and the title scheme reviewable while they are still cheap to change, and it gives the readback check something to compare against.

Derive titles from paths with a category prefix, so `docs/architecture/odds_integration.md` becomes `Architecture: Odds Integration`. The prefix keeps titles unique across directories that share filenames, and Bear has no folders, so the prefix is the only grouping a title carries. Keep date prefixes on dated files so chronology survives sorting. Uppercase the acronyms the path lowercased.

Check the manifest for duplicate titles before writing. Two notes with one title makes `--title` lookups ambiguous forever after.

## Source pointer

Open each body with the repo path and the commit it came from:

```
> Source: `docs/architecture/auth.md` @ commit a80e8e8
```

That line is what makes a note diffable against its source later, and what tells a re-import which notes are stale.

## Idempotency

`bearcli create --if-not-exists` returns the existing note instead of minting a duplicate, so a rerun after a partial failure is safe.

Correcting an import that already landed calls for `bearcli overwrite <id>`, which keeps ids, backlinks, and creation dates. Rebuild the full body on overwrite, including the `# Title` line and the trailing tag line, since Bear stores tags in the content and drops any the new body omits.

## Readback

Read every note back and compare it to its processed source. Comparing all of them costs one `cat` per note and catches truncation, encoding damage, and notes that silently failed to write. Strip the title line, the source pointer, and the trailing tag line before comparing.

Confirm heading counts match the source too. A malformed inert pass shows up as headings that stopped being headings.

Finish on the [tag-list diff](SKILL.md#tag-list-diff), which catches what the readback cannot.

## Scale

Roughly 180 notes import in under a minute, so batching or backgrounding buys nothing. Pilot two notes, read one back, then run the rest.
