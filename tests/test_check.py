#!/usr/bin/env python3
"""Check the writing-voice scanner's paragraph advisory.

check.py is loaded from its path, so each test runs the same file the skill
runs. A case builds a small document, scans it, and looks for or against
the rule 4 paragraph advisory. Every sentence in the fixtures stays under
30 words, so the sentence advisory never fires and cannot mask a result.
"""

import importlib.util
import unittest
from pathlib import Path

CHECK = (
    Path(__file__).resolve().parent.parent
    / "plugins" / "gborges-standard" / "skills" / "writing-voice" / "scripts" / "check.py"
)
spec = importlib.util.spec_from_file_location("check", CHECK)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def sentence(words):
    """One plain sentence of exactly `words` words."""
    return " ".join(["word"] * (words - 1)) + " end."


def paragraph(words):
    """One line of 20-word sentences adding up to `words` words."""
    return " ".join(sentence(20) for _ in range(words // 20))


def paragraph_hits(text):
    return [hit for hit in check.scan(text, "t") if "overpacked paragraph" in hit]


class ParagraphAdvisory(unittest.TestCase):
    def test_a_long_paragraph_is_flagged_once_with_its_count(self):
        hits = paragraph_hits(paragraph(140))
        self.assertEqual(len(hits), 1)
        self.assertIn("140 words", hits[0])

    def test_a_paragraph_at_the_limit_is_not_flagged(self):
        self.assertEqual(paragraph_hits(paragraph(120)), [])

    def test_two_short_paragraphs_are_not_flagged(self):
        self.assertEqual(paragraph_hits(paragraph(80) + "\n\n" + paragraph(80)), [])

    def test_list_items_are_counted_one_at_a_time(self):
        text = "\n".join(f"- {sentence(20)}" for _ in range(8))
        self.assertEqual(paragraph_hits(text), [])

    def test_a_numbered_list_is_counted_one_item_at_a_time(self):
        text = "\n".join(f"{n}. {sentence(20)}" for n in range(1, 9))
        self.assertEqual(paragraph_hits(text), [])

    def test_a_long_list_item_is_flagged(self):
        hits = paragraph_hits("- " + paragraph(140))
        self.assertEqual(len(hits), 1)

    def test_a_fenced_block_splits_a_paragraph(self):
        text = paragraph(80) + "\n```\ncode\n```\n" + paragraph(80)
        self.assertEqual(paragraph_hits(text), [])

    def test_a_heading_does_not_join_the_paragraph_below(self):
        self.assertEqual(paragraph_hits("## Heading\n" + paragraph(80)), [])

    def test_wrapped_lines_count_as_one_paragraph(self):
        text = "\n".join(sentence(20) for _ in range(7))
        hits = paragraph_hits(text)
        self.assertEqual(len(hits), 1)
        self.assertIn("140 words", hits[0])

    def test_the_advisory_names_the_first_line_of_the_paragraph(self):
        text = paragraph(60) + "\n\n" + paragraph(140)
        hits = paragraph_hits(text)
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0].startswith("t:3:1 "), hits[0])


if __name__ == "__main__":
    unittest.main()
