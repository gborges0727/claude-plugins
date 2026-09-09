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
# rev: 33

set -u

# claude-plugins-official is a trusted marketplace name but is not registered
# in a fresh session VM, and nothing registers it later. Adding it here is
# what lets the bundle's dependencies resolve. With both marketplaces known,
# installing the bundle pulls its dependencies in, so this script needs no
# edit when the dependency set changes.
claude plugin marketplace add anthropics/claude-plugins-official || true
claude plugin marketplace add gborges0727/claude-plugins || true

claude plugin install gborges-standard@gborges --scope user || true

# A cloud VM signs in to an account that usually cannot run Claude Fable 5.1, so
# presetting the config here saves one wasted dispatch. Leave the line
# commented out unless it earns its keep, because the routing rule already
# re-sends the brief to opus-xhigh when fable-xhigh fails with a model error.
# bash "$(ls -d ~/.claude/plugins/cache/gborges/gborges-standard/*/ | tail -1)scripts/setup.sh" --fable off --codex off

# Claude Code reads the 'attribution' key from the VM's user settings when
# it builds the prompt. Unset, the prompt tells the model to add a
# Co-Authored-By trailer to every commit, a 'Generated with Claude Code'
# line to every PR body, and a claude.ai session link to both. Empty text
# and a false link stop the instruction at the source, which the plugin's
# hooks cannot do: they only catch the GitHub MCP tools, and a commit or a
# 'gh pr create' run through Bash passes them by. setup.sh --attribution
# off writes the same key. The write is inline here so it does not depend
# on the plugin's cache path. Other keys in the file stay as they were.
python3 - <<'PY' || true
import json
import os

path = os.path.expanduser("~/.claude/settings.json")
data = {}
try:
    with open(path) as handle:
        loaded = json.load(handle)
    if isinstance(loaded, dict):
        data = loaded
except (OSError, ValueError):
    data = {}

data["attribution"] = {"commit": "", "pr": "", "sessionUrl": False}

os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as handle:
    handle.write(json.dumps(data, indent=2) + "\n")
print("Wrote " + path + ": attribution off")
PY

# Surface the result in the setup log. A dependency that fails to resolve
# leaves the bundle at 'failed to load' and is otherwise silent.
claude plugin list || true

exit 0
