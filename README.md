# claude-plugins

Gabe Borges' personal Claude Code marketplace. One bundle plugin, `gborges-standard`, carrying the working conventions, skills, and third-party plugins used across every repo.

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
# rev: 13
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
| `plain-english.md` | Output style | Forced on whenever the plugin is enabled (`force-for-plugin`). Register, git, and plan rules in the system prompt of every session |
| `strip-attribution.py` | `PreToolUse` hook | Removes AI-attribution footers from GitHub writes. Enforces the style's ban mechanically |
| `flag-server-attribution.py` | `PostToolUse` hook | Tells the session to delete the footer the GitHub server adds to a new PR body, which the `PreToolUse` hook cannot reach |
| `inject-writing-rules.py` | `PreToolUse` hook | Appends the style's rules to every subagent prompt, since the output style never reaches a subagent |
| `remind-writing-rules.py` | `UserPromptSubmit` hook | Returns the style's Reminder paragraph as context with every user message, so the rules sit next to the reply being written |
| `writing-voice` | Skill | Two-pass ritual for any prose past 200 characters, replies included |
| `read-aloud-prep` | Skill | Rewriting documents so a TTS voice reads them cleanly |
| `bear-notes` | Skill | Writing into Bear without minting junk tags and wikilinks |
| `add-to-git` | Command | Explicit invocation only, never model-triggered |
| `frontend-design` | Dependency | From `claude-plugins-official` |
| `mattpocock-skills` | Dependency | From `claude-plugins-official` |
| `context7` | Dependency | From `claude-plugins-official` |

Dependencies resolve to the same identifiers a user-scope install uses, so a machine that already has them does not get a second copy.

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

## Subagent rules injection

The output style never reaches a spawned subagent, which runs its own system prompt. A CLAUDE.md pointer does not help, because a pointer names a style the subagent cannot load. So a subagent writing a PR body or a commit message ships unstyled prose.

A second `PreToolUse` hook closes the gap. It matches the Agent tool (Task in older versions) and rewrites the spawn call, appending the style's Sentences, Punctuation, and Git sections plus the writing-voice ritual to the subagent's prompt. The block is read from the installed plain-english.md at run time, so the rules keep one source and the hook needs no edit when they change. Explore and Plan spawns are skipped, since only the styled main conversation reads their reports. A prompt already carrying the block is left alone, and on any read failure the hook stays silent rather than breaking the spawn.

## Reminding the rules each turn

The output style sits at the top of the system prompt, and its pull on a
reply weakens as the conversation grows over it. The writing-voice ritual
covers any prose past 200 characters, but the decision to run it gets made
while the reply is being written, which is where that pull is weakest.

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
