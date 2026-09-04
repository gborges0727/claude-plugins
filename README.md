# claude-plugins

Gabe Borges' personal plugin marketplace. One bundle plugin, `gborges-standard`, carrying the working conventions, skills, and third-party plugins used across every repo. Claude Code installs it from `.claude-plugin/marketplace.json` and the Codex CLI installs the same folder from `.agents/plugins/marketplace.json`. See [Codex](#codex).

It exists because a cloud session never sees the `~/.claude/` on a local machine. That config does not travel, so anything living only there is missing the moment work happens outside a local terminal. This marketplace is the copy that does travel, and edits here propagate to every repo without touching any of them.

There are two ways to pull it into a cloud session, a repo's `.claude/settings.json` and a [cloud environment setup script](#cloud-sessions). The setup script is the better one.

## Use it in a repo

Add to the repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "gborges": {
      "source": { "source": "github", "repo": "gborges0727/claude-plugins" }
    },
    "claude-plugins-official": {
      "source": { "source": "github", "repo": "anthropics/claude-plugins-official" }
    }
  },
  "enabledPlugins": {
    "gborges-standard@gborges": true
  }
}
```

Both marketplaces have to be declared. A local machine usually has `claude-plugins-official` registered already, from having browsed plugins at some point, so declaring `gborges` alone appears to be enough. A fresh session VM has no marketplaces registered at all and never adds that one on its own, so the bundle's three dependencies fail to resolve and the whole plugin is marked `failed to load`. That failure takes the style, the skills, and the hook down with it, and it prints nothing into the session.

For cloud sessions, prefer the [setup script](#cloud-sessions) over this file.

## Cloud sessions

Declaring the marketplace in a repo's `.claude/settings.json` is the portable option, and it is the wrong one for cloud sessions. Install from that file happens as the session starts, and it lags a boot. The first launch in a fresh VM registers the marketplace and installs nothing. The second launch installs the plugin. A cloud session only ever gets one launch, so the first turn has no plugin components loaded, and opening with a slash command does not resolve it. Sending a throwaway message to wait the install out is the workaround that costs tokens.

A setup script avoids the whole problem. Setup scripts run as root before Claude Code launches, so everything is registered by the time the first turn is read, and they run outside the model loop, so they cost nothing. The field is at [claude.ai/code](https://claude.ai/code) under the cloud icon above the message box, **Setup script** in the environment dialog.

Paste this loader rather than the body of `scripts/cloud-bootstrap.sh`, so the logic stays in git and the environment field never has to be edited again:

```bash
#!/bin/bash
# rev: 29
curl -fsSL https://raw.githubusercontent.com/gborges0727/claude-plugins/main/scripts/cloud-bootstrap.sh | bash || true
exit 0
```

`raw.githubusercontent.com` is on the default Trusted allowlist, so this needs no network configuration. A failed fetch leaves the session without the bundle and still starts it, which is the right failure, since a non-zero exit from a setup script kills the session outright.

The script installs at user scope inside the VM, which is a real user scope that Claude Code reads, unlike the one on a local machine that never travels. A repo needs no `.claude/settings.json` at all to pick the bundle up, in any repo the environment opens.

Anthropic snapshots the VM filesystem after the setup script completes and reuses the snapshot for later sessions, which skip the script entirely. The install is idempotent and takes under ten seconds from cold, so either path is fine.

What the cache does cost is freshness. A snapshot can serve a plugin version up to roughly a week old, and nothing inside the session can patch that, because plugins load while Claude Code launches. The cache rebuilds when the setup script text changes, when the allowed hosts change, or when it expires. So the loader's `rev` comment is the lever for a change that cannot wait out the expiry. Bumping it is the only reason to open the environment dialog again.

Every PR bumps the `rev`, in the snippet above and in `scripts/cloud-bootstrap.sh`, keeping the two equal. CI (`.github/workflows/rev-bump.yml`) fails the PR otherwise. The bump changes nothing in an environment by itself. It keeps the repo's number the source of truth. After a merge, the number to paste into the environment field is always the one on `main`.

## What the bundle contains

| Component | Kind | Notes |
|---|---|---|
| `plain-english.md` | Output style | Forced on whenever the plugin is enabled (`force-for-plugin`). Register, git, plan, and file-edit rules in the system prompt of every session. The file-edit rule is Anthropic's answer to Fable 5.1 rewriting a whole file for a small change |
| `strip-attribution.py` | `PreToolUse` hook | Removes AI-attribution footers from GitHub writes. Enforces the style's ban mechanically |
| `flag-server-attribution.py` | `PostToolUse` hook | Tells the session to delete the footer the GitHub server adds to a new PR body, which the `PreToolUse` hook cannot reach |
| `route-spawns.py` | `PreToolUse` hook | Decides which agent every spawn runs on, then appends the style's rules to its prompt, since the output style never reaches a subagent. Rewrites an unpinned type (`general-purpose`, `claude`, `default-agent`, or none) to `opus-medium`. Refuses a `fork` on a Fable session, since a fork copies the whole transcript onto the session's model, unless the user's latest message asked for one. Refuses a `fable-xhigh` dispatch the user did not summon, and rewrites it to `opus-xhigh` when `~/.claude/gborges-standard.json` says the account cannot run Fable. Appends Anthropic's long-output note to a `fable-xhigh` prompt, so Fable writes a long deliverable once instead of drafting it in thinking and again as the reply |
| `remind-writing-rules.py` | `UserPromptSubmit` hook | Returns the style's Reminder paragraph as context with every user message, so the rules sit next to the reply being written. Records whether the message named `@agent-fable-xhigh`, used the word fork, or named Astra |
| `writing-voice` | Skill | Two-pass ritual for every artifact (a file, a PR body, a commit message, a comment), whatever its length. The style alone shapes chat replies |
| `read-aloud-prep` | Skill | Rewriting documents so a TTS voice reads them cleanly |
| `bear-notes` | Skill | Writing into Bear without minting junk tags and wikilinks |
| `route-codex.py` | `PreToolUse` hook | Guards the `mcp__codex__codex` call the `codex-delegate` skill makes. Lets GPT-6 Astra run at medium on its own, refuses it above medium unless the user's latest message named Astra, and fills in the effort when the call set none |
| `codex-delegate` | Skill | Handing a subtask to the Codex CLI on one of four rungs (Luna, Sol, Astra at medium, or the user-summoned Astra at xhigh), so ChatGPT-plan quota pays for it instead of Claude tokens. Needs the `codex` MCP server registered |
| `model-routing-review` | Skill | Explicit invocation only. Re-derives the delegation ladder from today's catalog, prices, and scores, rewrites [docs/model-routing.md](docs/model-routing.md), and lists every file the ladder change touches |
| `add-to-git` | Command | Explicit invocation only, never model-triggered |
| `setup` | Command | Writes `~/.claude/gborges-standard.json`, the per-machine switches for Fable access and Codex delegation, and the Codex CLI's own model, subagent, and status line config under `~/.codex`. Wraps `scripts/setup.sh`, which does the same with no model turn |
| `sonnet-medium` | Agent | Sonnet 5 at medium effort. Edits and runs with a command check in the brief, parallel copies of one such task, and fetching a named doc page |
| `opus-medium` | Agent | Opus 5 at medium effort. The default, and the floor for anything that reads code to reach a conclusion |
| `opus-xhigh` | Agent | Opus 5 at xhigh effort. One escalation step for a task that failed below it, and the stand-in for Fable on an account without it |
| `fable-xhigh` | Agent | Fable 5.1 at xhigh effort. Runs only when the user's message names `@agent-fable-xhigh`. See [docs/subagent-routing.md](docs/subagent-routing.md) for the routing rule and the cost reasoning |
| `frontend-design` | Dependency | From `claude-plugins-official` |
| `mattpocock-skills` | Dependency | From `claude-plugins-official` |
| `context7` | Dependency | From `claude-plugins-official` |

Dependencies resolve to the same identifiers a user-scope install uses, so a machine that already has them does not get a second copy.

## Codex

The same plugin folder installs into the Codex CLI. Codex reads its own
marketplace file at `.agents/plugins/marketplace.json`, next to the Claude
one at `.claude-plugin/marketplace.json`, and both point at
`plugins/gborges-standard`. Every skill has one copy and both hosts read it.

```bash
codex plugin marketplace add gborges0727/claude-plugins
codex plugin add gborges-standard@gborges
```

Then open a Codex session, run `/hooks`, and trust the five hooks the plugin
ships. Codex hashes each hook and refuses to run one nobody approved, so the
skills work on install and the hooks stay dead until that step. Editing a
hook changes its hash and asks again. Codex installs a snapshot of the
plugin, so a local edit also needs the `version` in
`.codex-plugin/plugin.json` raised and `codex plugin add` run again.

[docs/codex-parity.md](docs/codex-parity.md) walks through the whole
Codex install on a machine, from this plugin to the MCP servers, the linked
skills, and the model setup, and lists what stays different.

Point the marketplace at a local checkout instead of GitHub to test a change
before it merges:

```bash
codex plugin marketplace add ~/git/claude-plugins
```

### The Codex side of the model setup

Codex has no plugin field for agents and does not ship `config.toml`, so
`scripts/setup.sh --codex-config on` writes that half by hand. It puts four
agent files in `~/.codex/agents`. Each pairs with one of the plugin's Claude
agents:

| Codex agent | Model and effort | Mirrors |
|---|---|---|
| `luna-xhigh` | `gpt-5.6-luna`, xhigh | `sonnet-medium`, fully specified edits and runs |
| `sol-xhigh` | `gpt-5.6-sol`, xhigh | `opus-medium`, the default worker |
| `astra-medium` | `gpt-6-astra`, medium | `opus-xhigh`, the one escalation step |
| `astra-xhigh` | `gpt-6-astra`, xhigh | `fable-xhigh`, only when the user names it |

In `~/.codex/config.toml` it sets the orchestrator to `gpt-5.6-sol` at
medium effort, sets `agents.default_subagent_model` to `gpt-5.6-sol` at
xhigh so an unnamed spawn lands there, and sets `tui.status_line` to the
same seven fields the Claude Code status line shows (directory, branch,
dirty marker, model with effort, context used, 5-hour limit, weekly limit).
Codex takes a fixed list of field names for its footer and cannot run a
script, so the per-model colors of `statusline.sh` do not carry over. The
script replaces only those entries and keeps every other line in the file.

Codex assigns a spawn's model before its `SubagentStart` hook runs, so the
routing hook cannot rewrite a spawn the way `route-spawns.py` does in Claude
Code. The `[agents]` default covers the unnamed case, and the agent
descriptions carry the routing rule for the rest.

### What Codex loads

Codex accepts `.claude-plugin/plugin.json` as a manifest and prefers
`.codex-plugin/plugin.json` when both exist. The Codex manifest names
`hooks/codex-hooks.json` and the Claude manifest names
`hooks/claude-hooks.json`, so neither host reads the other's hook set. That
is why no `hooks/hooks.json` exists: both hosts discover that name on their
own, and a file at it would fire twice.

| Component | Codex | Notes |
|---|---|---|
| The five skills | Yes | `SKILL.md` loads unchanged on both hosts |
| `plain-english.md` | Yes, through a hook | Codex has no output styles. `codex-session-style.py` returns the style body as `SessionStart` context |
| `strip-attribution.py` | Yes | Codex passes the same `tool_name` and `tool_input` fields and accepts the same `updatedInput` reply |
| `flag-server-attribution.py` | Yes | Same `PostToolUse` contract |
| `remind-writing-rules.py` | Yes | Same `UserPromptSubmit` contract |
| `route-codex.py` | No | Guards a Claude Code MCP tool. Codex reaches its own models directly |
| `route-spawns.py` | Yes, on a different event | Codex spawns subagents through a tool no `Agent` matcher catches, and fires `SubagentStart`. `--subagent-start` answers that event with the same rules block as context |
| `add-to-git` | No | A Claude command. Codex loads skills, not commands |
| The four agents | No | Claude Code agents. `codex-session-style.py` drops the style's Subagents section so Codex never gets sent to a name it cannot resolve |
| The three dependencies | No | `frontend-design`, `mattpocock-skills`, and `context7` live in a Claude marketplace that Codex cannot install from |

The style arrives as about 6,300 characters of session context, which is the
one real cost of the Codex path. `WRITING_VOICE_STYLE=0` turns it off, and
`WRITING_VOICE_REMIND=0` turns off the per-turn reminder as it always did.

Installing the bundle into Codex retires the hand-copied writing rules in
`~/.codex/AGENTS.md`. Delete that section once the hooks are trusted, or the
rules arrive twice.

## The Claude apps

The bundle reaches Claude Code only. The Claude apps (web, desktop, iOS)
install nothing from a marketplace, so the style and the skill go in through
Instructions for Claude and an uploaded skill zip instead. `chat/build.py`
generates both from the plugin files, so the rules keep one source. See
[chat/README.md](chat/README.md).

## Attribution stripping

The Plain English style bans AI-attribution trailers on commit messages and PR bodies, and says the ban holds even when a tool guide asks for one. Several harnesses ask for one anyway. Claude Code on the web instructs the model to append a `Generated by [Claude Code]` footer to every GitHub comment and PR body it writes.

That conflict is instructions against instructions, both sitting in the system prompt, and the model can resolve it either way on any given call. The `PreToolUse` hook removes the question from the model's hands by editing the call itself.

It matches `mcp__github__.*` and inspects the `body`, `message`, and `commit_message` arguments. When it finds a footer it returns the call with the footer gone. When it finds nothing it prints nothing and exits, which matters more than it looks: rewriting a call requires approving it, so staying silent on clean bodies keeps the normal permission prompt on every GitHub write the hook did not touch. The implicit approval only ever covers a call it just corrected.

Local sessions with no GitHub MCP server never fire it, since nothing matches the pattern.

One call escapes it. `mcp__github__create_pull_request` appends the footer server-side, after the arguments leave the session, so a `PreToolUse` hook never sees the text that GitHub stores. FairLine PR #427 showed it: the submitted link was `https://claude.ai/code`, and the stored body read `https://claude.ai/code/session_<id>`, a session id the hook could not have written.

