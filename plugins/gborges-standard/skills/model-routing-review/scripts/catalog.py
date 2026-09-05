#!/usr/bin/env python3
"""Print the Codex CLI's model catalog as one line per model.

`codex debug models` prints a JSON document of several hundred kilobytes,
most of it the system prompt each model ships with. The routing review
needs eight fields from it: the slug, the display name, OpenAI's one-line
description, the default effort, the efforts the model accepts, the
working and maximum context windows, the multi-agent backend version, and
any retirement notice. This script prints those and nothing else, so the
review reads a screen instead of a dump.

Usage: python3 catalog.py [--json]

Without --json the output is a Markdown table. Hidden models (visibility
"hide") are listed last with the marker (hidden), since a hidden model can
still be named in a call.
"""

import json
import subprocess
import sys

FIELDS = (
    "slug",
    "display_name",
    "description",
    "default_reasoning_level",
    "efforts",
    "context_window",
    "max_context_window",
    "multi_agent_version",
    "retires",
)


def load():
    done = subprocess.run(
        ["codex", "debug", "models"], capture_output=True, text=True, check=False
    )
    if done.returncode != 0:
        sys.stderr.write(done.stderr)
        sys.exit(done.returncode)
    return json.loads(done.stdout)["models"]


def row(model):
    upgrade = model.get("upgrade") or {}
    retires = upgrade.get("retirement_at", "")
    if retires and upgrade.get("model"):
        retires = f"{retires[:10]} (use {upgrade['model']})"
    return {
        "slug": model.get("slug", ""),
        "display_name": model.get("display_name", ""),
        "description": model.get("description", ""),
        "default_reasoning_level": model.get("default_reasoning_level", ""),
        "efforts": " ".join(
            level.get("effort", "") for level in model.get("supported_reasoning_levels", [])
        ),
        "context_window": model.get("context_window", ""),
        "max_context_window": model.get("max_context_window", ""),
        "multi_agent_version": model.get("multi_agent_version", ""),
        "retires": retires,
        "hidden": model.get("visibility") == "hide",
    }


def main():
    rows = [row(m) for m in load()]
    rows.sort(key=lambda r: (r["hidden"], r["slug"]))
    if "--json" in sys.argv:
        json.dump(rows, sys.stdout, indent=1)
        return
    print("| " + " | ".join(FIELDS) + " |")
    print("|" + "---|" * len(FIELDS))
    for r in rows:
        slug = r["slug"] + (" (hidden)" if r["hidden"] else "")
        cells = [slug] + [str(r[f]) for f in FIELDS[1:]]
        print("| " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
