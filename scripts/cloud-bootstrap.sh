#!/bin/bash
# Setup script for a Claude Code cloud environment.
#
# The loader snippet in README.md curls this file from main, so environments
# run whatever is on main here. It installs the bundle at user scope inside
# the session VM, before Claude Code launches, so the hook, the skills, and
# the command are live on the first turn and nothing is spent getting there.
#
# Every PR bumps the rev below and the identical rev in the README loader
# snippet. CI (.github/workflows/rev-bump.yml) fails the PR when the bump is
# missing or the two numbers differ. After the merge, paste the new rev into
# each environment's Setup script field when the change cannot wait out the
# snapshot expiry.
# rev: 18

set -u

# claude-plugins-official is a trusted marketplace name but is not registered
# in a fresh session VM, and nothing registers it later. Adding it here is
# what lets the bundle's dependencies resolve. With both marketplaces known,
# installing the bundle pulls its dependencies in, so this script needs no
# edit when the dependency set changes.
claude plugin marketplace add anthropics/claude-plugins-official || true
claude plugin marketplace add gborges0727/claude-plugins || true

claude plugin install gborges-standard@gborges --scope user || true

# Surface the result in the setup log. A dependency that fails to resolve
# leaves the bundle at 'failed to load' and is otherwise silent.
claude plugin list || true

exit 0
