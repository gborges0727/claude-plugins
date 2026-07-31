---
description: Clean up scratch files, stage everything, commit, and push. Explicit invocation only.
disable-model-invocation: true
---

# Add to Git

Check the repo's `CLAUDE.md` first. If it requires a branch, worktree, or pull request, follow that instead of committing to the current branch.

## Step 1: Cleanup
Remove any non-relevant files used for testing and debugging from the current directory.

## Step 2: Stage Changes
Add all uncommitted changes to git staging area:
```bash
git add .
```

## Step 3: Commit
Create a commit with a descriptive message explaining the relevant changes:
```bash
git commit -m 'Your descriptive commit message here'
```

## Step 4: Push
Push the changes to the remote repository (if it exists):
```bash
git push
```