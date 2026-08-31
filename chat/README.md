# The Claude apps version

The plugin in this repo only reaches Claude Code. The Claude apps (web,
desktop, iOS) load nothing from a marketplace. The same rules reach those
apps through the two customization surfaces they do have.

| Claude Code | Claude apps | Carries |
|---|---|---|
| `plain-english.md` output style | Instructions for Claude | Every sentence rule |
| `writing-voice` skill | An uploaded skill | The two-pass document ritual |
| `strip-attribution.py` hook | nothing | Does not port |
| `add-to-git` command | nothing | Does not port |

`chat/build.py` generates both app-side files from the plugin, so the rules
keep one source. The next build overwrites any hand edit to
`chat/instructions-for-claude.md`.

## Install the instructions

`chat/instructions-for-claude.md` is committed, so a phone can open it on
GitHub and copy from there.

1. Open Settings, then **Instructions for Claude**.
2. Paste the file, minus the generated-by comment on the first line.
3. Save.

The field is account-wide and stored server-side, so one paste covers web,
desktop, and iOS. Use a project's own instructions instead when you want the
style on some conversations and not others.

## Install the skill

1. Run `python3 chat/build.py` to produce `chat/dist/writing-voice.zip`.
2. Turn on code execution in Settings. The Skills interface stays hidden
   until you do, and pass 1 of the ritual runs `check.py`.
3. Open Customize, then Skills, then **+**, then Create skill, then Upload a
   skill, and pick the zip.

Anthropic documents skills for web chat, Claude Code, the Microsoft 365
add-ins, and Cowork. It does not document the mobile apps, so treat iOS
support as unconfirmed until you see the skill fire there.

## What the build changes

`build.py` copies `RULES.md`, `EXAMPLES.md`, and `scripts/check.py` from the
plugin untouched. It rewrites the passages in `SKILL.md` that name the
output style or the plugin's file layout. From the output style it drops the
Git and Subagents sections, since the apps write no commits and spawn no
subagents, and it swaps "The second pass" for a version that says the
mechanical scan needs code execution turned on. It also prepends a
chat-only "Banned Sources" block.

Every rewrite is an anchored string replacement. A missing anchor fails the
build instead of shipping the original text. So a plugin edit that
invalidates one of these rewrites shows up as an error here, not as stale
wording in a skill you already uploaded.

## What does not port

The apps expose no hook surface, so nothing enforces the ban on
AI-attribution footers mechanically. The rule survives as text in the
instructions, and that is all. The apps expose no slash commands either, so
`add-to-git` has no equivalent.
