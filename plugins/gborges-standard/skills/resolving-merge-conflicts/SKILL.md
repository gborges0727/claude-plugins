---
name: resolving-merge-conflicts
description: Resolve an in-progress git merge or rebase conflict by reading why each side changed, keeping both intents, and finishing the merge. Use when git reports conflicts or a merge or rebase is stopped.
---

# Resolving merge conflicts

1. **See where the merge stands.** Run `git status` to list the conflicted
   files, and `git log` on both sides to see what each branch changed.

2. **Find out why each side changed.** For each conflict, read the commit
   messages, the pull requests, and the issues behind both sides, until you
   can say what each change was for.

3. **Resolve each hunk.** Keep both intents where they fit together. Where
   they cannot, keep the one that matches the merge's stated goal and say
   what was given up. Add no behaviour that neither side had. Always
   resolve. Never run `--abort`.

4. **Run the project's checks.** Find them in the repo (usually the type
   checker, then the tests, then the formatter) and run them. Fix anything
   the merge broke.

5. **Finish.** Stage everything and commit the merge. When rebasing, run
   `git rebase --continue` and repeat from step 1 until every commit is
   replayed.
