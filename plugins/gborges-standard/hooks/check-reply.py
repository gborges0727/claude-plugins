#!/usr/bin/env python3
"""Scan every finished chat reply against the writing-voice string list.

Runs as a MessageDisplay hook. The writing-voice skill covers file
deliverables, and an ordinary chat reply gets the output style with nothing
checking it. This hook closes that gap: it reassembles each assistant message
and appends one line naming the rules the reply broke.

MessageDisplay fires once per streamed chunk, and each fire is a separate
process carrying message_id, index, a final flag, and this chunk's delta (a
fragment, not the whole message). So the hook writes every delta to a buffer
file keyed by message_id, and scans only on the chunk where final is true,
once the whole reply is known.

Returning displayContent replaces what that chunk puts on screen, so the final
chunk is re-emitted with the report appended. Earlier chunks are passed through
untouched, which keeps streaming intact.

The report changes the screen only. The transcript and what Claude reads keep
the original text, so a hit never edits a reply and never reaches the model.
Every hit is a report and not a verdict, the same as on the command line: the
rules carry carve-outs the scan cannot evaluate.

Fail-open contract: on any problem (the switch is off, the event will not
parse, check.py will not import, the buffer will not write), the hook prints
nothing and exits 0, which leaves the reply on screen exactly as Claude wrote
it. A display hook must never be able to swallow an answer. Keep every exit
path in this file that way.

Config:
  WRITING_VOICE_CHECK  1|0  master switch (default 1)
  WRITING_VOICE_MIN_CHARS   skip replies with less prose than this, code
                            stripped (default 200)
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

CHECK_PY = (
    Path(__file__).resolve().parent.parent
    / "skills" / "writing-voice" / "scripts" / "check.py"
)

BUFFER_ROOT = Path(os.environ.get("TMPDIR", "/tmp")) / "writing-voice-check"

# Buffers left behind by an interrupted message, swept on a later run.
STALE_SECONDS = 30 * 60

# Distinct rule-and-label pairs named in the report before it stops listing.
MAX_REPORTED = 6

RULE = "\n\n────────────────────────\nwriting-voice: "

FENCE = re.compile(r"^\s*(```|~~~)")


def emit(text: str) -> None:
    """Replace this chunk's on-screen text and stop."""
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "MessageDisplay",
                "displayContent": text,
            }
        },
        sys.stdout,
    )
    sys.exit(0)


def load_scan():
    """Reuse scan_hits() from the skill's check.py, so the string list keeps
    one source. The filename has a hyphen-free name but sits outside any
    package, so it is loaded by path."""
    spec = importlib.util.spec_from_file_location("writing_voice_check", CHECK_PY)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.scan_hits


def prose_length(text: str) -> int:
    """Count non-space characters outside fenced code blocks."""
    total = 0
    in_fence = False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            total += len(line) - line.count(" ") - line.count("\t")
    return total


def sweep(root: Path) -> None:
    """Delete buffers older than STALE_SECONDS, then the empty session
    directories they leave behind."""
    cutoff = time.time() - STALE_SECONDS
    for session in root.iterdir():
        if not session.is_dir():
            continue
        for message in session.iterdir():
            if message.is_dir() and message.stat().st_mtime < cutoff:
                shutil.rmtree(message, ignore_errors=True)
        try:
            session.rmdir()
        except OSError:
            pass


def quote(name: str) -> str:
    """Reduce an id to characters that are safe in one path component."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)[:128] or "unnamed"


def report(hits) -> str:
    """Name each rule the reply broke, worst-repeated first, as one line."""
    counts = Counter((rule, label) for _, _, rule, label, _ in hits)
    ranked = counts.most_common()
    parts = []
    for (rule, label), count in ranked[:MAX_REPORTED]:
        tail = f" x{count}" if count > 1 else ""
        parts.append(f"rule {rule} {label}{tail}")
    remaining = len(ranked) - MAX_REPORTED
    if remaining > 0:
        parts.append(f"and {remaining} more")
    return RULE + ", ".join(parts)


def main() -> None:
    if os.environ.get("WRITING_VOICE_CHECK", "1") != "1":
        return

    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    if not isinstance(event, dict):
        return

    message_id = event.get("message_id")
    if not message_id:
        return
    session_id = event.get("session_id") or "nosession"
    delta = event.get("delta") or ""
    index = event.get("index")
    index = index if isinstance(index, int) and index >= 0 else 0

    # Names sort in chunk order, so the reply reassembles by reading the
    # directory sorted. Path components come from ids, so they are quoted
    # against a stray separator.
    directory = BUFFER_ROOT / quote(session_id) / quote(str(message_id))
    try:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{index:08d}.part").write_text(delta, encoding="utf-8")
    except OSError:
        return

    if event.get("final") is not True:
        return

    try:
        sweep(BUFFER_ROOT)
    except OSError:
        pass

    try:
        parts = sorted(directory.glob("*.part"))
        full = "".join(part.read_text(encoding="utf-8") for part in parts)
    except OSError:
        return
    finally:
        shutil.rmtree(directory, ignore_errors=True)

    try:
        minimum = int(os.environ.get("WRITING_VOICE_MIN_CHARS", "200"))
    except ValueError:
        minimum = 200
    if prose_length(full) < minimum:
        return

    try:
        scan_hits = load_scan()
    except Exception:
        return
    if scan_hits is None:
        return

    try:
        hits = scan_hits(full)
    except Exception:
        return
    if not hits:
        return

    emit(delta + report(hits))


if __name__ == "__main__":
    main()
