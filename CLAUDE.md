# claude-plugins

## Bump the rev on every PR

Every PR raises the `rev` number in two places and keeps them equal:

- the `# rev: N` line in the loader snippet in `README.md`
- the `# rev: N` comment in `scripts/cloud-bootstrap.sh`

CI (`.github/workflows/rev-bump.yml`) fails any PR into `main` that skips
the bump or leaves the two numbers different. The number only moves forward.

The bump changes nothing in a cloud environment by itself. After the merge,
pasting the new rev into an environment's Setup script field is what forces
the snapshot rebuild. The repo's number exists so the field and the repo
never disagree about which rev is current.

## Strip the server-appended attribution after creating a PR

The cloud environment's PR-creation path appends a Claude Code attribution
footer to the PR body server-side, after the submitted text leaves the
session's hands. Writing the body without the footer does not prevent it.
The update path does not re-append it, so an edit removes it for good.

Immediately after creating a PR from a cloud session:

1. Fetch the PR body you just created.
2. If it ends with an attribution block (a `---` rule followed by a
   "Generated with/by Claude Code" line, or the `🤖 Generated with
   [Claude Code]` form), edit the PR body to remove that block.
3. Confirm the body now ends at your intended last line.

This repo carries no AI attribution on commits or PRs. The same applies to
commit trailers: no `Co-Authored-By: Claude`, no generated-with footer.
