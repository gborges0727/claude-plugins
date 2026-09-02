#!/usr/bin/env python3
"""Check the two hooks that route subagent dispatches.

Each test runs a hook the way Claude Code runs it. The hook starts as its
own python3 process, reads one event as JSON on stdin, and writes at most
one JSON object to stdout. HOME points at a fresh temporary directory, so
every test writes its own ~/.claude/gborges-standard.json and its own
mention records under ~/.claude/gborges-standard/state.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent / "plugins" / "gborges-standard" / "hooks"
ROUTE = HOOKS / "route-spawns.py"
REMIND = HOOKS / "remind-writing-rules.py"

FABLE = "gborges-standard:fable-xhigh"
OPUS = "gborges-standard:opus-xhigh"
OPUS_MEDIUM = "gborges-standard:opus-medium"

# A phrase from the long-output note that only a Fable spawn receives.
LONG_OUTPUT = "as reasoning and then again as a reply"


def run_hook(script, event, home):
    """Run one hook on one event and return its parsed stdout, or None."""
    env = dict(os.environ)
    env["HOME"] = str(home)
    env.pop("WRITING_VOICE_REMIND", None)
    done = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
    )
    assert done.returncode == 0, done.stderr
    out = done.stdout.strip()
    if not out:
        return None
    return json.loads(out)


class HookCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        (self.home / ".claude").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def write_config(self, text):
        (self.home / ".claude" / "gborges-standard.json").write_text(text, encoding="utf-8")

    def submit(self, prompt, session_id="s1"):
        return run_hook(
            REMIND,
            {"session_id": session_id, "prompt": prompt, "hook_event_name": "UserPromptSubmit"},
            self.home,
        )

    def spawn(self, subagent_type, session_id="s1", prompt="Do the work.", transcript=None):
        event = {
            "session_id": session_id,
            "tool_name": "Agent",
            "tool_input": {"subagent_type": subagent_type, "prompt": prompt},
        }
        if transcript is not None:
            event["transcript_path"] = str(transcript)
        return run_hook(ROUTE, event, self.home)

    def write_transcript(self, model, name="t.jsonl"):
        """Write a transcript whose newest reply came from the given model."""
        path = self.home / name
        lines = [
            json.dumps({"type": "user", "message": {"role": "user", "content": "hi"}}),
            json.dumps({"type": "assistant", "message": {"model": "claude-sonnet-5", "content": []}}),
            json.dumps({"type": "user", "message": {"role": "user", "content": "more"}}),
            json.dumps({"type": "assistant", "message": {"model": model, "content": []}}),
            json.dumps({"type": "user", "message": {"role": "user", "content": "go"}}),
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path


class FableMentionRule(HookCase):
    def test_fable_without_a_mention_is_denied(self):
        out = self.spawn(FABLE)
        block = out["hookSpecificOutput"]
        self.assertEqual(block["permissionDecision"], "deny")
        self.assertIn(OPUS, block["permissionDecisionReason"])

    def test_bare_fable_name_without_a_mention_is_denied(self):
        out = self.spawn("fable-xhigh")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_fable_after_a_mention_runs_and_gets_the_rules(self):
        self.submit("Please use @agent-fable-xhigh for this.")
        out = self.spawn(FABLE)
        block = out["hookSpecificOutput"]
        self.assertEqual(block["permissionDecision"], "allow")
        self.assertEqual(block["updatedInput"]["subagent_type"], FABLE)
        self.assertIn("<writing-rules>", block["updatedInput"]["prompt"])

    def test_a_fable_spawn_gets_the_long_output_note_after_the_rules(self):
        self.submit("Please use @agent-fable-xhigh for this.")
        prompt = self.spawn(FABLE)["hookSpecificOutput"]["updatedInput"]["prompt"]
        self.assertIn(LONG_OUTPUT, prompt)
        self.assertLess(prompt.index("</writing-rules>"), prompt.index(LONG_OUTPUT))

    def test_quoted_mention_form_also_unlocks_fable(self):
        self.submit('Hand it to @"fable-xhigh (agent)" now.')
        out = self.spawn(FABLE)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_full_name_mention_form_also_unlocks_fable(self):
        self.submit("Route this to @gborges-standard:fable-xhigh.")
        out = self.spawn(FABLE)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_a_mention_in_one_session_does_not_unlock_another(self):
        self.submit("Use @agent-fable-xhigh.", session_id="s1")
        out = self.spawn(FABLE, session_id="s2")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_a_later_message_without_the_mention_locks_fable_again(self):
        self.submit("Use @agent-fable-xhigh.")
        self.submit("Now carry on with the next file.")
        out = self.spawn(FABLE)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")


class FableTurnedOff(HookCase):
    def test_a_mentioned_fable_spawn_becomes_opus_when_fable_is_off(self):
        self.write_config('{"fable": false, "codex": false}')
        self.submit("Use @agent-fable-xhigh.")
        out = self.spawn(FABLE)
        block = out["hookSpecificOutput"]
        self.assertEqual(block["permissionDecision"], "allow")
        self.assertEqual(block["updatedInput"]["subagent_type"], OPUS)
        self.assertIn("<writing-rules>", block["updatedInput"]["prompt"])
        self.assertNotIn(LONG_OUTPUT, block["updatedInput"]["prompt"])
        self.assertIn(OPUS, block["permissionDecisionReason"])

    def test_an_unmentioned_fable_spawn_is_still_denied_when_fable_is_off(self):
        self.write_config('{"fable": false, "codex": false}')
        out = self.spawn(FABLE)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")


class OtherSpawns(HookCase):
    def test_an_opus_medium_spawn_keeps_its_type_and_gets_the_rules(self):
        out = self.spawn("gborges-standard:opus-medium")
        block = out["hookSpecificOutput"]
        self.assertEqual(block["permissionDecision"], "allow")
        self.assertEqual(block["updatedInput"]["subagent_type"], "gborges-standard:opus-medium")
        self.assertIn("<writing-rules>", block["updatedInput"]["prompt"])
        self.assertNotIn(LONG_OUTPUT, block["updatedInput"]["prompt"])

    def test_every_spawn_gets_the_file_edits_rule(self):
        prompt = self.spawn("gborges-standard:opus-medium")["hookSpecificOutput"]["updatedInput"]["prompt"]
        self.assertIn("## File edits", prompt)
        self.assertIn("Change only the lines that change.", prompt)

    def test_an_explore_spawn_produces_no_output(self):
        self.assertIsNone(self.spawn("Explore"))

    def test_a_named_specialist_keeps_its_type(self):
        block = self.spawn("claude-code-guide")["hookSpecificOutput"]
        self.assertEqual(block["updatedInput"]["subagent_type"], "claude-code-guide")


class UnpinnedSpawns(HookCase):
    def test_general_purpose_is_rewritten_to_opus_medium(self):
        block = self.spawn("general-purpose")["hookSpecificOutput"]
        self.assertEqual(block["permissionDecision"], "allow")
        self.assertEqual(block["updatedInput"]["subagent_type"], OPUS_MEDIUM)
        self.assertIn("<writing-rules>", block["updatedInput"]["prompt"])
        self.assertIn(OPUS_MEDIUM, block["permissionDecisionReason"])

    def test_every_unpinned_name_is_rewritten(self):
        for name in ("claude", "default-agent", "gborges-standard:default-agent", ""):
            with self.subTest(name=name):
                block = self.spawn(name)["hookSpecificOutput"]
                self.assertEqual(block["updatedInput"]["subagent_type"], OPUS_MEDIUM)

    def test_a_missing_type_is_rewritten(self):
        out = run_hook(
            ROUTE,
            {"session_id": "s1", "tool_name": "Agent", "tool_input": {"prompt": "Do the work."}},
            self.home,
        )
        self.assertEqual(out["hookSpecificOutput"]["updatedInput"]["subagent_type"], OPUS_MEDIUM)

    def test_an_unpinned_spawn_with_an_empty_prompt_is_still_rewritten(self):
        block = self.spawn("general-purpose", prompt="")["hookSpecificOutput"]
        self.assertEqual(block["updatedInput"]["subagent_type"], OPUS_MEDIUM)
        self.assertEqual(block["updatedInput"]["prompt"], "")


class ForkSpawns(HookCase):
    def test_a_fork_on_a_fable_session_is_denied_and_pointed_at_opus_medium(self):
        transcript = self.write_transcript("claude-fable-5-1")
        block = self.spawn("fork", transcript=transcript)["hookSpecificOutput"]
        self.assertEqual(block["permissionDecision"], "deny")
        self.assertIn(OPUS_MEDIUM, block["permissionDecisionReason"])
        self.assertNotIn("updatedInput", block)

    def test_a_fork_on_an_opus_session_passes_untouched(self):
        transcript = self.write_transcript("claude-opus-5")
        self.assertIsNone(self.spawn("fork", transcript=transcript))

    def test_the_newest_reply_decides_the_model(self):
        # The transcript's earlier reply is Sonnet; only the newest one counts.
        transcript = self.write_transcript("claude-fable-5-1")
        self.assertEqual(
            self.spawn("fork", transcript=transcript)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_a_fork_on_fable_passes_when_the_message_asked_for_one(self):
        transcript = self.write_transcript("claude-fable-5-1")
        self.submit("Fork this and try the other approach.")
        self.assertIsNone(self.spawn("fork", transcript=transcript))

    def test_a_later_message_without_the_word_locks_forks_again(self):
        transcript = self.write_transcript("claude-fable-5-1")
        self.submit("Fork this.")
        self.submit("Now review it.")
        self.assertEqual(
            self.spawn("fork", transcript=transcript)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_a_fork_request_does_not_unlock_fable(self):
        self.submit("Fork this.")
        self.assertEqual(self.spawn(FABLE)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_a_fork_passes_when_the_session_model_is_unknown(self):
        self.assertIsNone(self.spawn("fork"))
        self.assertIsNone(self.spawn("fork", transcript=self.home / "missing.jsonl"))
        empty = self.home / "empty.jsonl"
        empty.write_text("", encoding="utf-8")
        self.assertIsNone(self.spawn("fork", transcript=empty))

    def test_a_long_transcript_is_read_from_the_tail(self):
        transcript = self.home / "long.jsonl"
        filler = json.dumps({"type": "user", "message": {"content": "x" * 300_000}})
        newest = json.dumps({"type": "assistant", "message": {"model": "claude-fable-5-1", "content": []}})
        transcript.write_text(filler + "\n" + newest + "\n" + filler + "\n", encoding="utf-8")
        self.assertEqual(
            self.spawn("fork", transcript=transcript)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_a_malformed_config_leaves_a_mentioned_fable_spawn_on_fable(self):
        self.write_config("{not json")
        self.submit("Use @agent-fable-xhigh.")
        out = self.spawn("gborges-standard:fable-xhigh")
        block = out["hookSpecificOutput"]
        self.assertEqual(block["permissionDecision"], "allow")
        self.assertEqual(block["updatedInput"]["subagent_type"], "gborges-standard:fable-xhigh")
        self.assertIn("<writing-rules>", block["updatedInput"]["prompt"])


class NoCodexLine(HookCase):
    def test_codex_on_prints_no_codex_line(self):
        self.write_config('{"fable": true, "codex": true}')
        out = self.submit("Hello.")
        self.assertNotIn("Codex delegation", out["hookSpecificOutput"]["additionalContext"])

    def test_the_switch_off_prints_nothing_but_records_the_mention(self):
        done = subprocess.run(
            [sys.executable, str(REMIND)],
            input=json.dumps({"session_id": "s3", "prompt": "Use @agent-fable-xhigh."}),
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": str(self.home), "WRITING_VOICE_REMIND": "0"},
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout, "")
        out = self.spawn(FABLE, session_id="s3")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_a_non_json_event_still_prints_the_reminder(self):
        done = subprocess.run(
            [sys.executable, str(REMIND)],
            input="not json at all",
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": str(self.home)},
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("Plain English reminder: ", done.stdout)
        self.assertNotIn("Codex delegation", done.stdout)


if __name__ == "__main__":
    unittest.main()