`flag-server-attribution.py` covers that call as a `PostToolUse` hook. A hook runs as a local subprocess with no GitHub credentials, so it cannot rewrite the body itself. It returns `additionalContext` instead, telling the session to read the stored body and post a corrected one through `mcp__github__update_pull_request`. That follow-up call passes back through `strip-attribution.py`, and `update_pull_request` adds no footer of its own, so the correction sticks.

It reads the body out of the tool response and stays silent when that body is clean, matching the `PreToolUse` hook's habit of only speaking up when something is wrong. When the response carries no readable body it speaks anyway and says the footer is unconfirmed, since a missed footer costs more than one wasted read.

The comment and review write tools are left out. The GitHub MCP server offers no update tool for a posted comment, so there is no call to send the session to.

## Spawn routing and rules injection

A second `PreToolUse` hook, `route-spawns.py`, runs before every Agent call (Task in older versions), including the calls a skill or a forked agent makes. It decides which agent the spawn runs on, then appends the writing rules to the spawn's prompt.

The routing part exists because a spawn that names `general-purpose`, `claude`, `default-agent`, or no type at all inherits the session's model and effort. The style tells Claude to use the plugin's pinned agents, but a built-in skill's procedure names the built-in types, so its spawns slipped through on the session's model. The hook rewrites those types to `opus-medium` and lets the spawn through. Pinned types, Explore, Plan, and any other named type pass as they are.

