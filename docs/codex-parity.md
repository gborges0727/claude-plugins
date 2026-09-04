# Running Codex in parity with Claude Code

How to set up the Codex CLI on a machine so it carries the same rules,
skills, MCP servers, and model routing as Claude Code, and what stays
different. Written against Codex 0.153.0 on 2026-09-03. Every command
below ran on the home desktop that day.

## What lives in one place

| Piece | The one copy | How Codex reads it |
|---|---|---|
| Writing rules, hooks, five skills | this repo's `plugins/gborges-standard` | the `gborges` marketplace, installed with `codex plugin add` |
| Machine notes (SSH, colima, GitHub, Taildrop, 1Password) | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` is a symlink to it |
| Model routing and status line | `scripts/setup.sh --codex-config on` | it writes `~/.codex/config.toml` and `~/.codex/agents` |
| Per-machine switches (Fable, Codex delegation) | `~/.claude/gborges-standard.json` | the Codex hooks read the same file |

Skills from other marketplaces, MCP servers, and the Cloudflare plugin
each have a second registration on the Codex side. The sections below
cover every one.

## Install the plugin

```sh
codex plugin marketplace add gborges0727/claude-plugins
codex plugin add gborges-standard@gborges
```

Then open a Codex session and run `/hooks` to trust the five hooks. Codex
hashes each hook file and refuses to run one nobody approved, so the
skills work from install and the hooks stay off until this step. Editing a
hook changes its hash and asks again.

The GitHub install pulls whatever main holds. After a merge, refresh the
snapshot by hand, because Codex has no auto-update:

```sh
codex plugin marketplace upgrade
codex plugin add gborges-standard@gborges
```

Codex keys the snapshot on the `version` in `.codex-plugin/plugin.json`,
so every change to the plugin bumps it. Keep it equal to the version in
`.claude-plugin/plugin.json`.

## Point Codex at the global instructions

```sh
ln -s ~/.claude/CLAUDE.md ~/.codex/AGENTS.md
```

Codex reads through the link. `codex debug prompt-input` dumps the prompt
Codex builds, and every section of `CLAUDE.md` appears in it. Codex caps
combined instructions at 32 KiB (`project_doc_max_bytes`), and the file
is under 4 KB.

A tool that writes a fresh `~/.codex/AGENTS.md` turns the link into a
plain file and the two copies drift. `ls -la ~/.codex/AGENTS.md` showing
the arrow is the check.

## Register the MCP servers

Claude Code keeps its servers in `~/.claude.json`. Codex keeps them in
`~/.codex/config.toml`, written by `codex mcp add` with the same command
each server uses on the Claude side:

```sh
codex mcp add bear -- /Applications/Bear.app/Contents/MacOS/bearcli mcp-server
codex mcp add railway -- railway mcp proxy
codex mcp add schwab -- ~/git/schwab-trading/.venv/bin/schwab-mcp serve
```

`codex mcp list` shows all three enabled. Bear is optional on Codex. The
`bear-notes` skill writes through the `bearcli` binary and only reads
through the MCP tools, so the skill works without the server. The server
adds the typed search and outline tools.

## Install the other plugins

Three of the Claude marketplaces carry a Codex manifest
(`.agents/plugins/marketplace.json`) and install the same way:

```sh
codex plugin marketplace add cloudflare/skills
codex plugin marketplace add android/skills
codex plugin marketplace add chrisbanes/skills
codex plugin add cloudflare@cloudflare
codex plugin add android-skills@android-skills
codex plugin add chrisbanes-skills@chrisbanes-skills
```

Context7 is already in Codex's curated marketplace, installed under the
name `app-69ef18c674308191a2f952431f91ea61@openai-curated-remote`.

The Cloudflare plugin also registers a remote MCP server at
`mcp.cloudflare.com`. Its OAuth flow ends at a `127.0.0.1` redirect that
only a browser on this box can reach, and `codex mcp login` has no
device-code mode, so the server stays off. `codex mcp remove` cannot
delete a plugin-supplied server. The override is a table in
`~/.codex/config.toml` that names the URL and disables it, and Codex
rejects the entry without the URL:

```toml
[mcp_servers.cloudflare]
url = "https://mcp.cloudflare.com/mcp"
enabled = false
```

The 13 Cloudflare skills load either way. The Claude Code side of the
same plugin is also unauthenticated, so this is an accepted gap on both
hosts.

## Link the skills that have no Codex marketplace

Codex loads any folder holding a `SKILL.md` from `~/.agents/skills`.
Symlinks into the Claude Code checkouts keep one copy:

```sh
cd ~/.agents/skills
ln -s ~/.claude/skills/bear-todos bear-todos
ln -s ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design frontend-design
ln -s ~/.claude/plugins/marketplaces/swiftui-agent-skill/swiftui-pro swiftui-pro
```

Those three point at git checkouts that Claude Code updates in place, so
the links never break.

The mattpocock plugin is different. Claude Code fetches it into a
versioned cache folder, and its manifest loads 25 of the 35 skill folders
it ships. This loop links the same 25:

```sh
m=~/.claude/plugins/cache/claude-plugins-official/mattpocock-skills/1.2.3
cd ~/.agents/skills
for s in $(python3 -c "import json;print(' '.join(json.load(open('$m/.claude-plugin/plugin.json'))['skills']))"); do
  ln -s "$m/$s" "$(basename $s)"
