#!/usr/bin/env python3
"""Decide which OpenAI model and effort a Codex delegation may run at.

Runs as a PreToolUse hook on two tools. The first is mcp__codex__codex,
the MCP call that starts a Codex thread. The second is Bash, where it
looks only at commands that run `codex exec`, the way the codex-delegate
skill starts a lane. Every other Bash command passes untouched. The skill
tells the main agent which model and effort to name, and this hook
enforces the one rule that costs the most when broken.

GPT-6 Astra costs 2.5 times what Sol costs per token. The skill's
escalation rung runs Astra at medium effort, and that runs on the
orchestrator's own judgment. Anything above medium (high, xhigh, max, or
ultra) runs only when the user asked for it by name in their latest
message. remind-writing-rules.py records whether that message used the
word "astra", and this hook reads the record. An Astra call above medium
with no such record comes back denied, and the reason tells the main
agent to send the same brief to Astra at medium. That is the same shape
as the Fable rule in route-spawns.py, with the effort as the line.

The hook also fills in the effort when the call left it out. Codex takes
the effort from its config, and a call without one runs at the model's
own default, which is low on Sol. Every rung but the escalation runs at
xhigh, so a missing effort becomes xhigh on Luna and Sol, and on Astra
when the user named it. On an Astra call the user did not name, a
missing effort becomes medium, the escalation rung's setting. An effort
the call did set is left alone, so a summoned Astra call at max stays at
max.

On the MCP tool the effort lives in the config argument as
model_reasoning_effort. On a `codex exec` command it is the `-c
model_reasoning_effort=...` flag, and the model is `-m` or `--model`. The
fill-in on a command inserts `-c model_reasoning_effort=<effort>` right
after the words `codex exec`, and changes nothing else in the command.

A call that names no model at all is left alone. Codex then runs the
orchestrator model from ~/.codex/config.toml, and the skill tells the main
agent to name a model on every call, so an unnamed call is a skill miss
rather than a cost the hook should guess at. A command the shell parser
cannot split is left alone too.

On any read failure the hook stays silent and the call proceeds.
"""

import json
import re
import shlex
import sys

try:
    import plugin_config
except ImportError:
    # Fail safe when the sibling module is missing. Astra reads as
    # unmentioned, so it runs at medium and nothing higher.
    class plugin_config:  # noqa: N801
        @staticmethod
        def read_astra(session_id):
            return False


MCP_TOOL = "mcp__codex__codex"

ASTRA_MODELS = ("gpt-6-astra",)

EFFORT_KEY = "model_reasoning_effort"

DEFAULT_EFFORT = "xhigh"

# The escalation rung, and the most an unsummoned Astra call may run at.
ASTRA_CAP = "medium"

# Efforts Astra may run at without the user naming it, lowest first.
WITHIN_CAP = ("none", "low", "medium")

DENY_REASON = (
    "GPT-6 Astra runs above medium effort only when the user's own message "
    "names Astra. This message did not, so send the same brief to "
    "gpt-6-astra at medium, the escalation rung, or to gpt-5.6-sol."
)

# Where a `codex exec` command begins. The fill-in inserts the effort flag
# right after this match.
EXEC_START = re.compile(r"\bcodex\s+exec\b")

# Tokens that end one shell command and begin the next.
COMMAND_BREAKS = ("&&", "||", ";", "|", "&")


def pick_effort(model, effort, summoned):
    """Return (decision, fill). decision is 'deny', 'fill', or None."""
    astra = model in ASTRA_MODELS
    if astra and not summoned and effort and effort not in WITHIN_CAP:
        return "deny", None
    if effort:
        return None, None
    return "fill", (ASTRA_CAP if astra and not summoned else DEFAULT_EFFORT)


def unquote(value):
    """Strip one layer of TOML string quotes from a -c value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_exec(command):
    """Find the model and effort a `codex exec` command names.

    Returns (found, model, effort). found is False when the command runs no
    `codex exec`, or when the shell parser cannot split it.
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False, None, None
    for start in range(len(tokens) - 1):
        if tokens[start] != "codex" or tokens[start + 1] != "exec":
            continue
        model = None
        effort = None
        i = start + 2
        while i < len(tokens) and tokens[i] not in COMMAND_BREAKS:
            tok = tokens[i]
            value = None
            if tok in ("-m", "--model") and i + 1 < len(tokens):
                model = tokens[i + 1]
                i += 2
                continue
            if tok.startswith("--model="):
                model = tok[len("--model=") :]
            elif tok in ("-c", "--config") and i + 1 < len(tokens):
                value = tokens[i + 1]
                i += 1
            elif tok.startswith("--config="):
                value = tok[len("--config=") :]
            elif tok.startswith("-c") and len(tok) > 2:
                value = tok[2:]
            if value and "=" in value:
                key, raw = value.split("=", 1)
                if key == EFFORT_KEY:
                    effort = unquote(raw)
                elif key == "model" and model is None:
                    model = unquote(raw)
            i += 1
        return True, model, effort
    return False, None, None


def reply(decision, reason, updated=None):
    out = {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }
    if updated is not None:
        out["updatedInput"] = updated
    json.dump({"hookSpecificOutput": out}, sys.stdout)


def handle_mcp(event, tool_input):
    model = tool_input.get("model")
    if not isinstance(model, str) or not model:
        return
    config = tool_input.get("config")
    if not isinstance(config, dict):
        config = {}
    effort = config.get(EFFORT_KEY)
    summoned = model in ASTRA_MODELS and plugin_config.read_astra(event.get("session_id"))
    decision, fill = pick_effort(model, effort, summoned)
    if decision == "deny":
        reply("deny", DENY_REASON)
    elif decision == "fill":
        updated = dict(tool_input)
        updated["config"] = dict(config, **{EFFORT_KEY: fill})
        reply("allow", f"Set {EFFORT_KEY} to {fill} on the Codex call.", updated)


def handle_bash(event, tool_input):
    command = tool_input.get("command")
    if not isinstance(command, str) or not EXEC_START.search(command):
        return
    found, model, effort = parse_exec(command)
    if not found or not model:
        return
    summoned = model in ASTRA_MODELS and plugin_config.read_astra(event.get("session_id"))
    decision, fill = pick_effort(model, effort, summoned)
    if decision == "deny":
        reply("deny", DENY_REASON)
    elif decision == "fill":
        flag = f" -c {EFFORT_KEY}={fill}"
        updated = dict(tool_input)
        updated["command"] = EXEC_START.sub(lambda m: m.group(0) + flag, command, count=1)
        reply("allow", f"Set {EFFORT_KEY} to {fill} on the codex exec command.", updated)


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    if not isinstance(event, dict):
        return
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return
    tool = event.get("tool_name")
    if tool == MCP_TOOL:
        handle_mcp(event, tool_input)
    elif tool == "Bash":
        handle_bash(event, tool_input)


if __name__ == "__main__":
    main()
