---
name: op-run
description: >-
  Get credentials to a command through 1Password, so the secret reaches the process and never the
  transcript. Use when a command needs a credential you do not have, when a tool fails on a missing
  or invalid key, when the user asks to add, rotate, or move a secret, and when setting up secrets
  for a new project.
---

# Running commands that need secrets

Never fetch a value. Get it to the process instead.

Three ways, and the project has already picked one. Read its `CLAUDE.md` before
assuming.

## Which one is in play

Run `ls -la` on the directory holding the env file and read the first character
of the mode.

A `p` means a named pipe, so 1Password is mounting the file from an Environment:

```
prw-------  1 you  staff  0 Aug 14 18:24 .env
```

Nothing to do. Commands run unwrapped, because the file the app already reads is
the pipe:

```sh
npm run dev
```

The mount is live only while 1Password runs and stays unlocked. Values edited in
the app take effect on the next read, with no remount.

A `-` means a regular file holding `op://` references, so commands get wrapped:

```sh
op run --env-file=server/.env -- npm run dev
```

`op` resolves the references, hands the values to that one subprocess, and takes
them away when it exits.

The third way names an Environment on the command line, which needs a beta build
of the CLI:

```sh
op run --environment <id> -- npm run dev
```

`op environment --help` erroring with `unknown command` means the build is
stable and only the first two ways work. That command has one subcommand,
`read`, and no way to list Environments or look one up by name. The ID comes
from the desktop app, under Manage environment, then Copy environment ID.

## Why fetching loses

Every byte a command prints becomes tool output. Tool output enters the context
window, travels to the API, and is written to a transcript file on the user's
disk in plain text. So `op read`, `printenv`, and `cat .env` each turn a vaulted
secret back into the thing the vault was bought to prevent, and that copy
outlives the session.

`op run` also masks secrets that leak into a subprocess's output, so a stack
trace printing a connection string arrives redacted.

## Diagnosing a credential failure

An auth error, a 401, or a config parser rejecting an empty value all mean the
same thing: the variable did not arrive. Test presence, never the value.

```sh
node --experimental-strip-types -e "process.loadEnvFile(); const ks=['DATABASE_URL','API_KEY']; for (const k of ks) console.log(process.env[k] ? 'set   ' : 'absent', k)"
```

Read the config schema before calling anything broken. Most projects give most
variables defaults, so a short env file is normal rather than a fault, and only
the ones the schema marks required can actually stop a boot. Naming a defaulted
variable as missing sends the user chasing a problem that is not there.

Done when the command runs and every variable the schema requires reports
present.

## Adding, rotating, or moving a secret

The value passes through the human, because you cannot hold one. Give them the
exact steps and let them run them.

An Environment is created and edited in the desktop app, under Developer then
Environments. Its "Import .env file" button loads a whole file at once, and
"Connect" mounts one locally. The CLI only reads Environments.

For a vault item instead, have the user pipe JSON into `op item create -` rather
than passing values as arguments, so nothing crosses `argv` where `ps` could see
it.

Done when the user confirms the values are in, and a presence check reports every
required variable.

## Denials are the rule working

Projects using this deny reading the env file and deny `op read` in
`.claude/settings.json`. Renaming a file or moving a command into a script to get
past a hook defeats the same protection by hand.

When a denial stops you verifying something, say so and hand the command to the
user. An unverified claim stated as fact is worse than an admitted gap, and it is
worst in a commit message, which outlives the conversation that excused it.

## CI

A service account token in `OP_SERVICE_ACCOUNT_TOKEN` makes `op run` work
headless. Mounting is a desktop feature and does not apply there.

Scope the token to one vault or one Environment, so a leak reaches that project
and nothing else the user owns. One `op run` around the whole job beats many
separate reads, because service accounts are rate limited per request.
