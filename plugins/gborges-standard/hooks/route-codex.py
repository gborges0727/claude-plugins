#!/usr/bin/env python3
"""Decide which OpenAI model a Codex delegation may run on.

Runs as a PreToolUse hook on the mcp__codex__codex tool, the call that
starts a Codex thread from Claude Code. The codex-delegate skill tells the
main agent which model to name in that call, and this hook enforces the
one rule that costs the most when broken.

GPT-6 Astra costs what Fable costs per token and drains the ChatGPT
allowance faster than Sol, so it runs only when the user asked for it by
name in their latest message. remind-writing-rules.py records whether that
message used the word "astra", and this hook reads the record. An Astra
call with no such record comes back denied, and the reason tells the main
agent to send the same brief to Sol instead. That is the same shape as the
Fable rule in route-spawns.py.

The hook also fills in the reasoning effort when the call left it out.
Codex takes the effort from the config argument, and a call without one
runs at the model's own default, which is low on Sol. Every rung in the
skill's table runs at xhigh, so a missing effort becomes xhigh. An effort
the call did set is left alone, so the user can ask for max by name and
get it.

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
    # unmentioned and is refused, and every other call runs as before.
    class plugin_config:  # noqa: N801
        @staticmethod
        def read_astra(session_id):
            return False


TOOL = "mcp__codex__codex"

ASTRA_MODELS = ("gpt-6-astra",)

EFFORT_KEY = "model_reasoning_effort"

DEFAULT_EFFORT = "xhigh"

DENY_REASON = (
    "GPT-6 Astra runs only when the user's own message names Astra. This "
    "message did not, so send the same brief to gpt-5.6-sol instead."
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

    if model in ASTRA_MODELS and not plugin_config.read_astra(event.get("session_id")):
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

    config = tool_input.get("config")
    if not isinstance(config, dict):
        config = {}
    if config.get(EFFORT_KEY):
        return

    updated = dict(tool_input)
    updated["config"] = dict(config, **{EFFORT_KEY: DEFAULT_EFFORT})
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": f"Set {EFFORT_KEY} to {DEFAULT_EFFORT} on the Codex call.",
                "updatedInput": updated,
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
