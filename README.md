# claude-plugins

Gabe Borges' personal Claude Code marketplace. One bundle plugin, `gborges-standard`, carrying the working conventions, skills, and third-party plugins used across every repo.

It exists because Claude Code cloud sessions do not read user-scope config in `~/.claude/`. Anything that lives only there is missing the moment work happens outside a local terminal. Declaring this marketplace in a repo's `.claude/settings.json` gives that repo the same setup a local session has, and edits here propagate to every repo without touching any of them.

## Use it in a repo

Add to the repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "gborges": {
      "source": { "source": "github", "repo": "gborges0727/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "gborges-standard@gborges": true
  }
}
```

One marketplace, one plugin. The three bundled plugins live in `claude-plugins-official`, which Claude Code registers automatically, so nothing else needs declaring.

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

Add it to the `dependencies` array in `plugins/gborges-standard/.claude-plugin/plugin.json`. If it comes from `claude-plugins-official`, that is the only edit anywhere, and every consuming repo picks it up.

If it comes from any other marketplace, a dependency on it resolves only in sessions that already registered that marketplace, and it fails silently otherwise. Rather than adding the marketplace to every repo, add the plugin as a second entry in `.claude-plugin/marketplace.json` using a `git-subdir` source pointing at its upstream repo. The dependency then resolves inside `gborges` and consuming repos stay at one marketplace.

Bump `version` in `plugin.json` when the set changes. Local sessions pick up changes on `claude plugin update gborges-standard` or when auto-update is enabled for the marketplace, which is off by default for non-Anthropic marketplaces. Cloud sessions install fresh each time and always get the latest.

## Verifying the hook

The `SessionStart` hook is the fragile part of this design, and a hook that stops firing produces no error. To check it:

```bash
claude -p "Was any text about working conventions injected into your context at session start? If yes, quote the exact first bullet under the Prose heading. If not, reply exactly NONE."
```

Confirm it fails as well as passes. Run `claude plugin disable gborges-standard@gborges`, repeat, and expect `NONE`.

## Open cleanup

`~/.claude/CLAUDE.md` still states the prose, git, and plan rules that `CONVENTIONS.md` now carries, so a local session in a bundle-enabled repo receives both. This is deliberate for now: trimming user scope first would silently strip the rules from every repo not yet converted.

Once the repos in regular use all declare this marketplace, cut `~/.claude/CLAUDE.md` down to the commit signing keys alone, which are the one thing that cannot travel to a cloud sandbox and are deliberately absent from `CONVENTIONS.md`.