A `fork` is handled by the session's model instead. A fork copies the whole transcript into a second agent on the session's model, and a fork with a different type is no longer a fork. On an Opus or Sonnet session the fork passes untouched, since it already runs on a model the style would pick. On a Fable session the hook refuses it, and the refusal's reason tells the session to send the same task to `opus-medium` with a brief. The built-in `code-review` skill forks its reviewer, so this is what moves that reviewer onto Opus while the skill stays usable.

A fork still passes on Fable when the user's latest message used the word fork. It also passes when the hook cannot read the session's model from the transcript file the event names.

The rules part exists because the output style never reaches a spawned subagent, which runs its own system prompt. A CLAUDE.md pointer does not help, because a pointer names a style the subagent cannot load. So a subagent writing a PR body or a commit message would ship unstyled prose.

The hook rewrites the spawn call, appending the style's Sentences, The reader is new to this, Punctuation, Git, and File edits sections plus the writing-voice ritual to the subagent's prompt. The block is read from the installed plain-english.md at run time, so the rules keep one source and the hook needs no edit when they change. Explore and Plan spawns are skipped, since only the styled main conversation reads their reports. A prompt already carrying the block is left alone, and on any read failure the hook stays silent rather than breaking the spawn.

A `fable-xhigh` dispatch gets one more paragraph after the rules. At xhigh effort Fable can draft a long deliverable in its thinking and then write it out again as the reply, which doubles the turn's output. Anthropic's Fable 5.1 prompting guide gives a note that stops that, and the hook appends it to a Fable dispatch's prompt only, since no other agent needs it.

