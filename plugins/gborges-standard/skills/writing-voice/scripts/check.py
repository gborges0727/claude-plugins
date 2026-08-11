#!/usr/bin/env python3
"""Literal scan for the writing-voice Pass 1 string list.

Reads one or more files, or stdin when given no paths, and prints every banned
string with the rule number it breaks, plus an advisory on every sentence over
30 words (rule 4, overpacked). Quoted and code text is masked before scanning:
fenced blocks, indented blocks, inline code spans, blockquote lines, table
rows, and URLs. That mirrors the "when the rules don't apply" section of
RULES.md, where the passes run on your own prose only.

    python3 check.py draft.md
    cat draft.md | python3 check.py

Exit code is 1 when anything is found, 0 when clean. Every hit is a report, not
a verdict: each rule carries carve-outs the script cannot evaluate.

scan_hits() returns the same findings as tuples, for callers that format them
themselves. The check-reply.py hook imports it to scan finished chat replies.
"""

from __future__ import annotations

import argparse
import re
import sys

# (rule number, regex, human label). Patterns are matched case-insensitively
# unless they carry an inline flag. Order within a rule does not matter.
PATTERNS: list[tuple[int, str, str]] = [
    # Rule 7, packaging.
    (7, r"\bimportantly\b", "Importantly"),
    (7, r"\bnotably\b", "Notably"),
    (7, r"it('?s| is) worth noting", "It's worth noting"),
    (7, r"it('?s| is) important to note", "It's important to note"),
    (7, r"it bears mentioning", "It bears mentioning"),
    (7, r"worth flagging", "worth flagging"),
    (7, r"\bcritically,", "Critically,"),
    (7, r"the good news is", "The good news is"),
    (7, r"the hard truth is", "The hard truth is"),
    (7, r"the reality is", "The reality is"),
    (7, r"the truth is", "The truth is"),
    (7, r"the upshot:", "The upshot:"),
    (7, r"a concrete consequence:", "A concrete consequence:"),
    (7, r"the key point:", "The key point:"),
    (7, r"and that'?s the key point", "and that's the key point"),
    (7, r"which is the important part", "which is the important part"),
    (7, r"and that'?s what matters here", "and that's what matters here"),
    (7, r"the takeaway being", "the takeaway being"),
    (7, r"you'?re right\b", "You're right"),
    (7, r"here'?s the thing", "Here's the thing"),
    (7, r"that said,", "That said,"),
    (7, r"that being said", "That being said"),
    (7, r"with that said", "With that said"),
    (7, r"to be clear,", "To be clear,"),
    (7, r"zooming out", "Zooming out"),
    (7, r"at its core", "at its core"),
    (7, r"at a high level", "at a high level"),
    (7, r"\bin essence\b", "In essence"),
    (7, r"^essentially,", "Essentially,"),
    (7, r"^fundamentally,", "Fundamentally,"),
    (7, r"simply put,", "Simply put,"),
    (7, r"first and foremost", "first and foremost"),
    # Rule 5, verdict adjectives with no payload.
    (5, r"non-?trivial", "non-trivial"),
    (5, r"\bnuanced\b", "nuanced"),
    (5, r"\bmultifaceted\b", "multifaceted"),
    # Rule 6, stand-in nouns and coined abstractions.
    (6, r"is where the", "is where the"),
    (6, r"north star", "north star"),
    (6, r"\bplaybook\b", "playbook"),
    (6, r"\blinchpin\b", "linchpin"),
    (6, r"\bbackbone\b", "backbone"),
    (6, r"\bcornerstone\b", "cornerstone"),
    (6, r"load-?bearing", "load-bearing"),
    (6, r"the lever\b", "the lever"),
    (6, r"\b(?:the|an?|biggest|big|key|real|huge|major) unlock\b", "the unlock"),
    (6, r"the lens\b", "the lens"),
    (6, r"center of gravity", "center of gravity"),
    (6, r"gold standard", "gold standard"),
    (6, r"known recipe", "known recipe"),
    # Rule 6 continued, borrowed mechanism names. Carve-outs: a literal
    # mailed envelope, a back-of-the-envelope estimate.
    (6, r"\benvelope", "envelope"),
    (6, r"\bflywheel", "flywheel"),
    # Rule 6 continued, tech-culture jargon as seasoning.
    (6, r"\bfootgun", "footgun"),
    (6, r"happy path", "happy path"),
    (6, r"sane defaults", "sane defaults"),
    (6, r"escape hatch", "escape hatch"),
    (6, r"\bgotcha", "gotcha"),
    (6, r"belt and suspenders", "belt and suspenders"),
    (6, r"\borthogonal", "orthogonal"),
    (6, r"\bdelve", "delve"),
    (6, r"rich tapestry", "rich tapestry"),
    (5, r"(?-i:(?:^|(?<=[.!?] ))(?:\*\*)?[A-Z][\w' -]{2,32}(?:\*\*)?: [a-z])", "label-colon opener"),
    # Rule 12, discrete sentences (em dash).
    (12, "—", "em dash"),
    # Rule 9, asserted authenticity.
    (9, r"\bhonestly\b", "honestly"),
    (9, r"\bhonest (?:answer|ceiling|read|take|assessment|state|verdict|truth)\b", "honest <noun>"),
    (9, r"\bgenuinely\b", "genuinely"),
    (9, r"real value", "real value"),
    (9, r"\bcredible\b", "credible"),
    # Rule 8, manufactured contrast.
    (8, r"not just\b", "not just"),
    (8, r"isn'?t about\b", "isn't about"),
    (8, r"it wasn'?t\b", "it wasn't"),
    (8, r"\bless\b[^.!?]{1,40}\bmore\b", "less ... more"),
    (8, r"\bsure,", "Sure, ... But"),
    (8, r"it'?s tempting to think", "It's tempting to think"),
    (8, r"the real (point|question|issue) is", "the real point is"),
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
TABLE_ROW = re.compile(r"^\s*\|")

# Rule 4 advisory: a sentence this long is a re-read risk, not a verdict.
LONG_SENTENCE_WORDS = 30
SENTENCE = re.compile(r"[^.!?]+(?:[.!?]+|$)")
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
        if in_fence or BLOCKQUOTE.match(line) or INDENTED.match(line) or TABLE_ROW.match(line):
            out.append(" " * len(line))
            continue
        masked = line
        for pattern in (INLINE_CODE, URL, MD_LINK_TARGET):
            masked = pattern.sub(lambda m: " " * len(m.group(0)), masked)
        out.append(masked)
    return "\n".join(out)


def scan_hits(text: str) -> list[tuple[int, int, int, str, str]]:
    """Return every hit as (line, column, rule number, label, matched text).

    The structured form other callers read. check-reply.py groups these into a
    one-line report under a chat reply, and scan() below formats them for the
    command line."""
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

    for line_no, line in enumerate(masked.split("\n"), 1):
        for sent in SENTENCE.finditer(line):
            words = sent.group(0).split()
            if len(words) > LONG_SENTENCE_WORDS:
                head = " ".join(words[:6])
                hits.append((
                    line_no,
                    sent.start() + 1,
                    4,
                    "overpacked sentence",
                    f"{len(words)} words: {head}...",
                ))

    hits.sort()
    return hits


def scan(text: str, source: str) -> list[str]:
    """Format every hit as one command-line report line."""
    return [
        f"{source}:{line}:{col}  rule {rule:<2} {label}  ({found!r})"
        for line, col, rule, label, found in scan_hits(text)
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
