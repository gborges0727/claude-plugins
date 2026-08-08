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
# rev: 2
curl -fsSL https://raw.githubusercontent.com/gborges0727/claude-plugins/main/scripts/cloud-bootstrap.sh | bash || true
exit 0
```

`raw.githubusercontent.com` is on the default Trusted allowlist, so this needs no network configuration. A failed fetch leaves the session without the bundle and still starts it, which is the right failure, since a non-zero exit from a setup script kills the session outright.

The script installs at user scope inside the VM, which is a real user scope that Claude Code reads, unlike the one on a local machine that never travels. A repo needs no `.claude/settings.json` at all to pick the bundle up, in any repo the environment opens.

Anthropic snapshots the VM filesystem after the setup script completes and reuses the snapshot for later sessions, which skip the script entirely. The install is idempotent and takes under ten seconds from cold, so either path is fine.

What the cache does cost is freshness. A snapshot can serve a plugin version up to roughly a week old, and nothing inside the session can patch that, because plugins load while Claude Code launches. The cache rebuilds when the setup script text changes, when the allowed hosts change, or when it expires. So the loader's `rev` comment is the lever for a change that cannot wait out the expiry. Bumping it is the only reason to open the environment dialog again.

## What the bundle contains

| Component | Kind | Notes |
|---|---|---|
| `plain-english.md` | Output style | Forced on whenever the plugin is enabled (`force-for-plugin`). Register, git, and plan rules in the system prompt of every session |
| `strip-attribution.py` | `PreToolUse` hook | Removes AI-attribution footers from GitHub writes. Enforces the style's ban mechanically |
| `writing-voice` | Skill | Two-pass ritual for file deliverables longer than a few paragraphs |
| `read-aloud-prep` | Skill | Rewriting documents so a TTS voice reads them cleanly |
| `bear-notes` | Skill | Writing into Bear without minting junk tags and wikilinks |
| `add-to-git` | Command | Explicit invocation only, never model-triggered |
| `frontend-design` | Dependency | From `claude-plugins-official` |
| `mattpocock-skills` | Dependency | From `claude-plugins-official` |
| `context7` | Dependency | From `claude-plugins-official` |

Dependencies resolve to the same identifiers a user-scope install uses, so a machine that already has them does not get a second copy.

## Attribution stripping

The Plain English style bans AI-attribution trailers on commit messages and PR bodies, and says the ban holds even when a tool guide asks for one. Several harnesses ask for one anyway. Claude Code on the web instructs the model to append a `Generated by [Claude Code]` footer to every GitHub comment and PR body it writes.

That conflict is instructions against instructions, both sitting in the system prompt, and the model can resolve it either way on any given call. The `PreToolUse` hook removes the question from the model's hands by editing the call itself.

It matches `mcp__github__.*` and inspects the `body`, `message`, and `commit_message` arguments. When it finds a footer it returns the call with the footer gone. When it finds nothing it prints nothing and exits, which matters more than it looks: rewriting a call requires approving it, so staying silent on clean bodies keeps the normal permission prompt on every GitHub write the hook did not touch. The implicit approval only ever covers a call it just corrected.

Local sessions with no GitHub MCP server never fire it, since nothing matches the pattern.

## Adding a plugin to the set

Add it to the `dependencies` array in `plugins/gborges-standard/.claude-plugin/plugin.json`. If it comes from `claude-plugins-official`, that is the only edit anywhere, and every consuming repo picks it up. Installing the bundle pulls its dependencies in as long as their marketplace is registered, so `scripts/cloud-bootstrap.sh` does not name them and needs no edit either.

If it comes from any other marketplace, a dependency on it resolves only in sessions that already registered that marketplace, and it fails silently otherwise. Rather than adding the marketplace to every repo, add the plugin as a second entry in `.claude-plugin/marketplace.json` using a `git-subdir` source pointing at its upstream repo. The dependency then resolves inside `gborges` and consuming repos stay at one marketplace.

Bump `version` in `plugin.json` when the set changes. Local sessions pick up changes on `claude plugin update gborges-standard` or when auto-update is enabled for the marketplace, which is off by default for non-Anthropic marketplaces. Cloud sessions running off a cached environment snapshot keep whatever the setup script installed when the snapshot was built, so bump the `rev` comment in `scripts/cloud-bootstrap.sh` too when a change needs to land immediately.

## Verifying the style

A plugin that fails to load applies no style and prints no error. To check it:

```bash
claude -p "Does your system prompt contain a section titled Plain English? If yes, quote its first bullet under the Sentences heading. If not, reply exactly NONE."
```

Confirm it fails as well as passes. Run `claude plugin disable gborges-standard@gborges`, repeat, and expect `NONE`.

`claude plugin list` is the cheaper first check, since an unresolved dependency reports as `failed to load` there and produces `NONE` above for a reason that has nothing to do with the style. `claude plugin details gborges-standard` prints the component inventory that actually loaded.

## User scope

`~/.claude/CLAUDE.md` holds only the commit signing keys, which cannot travel to a cloud sandbox and are deliberately absent from this repo. Every other rule lives here.
