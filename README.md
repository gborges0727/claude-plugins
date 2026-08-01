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

Both marketplaces have to be declared. A local machine usually has `claude-plugins-official` registered already, from having browsed plugins at some point, so declaring `gborges` alone appears to be enough. A fresh session VM has no marketplaces registered at all and never adds that one on its own, so the bundle's three dependencies fail to resolve and the whole plugin is marked `failed to load`. That failure takes the hook, the skills, and the command down with it, and it prints nothing into the session.

For cloud sessions, prefer the [setup script](#cloud-sessions) over this file.

## Cloud sessions

Declaring the marketplace in a repo's `.claude/settings.json` is the portable option, and it is the wrong one for cloud sessions. Install from that file happens as the session starts, and it lags a boot. The first launch in a fresh VM registers the marketplace and installs nothing. The second launch installs the plugin. A cloud session only ever gets one launch, so the first turn has no plugin components loaded, and opening with a slash command does not resolve it. Sending a throwaway message to wait the install out is the workaround that costs tokens.

A setup script avoids the whole problem. Setup scripts run as root before Claude Code launches, so everything is registered by the time the first turn is read, and they run outside the model loop, so they cost nothing. Paste `scripts/cloud-bootstrap.sh` into the **Setup script** field of a cloud environment at [claude.ai/code](https://claude.ai/code), reached through the cloud icon above the message box.

The script installs at user scope inside the VM, which is a real user scope that Claude Code reads, unlike the one on a local machine that never travels. A repo needs no `.claude/settings.json` at all to pick the bundle up, in any repo the environment opens.

Anthropic snapshots the VM filesystem after the setup script completes and reuses the snapshot for later sessions, which skip the script entirely. The install is idempotent and takes about ten seconds from cold, so either path is fine. What the cache does cost is freshness, since a snapshot can serve a plugin version up to roughly a week old. Changing the script text rebuilds the cache, so bump the `rev` comment at the top of `cloud-bootstrap.sh` after publishing a change that sessions need right away.

## What the bundle contains

| Component | Kind | Notes |
|---|---|---|
| `CONVENTIONS.md` | `SessionStart` hook | Injected into context every session. Prose rules, git rules, plan-document rules |
| `writing-voice` | Skill | Drafting anything longer than a paragraph |
| `read-aloud-prep` | Skill | Rewriting documents so a TTS voice reads them cleanly |
| `add-to-git` | Command | Explicit invocation only, never model-triggered |
| `frontend-design` | Dependency | From `claude-plugins-official` |
| `mattpocock-skills` | Dependency | From `claude-plugins-official` |
| `context7` | Dependency | From `claude-plugins-official` |

Dependencies resolve to the same identifiers a user-scope install uses, so a machine that already has them does not get a second copy.

## Adding a plugin to the set

Add it to the `dependencies` array in `plugins/gborges-standard/.claude-plugin/plugin.json`. If it comes from `claude-plugins-official`, that is the only edit anywhere, and every consuming repo picks it up. Installing the bundle pulls its dependencies in as long as their marketplace is registered, so `scripts/cloud-bootstrap.sh` does not name them and needs no edit either.

If it comes from any other marketplace, a dependency on it resolves only in sessions that already registered that marketplace, and it fails silently otherwise. Rather than adding the marketplace to every repo, add the plugin as a second entry in `.claude-plugin/marketplace.json` using a `git-subdir` source pointing at its upstream repo. The dependency then resolves inside `gborges` and consuming repos stay at one marketplace.

Bump `version` in `plugin.json` when the set changes. Local sessions pick up changes on `claude plugin update gborges-standard` or when auto-update is enabled for the marketplace, which is off by default for non-Anthropic marketplaces. Cloud sessions running off a cached environment snapshot keep whatever the setup script installed when the snapshot was built, so bump the `rev` comment in `scripts/cloud-bootstrap.sh` too when a change needs to land immediately.

## Verifying the hook

The `SessionStart` hook is the fragile part of this design, and a hook that stops firing produces no error. To check it:

```bash
claude -p "Was any text about working conventions injected into your context at session start? If yes, quote the exact first bullet under the Prose heading. If not, reply exactly NONE."
```

Confirm it fails as well as passes. Run `claude plugin disable gborges-standard@gborges`, repeat, and expect `NONE`.

`claude plugin list` is the cheaper first check, since an unresolved dependency reports as `failed to load` there and produces `NONE` above for a reason that has nothing to do with the hook. `claude plugin details gborges-standard` prints the component inventory that actually loaded.

## Open cleanup

`~/.claude/CLAUDE.md` still states the prose, git, and plan rules that `CONVENTIONS.md` now carries, so a local session in a bundle-enabled repo receives both. This is deliberate for now: trimming user scope first would silently strip the rules from every repo not yet converted.

Once the repos in regular use all declare this marketplace, cut `~/.claude/CLAUDE.md` down to the commit signing keys alone, which are the one thing that cannot travel to a cloud sandbox and are deliberately absent from `CONVENTIONS.md`.
