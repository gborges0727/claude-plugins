#!/bin/bash
# Writes the per-machine config file the gborges-standard hooks read,
# ~/.claude/gborges-standard.json. Two keys live there. 'fable' says whether
# this account can run the Claude Fable 5.1 model. When it is false, a hook
# rewrites the plugin's fable-xhigh subagent to opus-xhigh. 'codex' says
# whether the Codex CLI is installed and signed in on this machine. When it
# is true, the orchestrator hands fully specified mechanical work to the
# codex-delegate skill before it reaches for the sonnet-medium subagent.
#
# A third flag, --codex-config, writes the Codex CLI's own model setup into
# ~/.codex: four agent files under ~/.codex/agents that mirror the plugin's
# four Claude subagents, the [agents] defaults that send every spawn to
# GPT-5.6 Terra at xhigh effort, the orchestrator model, and the footer
# status line. It defaults to on when a codex binary is on PATH.
#
# Run it with all flags and it writes the files without asking anything.
# Leave a flag out and it asks, or falls back to the default when nothing
# is there to answer.

set -u

usage() {
  cat <<'EOF'
Write ~/.claude/gborges-standard.json, the config the gborges-standard hooks read.

Usage: setup.sh [--fable on|off] [--codex on|off] [--codex-config on|off]

  --fable on|off         This account can run the Claude Fable 5.1 model. Default on.
  --codex on|off         The Codex CLI is available for delegated work. Default off.
  --codex-config on|off  Write the Codex CLI's model, subagent, and status line
                         config under ~/.codex. Default on when codex is on PATH.
  -h, --help             Print this text.

A flag you leave out is asked for when a terminal is attached. Otherwise the
default applies and the script says so on stderr. Keys already in the file
other than 'fable' and 'codex' are kept. In ~/.codex/config.toml only the
model, model_reasoning_effort, [agents], and [tui] entries are replaced.
EOF
}

