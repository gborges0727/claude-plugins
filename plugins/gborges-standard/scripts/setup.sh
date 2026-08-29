#!/bin/bash
# Writes the per-machine config file the gborges-standard hooks read,
# ~/.claude/gborges-standard.json. Two keys live there. 'fable' says whether
# this account can run the Claude Fable 5 model. When it is false, a hook
# rewrites the plugin's fable-xhigh subagent to opus-xhigh. 'codex' says
# whether the Codex CLI is installed and signed in on this machine. When it
# is true, the orchestrator hands fully specified mechanical work to the
# codex-delegate skill before it reaches for the sonnet-medium subagent.
#
# Run it with both flags and it writes the file without asking anything.
# Leave a flag out and it asks, or falls back to the default when nothing
# is there to answer.

set -u

usage() {
  cat <<'EOF'
Write ~/.claude/gborges-standard.json, the config the gborges-standard hooks read.

Usage: setup.sh [--fable on|off] [--codex on|off]

  --fable on|off   This account can run the Claude Fable 5 model. Default on.
  --codex on|off   The Codex CLI is available for delegated work. Default off.
  -h, --help       Print this text.

A flag you leave out is asked for when a terminal is attached. Otherwise the
default applies and the script says so on stderr. Keys already in the file
other than 'fable' and 'codex' are kept.
EOF
}

fable=""
codex=""

parse_onoff() {
  case "$2" in
    on|off) printf '%s' "$2" ;;
    *)
      printf 'setup.sh: %s takes on or off, got %s\n' "$1" "$2" >&2
      exit 2
      ;;
  esac
}

while [ $# -gt 0 ]; do
  case "$1" in
    --fable)
      if [ $# -lt 2 ]; then
        printf 'setup.sh: --fable needs a value\n' >&2
        usage >&2
        exit 2
      fi
      fable=$(parse_onoff --fable "$2") || exit 2
      shift 2
      ;;
    --codex)
      if [ $# -lt 2 ]; then
        printf 'setup.sh: --codex needs a value\n' >&2
        usage >&2
        exit 2
      fi
      codex=$(parse_onoff --codex "$2") || exit 2
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'setup.sh: unknown flag %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

# Ask for a value the flags did not supply. With no terminal on stdin there is
# nobody to ask, so take the default and print which one was taken.
ask() {
  local name="$1" default="$2" question="$3" answer=""
  if [ -t 0 ]; then
    printf '%s [%s]: ' "$question" "$default" >&2
    read -r answer || answer=""
    case "$answer" in
      "") printf '%s' "$default" ;;
      y|Y|yes|YES|on|ON) printf 'on' ;;
      n|N|no|NO|off|OFF) printf 'off' ;;
      *)
        printf 'setup.sh: %s takes on or off, got %s\n' "$name" "$answer" >&2
        exit 2
        ;;
    esac
  else
    printf 'setup.sh: no terminal to ask on, using %s=%s\n' "$name" "$default" >&2
    printf '%s' "$default"
  fi
}

if [ -z "$fable" ]; then
  fable=$(ask fable on 'Can this account run the Claude Fable 5 model? (on/off)') || exit 2
fi
if [ -z "$codex" ]; then
  codex=$(ask codex off 'Delegate mechanical work to the Codex CLI? (on/off)') || exit 2
fi

config_dir="${HOME}/.claude"
config_file="${config_dir}/gborges-standard.json"

mkdir -p "$config_dir" || exit 1

# Read what the file already holds, replace the two keys, write it back.
# Anything else in the file survives. A file that is missing or is not an
# object starts over as an empty object.
FABLE="$fable" CODEX="$codex" CONFIG_FILE="$config_file" python3 - <<'PY' || exit 1
import json
import os

path = os.environ["CONFIG_FILE"]
data = {}
try:
    with open(path) as handle:
        loaded = json.load(handle)
    if isinstance(loaded, dict):
        data = loaded
except (OSError, ValueError):
    data = {}

data["fable"] = os.environ["FABLE"] == "on"
data["codex"] = os.environ["CODEX"] == "on"

with open(path, "w") as handle:
    handle.write(json.dumps(data) + "\n")
PY

printf 'Wrote %s: %s\n' "$config_file" "$(tr -d '\n' < "$config_file")"