done
```

Those 25 links break when Claude Code moves the plugin past 1.2.3, because
the cache path carries the version. Re-run the loop with the new version
when `ls -la ~/.agents/skills | grep mattpocock` shows dangling links.

`use-railway` was already in `~/.agents/skills`, so the folder ends at 29
skills.

## Write the model setup and status line

```sh
bash plugins/gborges-standard/scripts/setup.sh --fable on --codex off --codex-config on
```

The third flag defaults to on when `codex` is on PATH. It writes four
agent files in `~/.codex/agents`, one for each of the plugin's Claude
agents:

| Codex agent | Model and effort | Mirrors |
|---|---|---|
| `luna-xhigh` | `gpt-5.6-luna`, xhigh | `sonnet-medium`, fully specified edits and runs |
| `terra-xhigh` | `gpt-5.6-terra`, xhigh | `opus-medium`, the default worker |
| `sol-xhigh` | `gpt-5.6-sol`, xhigh | `opus-xhigh`, the one escalation step |
| `astra-xhigh` | `gpt-6-astra`, xhigh | `fable-xhigh`, only when the user names it |

In `~/.codex/config.toml` it sets the orchestrator to `gpt-5.6-sol` at
medium effort, and sets `agents.default_subagent_model` to `gpt-5.6-terra`
at xhigh so an unnamed spawn lands there. Codex resolves a spawn's model
as the explicit spawn value, then this default, then the parent's model.

It also sets `tui.status_line` to the seven fields `statusline.sh` shows
in Claude Code, in the same order:

| Claude line | Codex field |
|---|---|
| directory name | `current-dir` |
| git branch | `git-branch` |
| dirty marker | `branch-changes` |
| model and effort | `model-with-reasoning` |
| context used | `context-used` |
| 5-hour limit | `five-hour-limit` |
| 7-day limit | `weekly-limit` |

Codex takes a fixed list of field names for its footer and cannot run a
script (openai/codex issue 20244 asks for that), so the per-model colors
in `statusline.sh` do not carry over. `status_line_use_colors = true`
applies the active `/theme` colors instead.

The script replaces only the `model`, `model_reasoning_effort`,
`[agents]`, and `[tui]` entries and keeps every other line. It parses the
result before writing it, and a second run produces the same file.
`tests/test_setup.py` covers all of that.

## What stays different

Codex tells its model not to spawn subagents unless the user, `AGENTS.md`,
or a skill asks, and not to set a model on a spawn unless instructed. So
the `[agents]` default is right, but Codex does not delegate on its own
the way the Plain English style tells Claude Code to. The session-style
hook drops the style's Subagents section for Codex. A Codex-specific
Subagents section naming the four agents, in that hook or in `AGENTS.md`,
is the missing piece.

Codex assigns a spawn's model before its `SubagentStart` hook runs, so no
hook can rewrite a spawn the way `route-spawns.py` does in Claude Code.
Codex's `PreToolUse` hook does accept `updatedInput`, so a hook matching
the `spawn_agent` tool could rewrite the model argument. Nobody has
written that yet.

The `add-to-git` and `setup` commands, the four Claude agents, and the
`swift-lsp` and `kotlin-lsp` plugins have no Codex equivalent. Claude
Code's permission allowlist, model setting, output style, theme, and auto
mode block are Claude Code settings with no counterpart to copy.

Codex carries five plugins Claude Code does not: `github`, `superpowers`,
`openai-templates`, `deep-research-work`, and `plugin-management`. The
`github` one matters, because the attribution hooks match on
`mcp__github__*` tools.

## Check the result

| Check | Command | Expect |
|---|---|---|
| plugins installed | `codex plugin list` | `gborges-standard`, `cloudflare`, `android-skills`, `chrisbanes-skills` all `installed, enabled` |
| MCP servers | `codex mcp list` | `bear`, `railway`, `schwab` enabled, `cloudflare` disabled |
| instructions | `codex debug prompt-input \| grep -c colima` | 1 or more |
| skills | `ls ~/.agents/skills \| wc -l` | 29 |
| model slugs | `codex debug models` | `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-6-astra` present |
| config parses | `codex doctor` | every row a check mark |
| agents and footer | a Codex session, `/agents` and the footer | four agents listed, seven fields shown |

The last row needs an interactive session. Everything above it runs
without one and without spending quota.
