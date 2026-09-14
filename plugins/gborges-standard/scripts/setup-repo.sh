#!/bin/bash
# Writes the per-repo config file the document-writing skills read,
# .claude/gborges-standard.json at the repo root. Two keys live there.
# 'docs' names the folder that specs, tickets, maps, research notes,
# handoffs, and routine specs go under. 'tracker' says whether specs and
# tickets also become GitHub issues ('github') or stay as files ('files').
# reference/output-locations.md in the plugin lists what each skill writes
# and where, and what happens when the file is missing.
#
# Run it with both flags and it writes the file without asking anything.
# Leave a flag out and it asks, or falls back to the default when nothing
# is there to answer.

set -u

usage() {
  cat <<'EOF'
Write .claude/gborges-standard.json at the repo root, the per-repo config the
document-writing skills read.

Usage: setup-repo.sh [--docs FOLDER] [--tracker files|github]

  --docs FOLDER          Folder that specs, research notes, handoffs, maps, and
                         routine specs go under. Default docs.
  --tracker files|github Whether specs and tickets also become GitHub issues.
                         Default files.
  -h, --help             Print this text.

The file goes at the top of the git checkout that contains the working
directory, or in the working directory when it is not inside a git checkout.
Keys already in the file other than 'docs' and 'tracker' are kept.
EOF
}

docs=""
tracker=""

while [ $# -gt 0 ]; do
  case "$1" in
    --docs)
      if [ $# -lt 2 ]; then
        printf 'setup-repo.sh: --docs needs a value\n' >&2
        usage >&2
        exit 2
      fi
      docs="$2"
      shift 2
      ;;
    --tracker)
      if [ $# -lt 2 ]; then
        printf 'setup-repo.sh: --tracker needs a value\n' >&2
        usage >&2
        exit 2
      fi
      case "$2" in
        files|github) tracker="$2" ;;
        *)
          printf 'setup-repo.sh: --tracker takes files or github, got %s\n' "$2" >&2
          exit 2
          ;;
      esac
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'setup-repo.sh: unknown argument %s\n' "$1" >&2
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
    if [ -z "$answer" ]; then
      printf '%s' "$default"
    else
      printf '%s' "$answer"
    fi
  else
    printf 'setup-repo.sh: no terminal to ask on, using %s=%s\n' "$name" "$default" >&2
    printf '%s' "$default"
  fi
}

if [ -z "$docs" ]; then
  docs=$(ask docs docs 'Folder for specs, research notes, handoffs, and routine specs') || exit 2
fi
if [ -z "$tracker" ]; then
  tracker=$(ask tracker files 'Also open GitHub issues for specs and tickets? (files/github)') || exit 2
  case "$tracker" in
    files|github) ;;
    *)
      printf 'setup-repo.sh: tracker takes files or github, got %s\n' "$tracker" >&2
      exit 2
      ;;
  esac
fi

root=$(git rev-parse --show-toplevel 2>/dev/null) || root="$PWD"
config_dir="${root}/.claude"
config_file="${config_dir}/gborges-standard.json"

mkdir -p "$config_dir" || exit 1

# Every other key in the file stays as it was. A file that is missing or is
# not an object starts over as an empty object.
DOCS="$docs" TRACKER="$tracker" CONFIG_FILE="$config_file" python3 - <<'PY' || exit 1
import json
import os

path = os.environ["CONFIG_FILE"]
data = {}
try:
    with open(path, encoding="utf-8") as handle:
        loaded = json.load(handle)
    if isinstance(loaded, dict):
        data = loaded
except (OSError, ValueError):
    pass

data["docs"] = os.environ["DOCS"]
data["tracker"] = os.environ["TRACKER"]

with open(path, "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2)
    handle.write("\n")
PY

printf 'Wrote %s: docs %s, tracker %s\n' "$config_file" "$docs" "$tracker"
