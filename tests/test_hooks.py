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
INJECT = HOOKS / "inject-writing-rules.py"
REMIND = HOOKS / "remind-writing-rules.py"

FABLE = "gborges-standard:fable-xhigh"
OPUS = "gborges-standard:opus-xhigh"

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

    def spawn(self, subagent_type, session_id="s1", prompt="Do the work."):
        return run_hook(
            INJECT,
            {
                "session_id": session_id,
                "tool_name": "Agent",
                "tool_input": {"subagent_type": subagent_type, "prompt": prompt},
            },
            self.home,
        )


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

    def test_a_malformed_config_leaves_a_mentioned_fable_spawn_on_fable(self):
        self.write_config("{not json")
        self.submit("Use @agent-fable-xhigh.")
        out = self.spawn("gborges-standard:fable-xhigh")
        block = out["hookSpecificOutput"]
        self.assertEqual(block["permissionDecision"], "allow")
        self.assertEqual(block["updatedInput"]["subagent_type"], "gborges-standard:fable-xhigh")
        self.assertIn("<writing-rules>", block["updatedInput"]["prompt"])


class CodexLine(HookCase):
    def test_no_config_file_reports_codex_off(self):
        out = self.submit("Hello.")
        self.assertIn("Codex delegation is off for this machine.", out["hookSpecificOutput"]["additionalContext"])

    def test_codex_true_reports_codex_on(self):
        self.write_config('{"fable": true, "codex": true}')
        out = self.submit("Hello.")
        self.assertIn("Codex delegation is on for this machine.", out["hookSpecificOutput"]["additionalContext"])

    def test_a_malformed_config_reports_codex_off(self):
        self.write_config("{not json")
        out = self.submit("Hello.")
        self.assertIn("Codex delegation is off for this machine.", out["hookSpecificOutput"]["additionalContext"])

    def test_the_reminder_line_comes_before_the_codex_line(self):
        out = self.submit("Hello.")
        context = out["hookSpecificOutput"]["additionalContext"]
        lines = [line for line in context.splitlines() if line.strip()]
        self.assertIn("Plain English reminder: ", lines[0])
        self.assertEqual(lines[-1], "Codex delegation is off for this machine.")

    def test_the_codex_host_flag_leaves_the_codex_line_out(self):
        self.write_config('{"fable": true, "codex": true}')
        done = subprocess.run(
            [sys.executable, str(REMIND), "--codex-host"],
            input=json.dumps({"session_id": "s9", "prompt": "Hello."}),
            capture_output=True, text=True, env={**os.environ, "HOME": str(self.home)},
        )
        context = json.loads(done.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertNotIn("Codex delegation", context)
        self.assertIn("Plain English reminder: ", context)

    def test_the_switch_off_still_records_the_mention_and_prints_codex(self):
        env_home = self.home
        done = subprocess.run(
            [sys.executable, str(REMIND)],
            input=json.dumps({"session_id": "s3", "prompt": "Use @agent-fable-xhigh."}),
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": str(env_home), "WRITING_VOICE_REMIND": "0"},
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        context = json.loads(done.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(context.strip(), "Codex delegation is off for this machine.")
        out = self.spawn(FABLE, session_id="s3")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_a_non_json_event_still_prints_the_codex_line(self):
        done = subprocess.run(
            [sys.executable, str(REMIND)],
            input="not json at all",
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": str(self.home)},
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("Codex delegation is off for this machine.", done.stdout)


if __name__ == "__main__":
    unittest.main()
