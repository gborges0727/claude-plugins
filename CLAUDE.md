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

## No AI attribution on PRs or commits

The cloud environment's PR-creation path appends a Claude Code attribution
footer to the PR body server-side, after the submitted text leaves the
session's hands. Writing the body without the footer does not prevent it.
The update path does not re-append it, so an edit removes it for good.

A PostToolUse hook in `.claude/settings.json` fires after every
`mcp__github__create_pull_request` call and injects the fix-up instruction
(`scripts/strip-pr-attribution-hook.sh`): fetch the PR body, remove the
trailing attribution block, confirm the body ends at the intended last line.

The hook only fires when the PR is created through that tool. If a PR gets
created another way (the web UI's Create PR button) and shows the footer,
apply the same edit by hand: fetch the body, strip the trailing `---` rule
and "Generated with/by Claude Code" line.

Commits carry no AI trailers either: no `Co-Authored-By: Claude`, no
generated-with footer.
