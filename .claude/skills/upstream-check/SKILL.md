---
name: upstream-check
description: Compare Matt Pocock's skills repo against the commit this plugin's ported skills were taken from, and list what is new, changed, or gone. Explicit invocation only.
disable-model-invocation: true
---

# Upstream check

The plugin's `grill`, `build`, `spec`, `routine`, `wayfinder`, `handoff`,
`research`, `wait-what`, `teach`, `writing-for-agents`, `domain-modeling`,
`diagnosing-bugs`, and `resolving-merge-conflicts` skills were rewritten
from `github.com/mattpocock/skills`. This skill says what has changed there
since, so you can decide what to fold in.

`UPSTREAM.md` next to this file records the upstream commit the port was
taken from, and the map from each upstream skill to the plugin skill it
became. Read it first.

## Steps

1. Get the current upstream commit and the list of skill folders:

   ```sh
   gh api repos/mattpocock/skills/commits/main --jq .sha
   gh api 'repos/mattpocock/skills/git/trees/main?recursive=1' --jq '.tree[] | select(.path | endswith("/SKILL.md")) | .path'
   ```

2. List the skill folders at the recorded commit the same way, with the
   recorded SHA in place of `main`. Compare the two lists. A folder only in
   the new list is a new skill. A folder only in the old list was removed.

3. For every upstream skill that `UPSTREAM.md` maps to a plugin skill, and
   for every skill the user asked about, diff its folder between the two
   commits:

   ```sh
   gh api repos/mattpocock/skills/compare/<recorded-sha>...<current-sha> --jq '.files[] | select(.filename | startswith("skills/")) | .filename'
   ```

   Fetch the changed `SKILL.md` at both commits with
   `gh api repos/mattpocock/skills/contents/<path>?ref=<sha>` and read the
   difference.

4. Report, in this order: new skills with a one-line gist each, changed
   skills with what changed and whether the plugin's version already covers
   it, and removed skills. Say when nothing changed.

5. Offer to update the recorded SHA and date in `UPSTREAM.md`. Do it only
   on a yes.

Nothing here touches the plugin's skills. Folding a change in is its own
task.