## The routed subagents

A subagent spawned with the built-in `general-purpose` type inherits the
orchestrating session's model and effort, so the same delegated task runs
on Sonnet at low effort in one session and on Opus at max in another. The
four files in `agents/` pin a model and an effort each, and their names say
which: `sonnet-medium`, `opus-medium`, `opus-xhigh`, and `fable-xhigh`.
Claude Code loads them as `gborges-standard:<name>`.

The definitions alone change nothing, because Claude reaches for
`general-purpose` by habit. The style's Subagents section is the routing
rule. `opus-medium` is the default and the floor for any task that reads
code to reach a conclusion. `sonnet-medium` takes work a command can check.
`opus-xhigh` is one escalation step, taken once, after a failed check.
`fable-xhigh` runs only when the user's own message names
`@agent-fable-xhigh`, and `route-spawns.py` refuses every other
dispatch of it. [docs/subagent-routing.md](docs/subagent-routing.md) holds
the cost reasoning.

`/gborges-standard:setup` writes `~/.claude/gborges-standard.json`, two
switches per machine. `fable` false makes the hook rewrite `fable-xhigh` to
`opus-xhigh`. `codex` true tells the session, through one line the
per-message hook adds, to send fully specified mechanical work to the
`codex-delegate` skill first.

Claude Code re-reads the agent list on each Agent call, so a running session
picks the agents up without a restart. The routing rule lives in the output
style, which loads at session start, so a session that was open before the
plugin updated follows the rule only after a restart.

