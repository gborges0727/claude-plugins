#!/usr/bin/env python3
"""Decide which OpenAI model and effort a Codex delegation may run at.

Runs as a PreToolUse hook on the mcp__codex__codex tool, the call that
starts a Codex thread from Claude Code. The codex-delegate skill tells the
main agent which model and effort to name in that call, and this hook
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
the effort from the config argument, and a call without one runs at the
model's own default, which is low on Sol. Every rung but the escalation
runs at xhigh, so a missing effort becomes xhigh on Luna and Sol, and on
Astra when the user named it. On an Astra call the user did not name, a
missing effort becomes medium, the escalation rung's setting. An effort
the call did set is left alone, so a summoned Astra call at max stays at
max.

A call that names no model at all is left alone too. Codex then runs the
orchestrator model from ~/.codex/config.toml, and the skill tells the main
agent to name a model on every call, so an unnamed call is a skill miss
rather than a cost the hook should guess at.

On any read failure the hook stays silent and the call proceeds.
"""

import json
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


TOOL = "mcp__codex__codex"

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


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    if not isinstance(event, dict) or event.get("tool_name") != TOOL:
        return

    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return
    model = tool_input.get("model")
    if not isinstance(model, str) or not model:
        return

    config = tool_input.get("config")
    if not isinstance(config, dict):
        config = {}
    effort = config.get(EFFORT_KEY)

    summoned = model in ASTRA_MODELS and plugin_config.read_astra(event.get("session_id"))

    if model in ASTRA_MODELS and not summoned and effort and effort not in WITHIN_CAP:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": DENY_REASON,
                }
            },
            sys.stdout,
        )
        return

    if effort:
        return

    fill = ASTRA_CAP if model in ASTRA_MODELS and not summoned else DEFAULT_EFFORT
    updated = dict(tool_input)
    updated["config"] = dict(config, **{EFFORT_KEY: fill})
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": f"Set {EFFORT_KEY} to {fill} on the Codex call.",
                "updatedInput": updated,
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
