#!/usr/bin/env python3
"""Make Bear-live markup inert. Reads a document on stdin, writes it on stdout.

Wraps bare #refs and [[brackets]] in backticks so Bear shows them instead of
minting a global tag or a wikilink. Markdown headings, fenced code blocks, and
existing inline-code spans pass through untouched.

    python3 inert.py < doc.md | bearcli create "Title" --tags notes
"""
import re
import sys

# A # that opens a word, allowing the /#126 form inside #123/#126/#128.
# Trailing punctuation is excluded so Bear cannot absorb it into the tag name.
REF = re.compile(r"(?<![\w`#])#([A-Za-z0-9][\w.\-']*)")
WIKILINK = re.compile(r"\[\[([^\]\n]*)\]\]")
HEADING = re.compile(r"^\s{0,3}#{1,6}(\s|$)")
FENCE = re.compile(r"^\s*(```|~~~)")


def _split_heading(line: str) -> tuple[str, str]:
    """Return (heading marker, rest). Marker is empty on a non-heading line."""
    if not HEADING.match(line):
        return "", line
    indent = len(line) - len(line.lstrip())
    hashes = len(line[indent:]) - len(line[indent:].lstrip("#"))
    cut = indent + hashes
    return line[:cut], line[cut:]


def _neutralize(text: str) -> str:
    text = REF.sub(lambda m: f"`#{m.group(1)}`", text)
    return WIKILINK.sub(lambda m: f"`[[{m.group(1)}]]`", text)


def inert_line(line: str) -> str:
    marker, body = _split_heading(line)
    # Odd indexes are inside inline-code spans and are left as written.
    parts = body.split("`")
    for i in range(0, len(parts), 2):
        parts[i] = _neutralize(parts[i])
    return marker + "`".join(parts)


def inert(src: str) -> str:
    out = []
    in_fence = False
    for line in src.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
        else:
            out.append(line if in_fence else inert_line(line))
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.write(inert(sys.stdin.read()))