fable=""
codex=""
codex_config=""

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
    --codex-config)
      if [ $# -lt 2 ]; then
        printf 'setup.sh: --codex-config needs a value\n' >&2
        usage >&2
        exit 2
      fi
      codex_config=$(parse_onoff --codex-config "$2") || exit 2
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
  fable=$(ask fable on 'Can this account run the Claude Fable 5.1 model? (on/off)') || exit 2
fi
if [ -z "$codex" ]; then
  codex=$(ask codex off 'Delegate mechanical work to the Codex CLI? (on/off)') || exit 2
fi
if [ -z "$codex_config" ]; then
  if command -v codex >/dev/null 2>&1; then codex_default=on; else codex_default=off; fi
  codex_config=$(ask codex-config "$codex_default" 'Write the Codex CLI model and status line config? (on/off)') || exit 2
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

[ "$codex_config" = "on" ] || exit 0

# The Codex side. Codex has no plugin field for agents or for config.toml,
# so this is the one place they get written. Each agent mirrors one Claude
# subagent: luna-xhigh takes fully specified edits like sonnet-medium,
# terra-xhigh is the default worker like opus-medium, sol-xhigh is the one
# escalation step like opus-xhigh, and astra-xhigh runs only when the user
# names it, like fable-xhigh. Terra is the default rather than Luna because
# OpenAI positions Luna for clear repeatable work and Terra as the
# all-rounder, Luna's long-context recall drops to 41% past 256K tokens, and
# Codex's catalog marks Luna multi_agent_version v1 while Sol, Terra, and
# Astra are v2, so a Sol orchestrator's spawn cannot land on Luna by model
# name.
codex_dir="${HOME}/.codex"
agents_dir="${codex_dir}/agents"
codex_config_file="${codex_dir}/config.toml"

mkdir -p "$agents_dir" || exit 1

write_agent() {
  local name="$1" model="$2" effort="$3" description="$4" instructions="$5"
  cat > "${agents_dir}/${name}.toml" <<EOF
# Written by gborges-standard setup.sh. Edits here are overwritten on the next run.
name = "${name}"
description = "${description}"
model = "${model}"
model_reasoning_effort = "${effort}"
developer_instructions = "${instructions}"
EOF
}

write_agent luna-xhigh gpt-5.6-luna xhigh \
  "GPT-5.6 Luna at xhigh effort. Use for an edit or a run whose brief names the exact change and a command that checks it, for parallel copies of one such task across files, and for fetching a named doc page outside the codebase. Never for reading code to reach a conclusion, and never for a brief whose files run past 272K tokens." \
  "You are a worker handling one fully specified unit of work from the orchestrating session. Run the check the brief names before you report. If the check fails or you cannot finish, say so plainly and quote the failing output instead of working around it."

write_agent terra-xhigh gpt-5.6-terra xhigh \
  "GPT-5.6 Terra at xhigh effort. The default for delegated work, and the floor for any task that reads code to reach a conclusion (an investigation, a diagnosis, a review, a design choice)." \
  "You are a general-purpose worker handling a delegated unit of work from the orchestrating session. When the brief names a check, run it before you report. If the check fails or you cannot finish, say so plainly and quote the failing output."

write_agent sol-xhigh gpt-5.6-sol xhigh \
  "GPT-5.6 Sol at xhigh effort. Use for a task that already failed once on terra-xhigh or luna-xhigh, for a task that is one long dependent chain the orchestrator cannot split into parallel pieces, and for a brief that must read past 272K tokens of context." \
  "You are a worker taking a hard unit of work from the orchestrating session. The brief may carry the exact output of a failed earlier attempt. Start from that output, not from the earlier approach. When the brief names a check, run it before you report, and quote the failing output if it still fails."

write_agent astra-xhigh gpt-6-astra xhigh \
  "GPT-6 Astra at xhigh effort. Runs only when the user's own message names astra-xhigh. Every other dispatch goes to sol-xhigh instead." \
  "You are the strongest worker available, summoned by the user for one hard unit of work. Take the whole task to the end. When the brief names a check, run it before you report, and quote the failing output if it still fails."

# The luna-medium name was retired, so a file left by an earlier run goes.
rm -f "${agents_dir}/luna-medium.toml"

# Replace the managed entries in config.toml and keep everything else:
# the top-level model and effort lines, the [agents] table, and the [tui]
# table. Each table is cut from its header to the next header. A file that
# is missing starts empty. The result is parsed back before it is written,
# so a broken file never lands.
CODEX_CONFIG_FILE="$codex_config_file" python3 - <<'PY' || exit 1
import os
import re
import tomllib

path = os.environ["CODEX_CONFIG_FILE"]
try:
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
except OSError:
    text = ""

HEADER = re.compile(r"^\s*\[")
MANAGED_TABLES = {"[agents]", "[tui]"}
MANAGED_KEYS = re.compile(r"^\s*(model|model_reasoning_effort)\s*=")

MANAGED_COMMENT = "# Written by gborges-standard setup.sh"

kept = []
skipping = False
seen_header = False
for line in text.splitlines():
    if line.startswith(MANAGED_COMMENT):
        continue
    if HEADER.match(line):
        seen_header = True
        skipping = line.strip() in MANAGED_TABLES
        if skipping:
            continue
    elif skipping:
        continue
    elif not seen_header and MANAGED_KEYS.match(line):
        continue
    kept.append(line)

# Top-level keys must sit above every table header, so the model lines go
# first and the two tables go last.
body = re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip("\n")
managed_top = (
    "# Written by gborges-standard setup.sh: orchestrator model.\n"
    'model = "gpt-5.6-sol"\n'
    'model_reasoning_effort = "medium"\n'
)
managed_tables = (
    "# Written by gborges-standard setup.sh: spawns default to Terra xhigh unless they name an agent in ~/.codex/agents.\n"
    "[agents]\n"
    'default_subagent_model = "gpt-5.6-terra"\n'
    'default_subagent_reasoning_effort = "xhigh"\n'
    "\n"
    "# Written by gborges-standard setup.sh: the Claude Code status line fields, in the same order.\n"
    "[tui]\n"
    'status_line = ["current-dir", "git-branch", "branch-changes", "model-with-reasoning", "context-used", "five-hour-limit", "weekly-limit"]\n'
    "status_line_use_colors = true\n"
)
out = managed_top + ("\n" + body + "\n" if body else "") + "\n" + managed_tables

parsed = tomllib.loads(out)
assert parsed["model"] == "gpt-5.6-sol"
assert parsed["agents"]["default_subagent_model"] == "gpt-5.6-terra"
assert len(parsed["tui"]["status_line"]) == 7

tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as handle:
    handle.write(out)
os.replace(tmp, path)
PY

printf 'Wrote %s and 4 agents in %s\n' "$codex_config_file" "$agents_dir"
