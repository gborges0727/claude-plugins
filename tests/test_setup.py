"""Runs scripts/setup.sh against a temporary home and checks what it writes.

The script writes ~/.claude/gborges-standard.json for the hooks and, with
--codex-config on, four agent files under ~/.codex/agents plus the managed
entries in ~/.codex/config.toml. These tests cover both writers, the
preservation of entries the script does not own, and a second run landing
on the same result.
"""

import json
import os
import subprocess
import tomllib
import unittest
from pathlib import Path
import tempfile

SCRIPT = Path(__file__).resolve().parent.parent / "plugins" / "gborges-standard" / "scripts" / "setup.sh"

AGENTS = {
    "luna-xhigh": ("gpt-5.6-luna", "xhigh"),
    "luna-medium": ("gpt-5.6-luna", "medium"),
    "terra-xhigh": ("gpt-5.6-terra", "xhigh"),
    "sol-xhigh": ("gpt-5.6-sol", "xhigh"),
}

EXISTING_CONFIG = """model = "gpt-5.5"
model_reasoning_effort = "low"

[projects."/tmp/repo"]
trust_level = "trusted"

[agents]
default_subagent_model = "gpt-5.4"

[agents.old]
description = "an agent table the script must keep"

[mcp_servers.bear]
command = "/Applications/Bear.app/Contents/MacOS/bearcli"
args = ["mcp-server"]

[tui]
status_line = ["model"]
"""


def run_setup(home, *flags):
    env = dict(os.environ, HOME=str(home))
    return subprocess.run(
        ["bash", str(SCRIPT), *flags],
        env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL,
    )


class SetupWrites(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def config(self):
        return tomllib.loads((self.home / ".codex" / "config.toml").read_text())

    def test_writes_hook_config_and_codex_files(self):
        result = run_setup(self.home, "--fable", "off", "--codex", "on", "--codex-config", "on")
        self.assertEqual(result.returncode, 0, result.stderr)
        hook_config = json.loads((self.home / ".claude" / "gborges-standard.json").read_text())
        self.assertEqual(hook_config, {"fable": False, "codex": True})
        for name, (model, effort) in AGENTS.items():
            agent = tomllib.loads((self.home / ".codex" / "agents" / f"{name}.toml").read_text())
            self.assertEqual(agent["name"], name)
            self.assertEqual(agent["model"], model)
            self.assertEqual(agent["model_reasoning_effort"], effort)
            self.assertTrue(agent["description"])
            self.assertTrue(agent["developer_instructions"])
        parsed = self.config()
        self.assertEqual(parsed["model"], "gpt-5.6-sol")
        self.assertEqual(parsed["model_reasoning_effort"], "medium")
        self.assertEqual(parsed["agents"]["default_subagent_model"], "gpt-5.6-luna")
        self.assertEqual(parsed["agents"]["default_subagent_reasoning_effort"], "xhigh")
        self.assertEqual(parsed["tui"]["status_line"][0], "current-dir")
        self.assertEqual(len(parsed["tui"]["status_line"]), 7)
        self.assertTrue(parsed["tui"]["status_line_use_colors"])

    def test_codex_config_off_writes_nothing_under_codex(self):
        result = run_setup(self.home, "--fable", "on", "--codex", "off", "--codex-config", "off")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / ".codex").exists())

    def test_replaces_managed_entries_and_keeps_the_rest(self):
        codex_dir = self.home / ".codex"
        codex_dir.mkdir()
        (codex_dir / "config.toml").write_text(EXISTING_CONFIG)
        result = run_setup(self.home, "--fable", "on", "--codex", "off", "--codex-config", "on")
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = self.config()
        self.assertEqual(parsed["model"], "gpt-5.6-sol")
        self.assertEqual(parsed["agents"]["default_subagent_model"], "gpt-5.6-luna")
        self.assertEqual(parsed["agents"]["old"]["description"], "an agent table the script must keep")
        self.assertEqual(parsed["projects"]["/tmp/repo"]["trust_level"], "trusted")
        self.assertEqual(parsed["mcp_servers"]["bear"]["args"], ["mcp-server"])
        self.assertEqual(len(parsed["tui"]["status_line"]), 7)
        text = (codex_dir / "config.toml").read_text()
        self.assertEqual(text.count("[agents]\n"), 1)
        self.assertEqual(text.count("[tui]\n"), 1)
        self.assertEqual(text.count("\nmodel = "), 1)

    def test_second_run_lands_on_the_same_file(self):
        flags = ("--fable", "on", "--codex", "off", "--codex-config", "on")
        run_setup(self.home, *flags)
        first = (self.home / ".codex" / "config.toml").read_text()
        run_setup(self.home, *flags)
        second = (self.home / ".codex" / "config.toml").read_text()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
