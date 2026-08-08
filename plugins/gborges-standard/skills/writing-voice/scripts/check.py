#!/usr/bin/env python3
"""Literal scan for the writing-voice Pass 1 string list.

Reads one or more files, or stdin when given no paths, and prints every banned
string with the rule number it breaks. Quoted and code text is masked before
scanning: fenced blocks, indented blocks, inline code spans, blockquote lines,
and URLs. That mirrors the "when the rules don't apply" section of SKILL.md,
where the passes run on your own prose only.

    python3 check.py draft.md
    cat draft.md | python3 check.py

Exit code is 1 when anything is found, 0 when clean. Every hit is a report, not
a verdict: each rule carries carve-outs the script cannot evaluate.
"""

from __future__ import annotations

import argparse
import re
import sys

# (rule number, regex, human label). Patterns are matched case-insensitively
# unless they carry an inline flag. Order within a rule does not matter.
PATTERNS: list[tuple[int, str, str]] = [
    # Rule 1, packaging.
    (1, r"\bimportantly\b", "Importantly"),
    (1, r"\bnotably\b", "Notably"),
    (1, r"it'?s worth noting", "It's worth noting"),
    (1, r"it'?s important to note", "It's important to note"),
    (1, r"it bears mentioning", "It bears mentioning"),
    (1, r"worth flagging", "worth flagging"),
    (1, r"\bcritically,", "Critically,"),
    (1, r"the good news is", "The good news is"),
    (1, r"the hard truth is", "The hard truth is"),
    (1, r"the reality is", "The reality is"),
    (1, r"the truth is", "The truth is"),
    (1, r"the upshot:", "The upshot:"),
    (1, r"a concrete consequence:", "A concrete consequence:"),
    (1, r"the key point:", "The key point:"),
    (1, r"and that'?s the key point", "and that's the key point"),
    (1, r"which is the important part", "which is the important part"),
    (1, r"and that'?s what matters here", "and that's what matters here"),
    (1, r"the takeaway being", "the takeaway being"),
    (1, r"honest answer", "Honest answer"),
    (1, r"you'?re right\b", "You're right"),
    (1, r"here'?s the thing", "Here's the thing"),
    (1, r"that said,", "That said,"),
    (1, r"that being said", "That being said"),
    (1, r"with that said", "With that said"),
    (1, r"to be clear,", "To be clear,"),
    (1, r"zooming out", "Zooming out"),
    (1, r"at its core", "at its core"),
    (1, r"at a high level", "at a high level"),
    (1, r"\bin essence\b", "In essence"),
    (1, r"^essentially,", "Essentially,"),
    (1, r"^fundamentally,", "Fundamentally,"),
    (1, r"simply put,", "Simply put,"),
    (1, r"first and foremost", "first and foremost"),
    # Rule 2, no payload.
    (2, r"non-?trivial", "non-trivial"),
    (2, r"\bnuanced\b", "nuanced"),
    (2, r"\bmultifaceted\b", "multifaceted"),
    # Rule 3, stand-in nouns.
    (3, r"is where the", "is where the"),
    (3, r"north star", "north star"),
    (3, r"\bplaybook\b", "playbook"),
    (3, r"\blinchpin\b", "linchpin"),
    (3, r"\bbackbone\b", "backbone"),
    (3, r"\bcornerstone\b", "cornerstone"),
    (3, r"load-?bearing", "load-bearing"),
    (3, r"the lever\b", "the lever"),
    (3, r"the unlock\b", "the unlock"),
    (3, r"the lens\b", "the lens"),
    (3, r"center of gravity", "center of gravity"),
    (3, r"gold standard", "gold standard"),
    (3, r"known recipe", "known recipe"),
    # Rule 3, tech-culture jargon as seasoning.
    (3, r"\bfootgun", "footgun"),
    (3, r"happy path", "happy path"),
    (3, r"sane defaults", "sane defaults"),
    (3, r"escape hatch", "escape hatch"),
    (3, r"\bgotcha", "gotcha"),
    (3, r"belt and suspenders", "belt and suspenders"),
    (3, r"\borthogonal", "orthogonal"),
    (3, r"\bdelve", "delve"),
    (3, r"rich tapestry", "rich tapestry"),
    # Rule 4, discrete sentences.
    (4, "—", "em dash"),
    # Rule 7, asserted authenticity.
    (7, r"\bhonestly\b", "honestly"),
    (7, r"\bgenuinely\b", "genuinely"),
    (7, r"real value", "real value"),
    (7, r"\bcredible\b", "credible"),
    # Rule 9, manufactured contrast.
    (9, r"not just\b", "not just"),
    (9, r"isn'?t about\b", "isn't about"),
    (9, r"it wasn'?t\b", "it wasn't"),
    (9, r"\bless\b[^.!?]{1,40}\bmore\b", "less ... more"),
    (9, r"\bsure,", "Sure, ... But"),
    (9, r"it'?s tempting to think", "It's tempting to think"),
    (9, r"the real (point|question|issue) is", "the real point is"),
    # Rule 11, openers and closers.
    (11, r"you'?re absolutely", "You're absolutely"),
    (11, r"great question", "Great question"),
    (11, r"great point", "Great point"),
    (11, r"\blet me\b", "Let me"),
    (11, r"looking at your", "Looking at your"),
    (11, r"to answer your question", "To answer your question"),
    (11, r"i'?ll go ahead and", "I'll go ahead and"),
    (11, r"let'?s (dive in|get started)", "Let's dive in"),
    (11, r"^(sure|certainly|absolutely|of course|perfect|excellent)!", "Sure!"),
    (11, r"uh oh", "Uh oh"),
    (11, r"\boh no\b", "Oh no"),
    (11, r"there seems to be", "There seems to be"),
    (11, r"something went wrong", "Something went wrong"),
    (11, r"would you like me to", "Would you like me to"),
    (11, r"happy to\b", "Happy to"),
    (11, r"let me know if", "Let me know if"),
    (11, r"let me know how it goes", "Let me know how it goes"),
    (11, r"just say the word", "just say the word"),
    (11, r"hope (this|that) helps", "Hope this helps"),
    (11, r"feel free to ask", "Feel free to ask"),
    (11, r"don'?t hesitate", "Don't hesitate"),
    (11, r"i'?d be happy to", "I'd be happy to"),
    (
        11,
        "["
        "\U0001f300-\U0001faff"
        "☀-➿"
        "⬀-⯿"
        "]",
        "emoji",
    ),
]

