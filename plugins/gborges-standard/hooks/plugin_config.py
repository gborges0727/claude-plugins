#!/usr/bin/env python3
"""Read the per-machine settings the hooks in this folder consult.

Two settings live outside the repo because they differ per machine. The
"fable" key says whether the Fable model is available here. The "codex" key
says whether this machine may hand coding subtasks to the Codex CLI. The
settings file is ~/.claude/gborges-standard.json and holds one flat object,
for example {"fable": true, "codex": false}. The setup script writes it.
Nothing in this module writes it.

load() always returns both keys. A missing file, a file that will not read,
text that is not JSON, JSON that is not an object, and a missing or
non-boolean key all fall back to fable = True and codex = False. Hooks read
this on every event, so a broken file must never stop a spawn or a turn.

The same folder also tracks whether the user's latest message named the
Fable agent. mention_from_prompt() decides that from the message text,
write_mention() records the answer for one session, and read_mention()
reports it back. The record is one file per session under
~/.claude/gborges-standard/state, holding the single character 1 or 0. The
UserPromptSubmit hook rewrites it on every message, so it always describes
the latest message and never an earlier one. A session with no file counts
as no mention.
"""

import json
from pathlib import Path

CONFIG = ".claude/gborges-standard.json"

STATE = ".claude/gborges-standard/state"

DEFAULTS = {"fable": True, "codex": False}

# The three ways a user can name the Fable agent in a message. The first is
# what Claude Code inserts for an @-mention of an agent. The other two are
# what a person types by hand.
MENTIONS = (
    "@agent-fable-xhigh",
    '@"fable-xhigh (agent)"',
    "@gborges-standard:fable-xhigh",
)


def load():
    """Return {"fable": bool, "codex": bool}, defaulting on any problem."""
    settings = dict(DEFAULTS)
    try:
        text = (Path.home() / CONFIG).read_text(encoding="utf-8")
    except OSError:
        return settings
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return settings
    if not isinstance(parsed, dict):
        return settings
    for key in settings:
        if isinstance(parsed.get(key), bool):
            settings[key] = parsed[key]
    return settings


def mention_from_prompt(prompt):
    """Say whether this message text names the Fable agent."""
    if not isinstance(prompt, str):
        return False
    return any(form in prompt for form in MENTIONS)


def _record_path(session_id):
    # A session id reaches this hook from outside, so strip anything that
    # would climb out of the state folder or name a file elsewhere.
    safe = "".join(c for c in str(session_id) if c.isalnum() or c in "-_")
    if not safe:
        return None
    return Path.home() / STATE / f"fable-mention-{safe}"


def write_mention(session_id, mentioned):
    """Record for this session whether the latest message named Fable."""
    path = _record_path(session_id)
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("1" if mentioned else "0", encoding="utf-8")
    except OSError:
        pass


def read_mention(session_id):
    """Report whether this session's latest message named Fable."""
    path = _record_path(session_id)
    if path is None:
        return False
    try:
        return path.read_text(encoding="utf-8").strip() == "1"
    except OSError:
        return False
