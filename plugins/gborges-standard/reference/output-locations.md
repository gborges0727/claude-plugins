# Where skills write their output

The skills in this plugin that produce a document (`spec`, `wayfinder`,
`research`, `handoff`, `routine`) all decide where it goes the same way.
This file is that rule. Each skill points here instead of restating it.

## The repo file

A repo can carry `.claude/gborges-standard.json` at its root, committed like
any other file. The `/setup-repo` command writes it. Two keys matter here:

| Key | Values | Default | What it controls |
|---|---|---|---|
| `docs` | a folder name | `docs` | the folder every document goes under |
| `tracker` | `files` or `github` | `files` | whether specs and tickets also become GitHub issues |

A missing file, a missing key, or a value that is not a string means the
default. The file with the same name under `~/.claude/` holds machine
settings (`fable`, `codex`) and never these keys.

## Defaults

With `docs` set to `docs`, the skills write here. `<slug>` is a short
kebab-case name for the piece of work, chosen from the ask.

| Document | Path |
|---|---|
| a spec | `docs/specs/<slug>.md` |
| the tickets for a spec | `docs/specs/<slug>/tickets/NN-<slug>.md`, numbered from `01` |
| a wayfinder map | `docs/specs/<slug>/map.md`, with one file per open question at `docs/specs/<slug>/questions/NN-<slug>.md` |
| a research note | `docs/research/<slug>.md` |
| a handoff | `docs/handoff/<slug>.md` |
| a routine spec | `docs/routines/<slug>.md` |

Create a folder the first time something goes in it.

## When the user names a place

Anything the user says in the invocation wins over the file and the
defaults. "Put it in Bear" means the `bear-notes` skill. A path means that
path. "File it" or "open an issue" means a GitHub issue through `gh`, whatever
`tracker` says.

## GitHub issues

When `tracker` is `github`, `spec` and `wayfinder` also open one issue per
spec, ticket, map, or question, in dependency order so a ticket can name the
issue that blocks it. The file under `docs/` is still written and is the
copy the next session reads. When `tracker` is `files`, nothing touches
GitHub unless the user asks.