COMPILED = [
    (rule, re.compile(pattern, re.IGNORECASE | re.MULTILINE), label)
    for rule, pattern, label in PATTERNS
]

FENCE = re.compile(r"^\s*(```|~~~)")
BLOCKQUOTE = re.compile(r"^\s*>")
INDENTED = re.compile(r"^(\t| {4,})\S")
INLINE_CODE = re.compile(r"`[^`\n]*`")
URL = re.compile(r"<?\bhttps?://\S+>?")
MD_LINK_TARGET = re.compile(r"\]\([^)]*\)")


def mask(text: str) -> str:
    """Blank out quoted and code regions, preserving line and column offsets."""
    lines = text.split("\n")
    out: list[str] = []
    in_fence = False
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(" " * len(line))
            continue
        if in_fence or BLOCKQUOTE.match(line) or INDENTED.match(line):
            out.append(" " * len(line))
            continue
        masked = line
        for pattern in (INLINE_CODE, URL, MD_LINK_TARGET):
            masked = pattern.sub(lambda m: " " * len(m.group(0)), masked)
        out.append(masked)
    return "\n".join(out)


def scan(text: str, source: str) -> list[str]:
    masked = mask(text)
    starts = [0]
    for line in masked.split("\n"):
        starts.append(starts[-1] + len(line) + 1)

    def position(offset: int) -> tuple[int, int]:
        lo, hi = 0, len(starts) - 1
        while lo < hi - 1:
            mid = (lo + hi) // 2
            if starts[mid] <= offset:
                lo = mid
            else:
                hi = mid
        return lo + 1, offset - starts[lo] + 1

    hits: list[tuple[int, int, int, str, str]] = []
    for rule, pattern, label in COMPILED:
        for match in pattern.finditer(masked):
            line, col = position(match.start())
            hits.append((line, col, rule, label, match.group(0).strip()))

    hits.sort()
    return [
        f"{source}:{line}:{col}  rule {rule:<2} {label}  ({found!r})"
        for line, col, rule, label, found in hits
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan prose for the writing-voice Pass 1 string list."
    )
    parser.add_argument("paths", nargs="*", help="files to scan; stdin when omitted")
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="exit code only, no output"
    )
    args = parser.parse_args()

    reports: list[str] = []
    if args.paths:
        for path in args.paths:
            try:
                with open(path, encoding="utf-8") as handle:
                    reports.extend(scan(handle.read(), path))
            except OSError as error:
                print(f"{path}: {error}", file=sys.stderr)
                return 2
    else:
        reports.extend(scan(sys.stdin.read(), "<stdin>"))

    if not args.quiet:
        for report in reports:
            print(report)
        if reports:
            print(f"\n{len(reports)} hit(s). Each carries carve-outs; read the rule.")
    return 1 if reports else 0

if __name__ == "__main__":
    sys.exit(main())
