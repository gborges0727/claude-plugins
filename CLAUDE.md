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