## Reminding the rules each turn

The output style sits at the top of the system prompt, and its pull on a
reply weakens as the conversation grows over it. The writing-voice ritual
covers artifacts only, so a chat reply is shaped while it is being written,
which is where that pull is weakest.

`remind-writing-rules.py` fires on `UserPromptSubmit`, which runs when a
message is sent and before Claude answers it. It reads the `## Reminder`
section out of the installed plain-english.md and returns it as one line of
context, so the style's own distillation sits at the bottom of the
conversation, next to the reply being written, where recency gives it the
most force. The section is read at run time, so the reminder keeps one
source and the hook needs no edit when the style changes.

The line restates the rules and nothing else. A reminder that quotes a
reply's mistakes pastes the banned phrasing back into fresh context and
feeds the habit it polices, so no scan output belongs in it. Nothing scans
chat replies at all: earlier designs that graded the finished reply either
showed the grade to the wrong reader (a display report the model never
sees) or arrived a turn too late to matter.

The cost is the line itself, about fifty tokens with every user message,
and it stays in the transcript. `WRITING_VOICE_REMIND=0` turns it off.

Every exit path fails open. A switch that is off, a missing style file, a
Reminder section that has been renamed: each prints nothing and exits 0,
and the turn proceeds without a reminder.

## Adding a plugin to the set

Add it to the `dependencies` array in `plugins/gborges-standard/.claude-plugin/plugin.json`. If it comes from `claude-plugins-official`, that is the only edit anywhere, and every consuming repo picks it up. Installing the bundle pulls its dependencies in as long as their marketplace is registered, so `scripts/cloud-bootstrap.sh` does not name them and needs no edit either.

If it comes from any other marketplace, a dependency on it resolves only in sessions that already registered that marketplace, and it fails silently otherwise. Rather than adding the marketplace to every repo, add the plugin as a second entry in `.claude-plugin/marketplace.json` using a `git-subdir` source pointing at its upstream repo. The dependency then resolves inside `gborges` and consuming repos stay at one marketplace.

Bump `version` in `plugin.json` when the set changes. Local sessions pick up changes on `claude plugin update gborges-standard` or when auto-update is enabled for the marketplace, which is off by default for non-Anthropic marketplaces. Cloud sessions running off a cached environment snapshot keep whatever the setup script installed when the snapshot was built. The PR carries the `rev` bump already, so when the change needs to land immediately, paste the merged rev into the environment's Setup script field and the snapshot rebuilds.

## Verifying the style

A plugin that fails to load applies no style and prints no error. To check it:

```bash
claude -p "Does your system prompt contain a section titled Plain English? If yes, quote its first bullet under the Sentences heading. If not, reply exactly NONE."
```

Confirm it fails as well as passes. Run `claude plugin disable gborges-standard@gborges`, repeat, and expect `NONE`.

`claude plugin list` is the cheaper first check, since an unresolved dependency reports as `failed to load` there and produces `NONE` above for a reason that has nothing to do with the style. `claude plugin details gborges-standard` prints the component inventory that actually loaded.

## User scope

`~/.claude/CLAUDE.md` holds only the commit signing keys, which cannot travel to a cloud sandbox and are deliberately absent from this repo. Every other rule lives here.
