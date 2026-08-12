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
    # Rule 7 continued, a question you ask and then answer yourself. The
    # lookbehind keeps this to sentence-initial noun-phrase questions, so a
    # real question ("Should we cache this?") does not match.
    (7, r"(?:^|(?<=[.!?] ))(?:\*\*)?(?:and )?the [\w' -]{2,30}\?", "self-answered question"),
    (7, r"why does (?:this|that|it) matter\?", "Why does this matter?"),
    (7, r"what does (?:this|that|it) mean\?", "What does this mean?"),
    (7, r"so,? what\?", "So what?"),
    (7, r"read that again", "Read that again"),
    (7, r"let that sink in", "Let that sink in"),
    # Rule 7 continued, a counted preview announcing a list it does not deliver.
    (
        7,
        r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+) things?\s+"
        r"(?:will|to|that|you|can|are|here)\b",
        "counted preview",
    ),
    (
        7,
        r"there are (?:two|three|four|five|six|seven|eight|nine|ten|\d+) "
        r"(?:things|reasons|ways|problems|issues|places|cases|gotchas)",
        "counted preview",
    ),
    # Rule 7 continued, a stakes flag that ranks an item without a reason.
    (7, r"the (?:one|ones) that matters?\b", "the one that matters"),
    (7, r"is the important (?:one|part)\b", "is the important one"),
    (7, r"what (?:really |actually )?matters (?:here )?is\b", "what matters is"),
    (7, r"the (?:big|main) one (?:is|here)\b", "the big one is"),
    (7, r"the main thing (?:is|here)\b", "the main thing is"),
    (7, r"the (?:key|critical) (?:issue|one|item|question) (?:is|here)\b", "the key issue is"),
    # Rule 2, vivid metaphors standing in for the failure.
    (2, r"\bbite you\b", "bite you"),
    (2, r"come back to bite", "come back to bite"),
    (2, r"blow up in your face", "blow up in your face"),
    (2, r"shoot yourself in the foot", "shoot yourself in the foot"),
    # Rule 10, repeated rhythm standing in for content.
    (10, r"\bno [\w-]+\.\s+no [\w-]+\.", "repeated fragment shape"),
    (10, r"\bstop [\w-]+\.\s+start [\w-]+\.", "repeated fragment shape"),
    (10, r"\bbecame [\w -]{1,24}\.\s+\w+ became\b", "escalating ladder"),
    # Rule 5, verdict adjectives with no payload.
    (5, r"non-?trivial", "non-trivial"),
    # Rule 5 continued, naming a change's category instead of the change.
    (
        5,
        r"\b(?:is|are|was|were)\s+(?:purely\s+|mostly\s+|just\s+|mainly\s+)?"
        r"(?:structural|architectural|cosmetic|mechanical|conceptual|philosophical)\b",
        "category instead of the change",
    ),
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
