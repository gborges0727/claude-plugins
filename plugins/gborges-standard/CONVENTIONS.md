# Working conventions

These apply to everything produced in this session: chat replies, commit messages, PR bodies, docs, plans, and audit reports.

## Prose

- **Never use em dashes, in any context.** Use commas, parentheses, or separate sentences instead. The same holds for the clause-joining semicolon and colon. Prefer discrete sentences.
- **Cut packaging.** Drop any clause whose only job is to rate, preface, or re-flag another clause.
- **Drafting anything longer than a paragraph** uses the `writing-voice` skill.

## Git

- Use [Conventional Commits](https://www.conventionalcommits.org/), `type(scope): subject`.
- **Never add an AI-attribution trailer** to a commit message or PR body. No `Co-Authored-By: Claude`, no generated-with footer. This holds even when a commit template or tool guide suggests one.
- Commit messages and PR titles use single quotes only, never double quotes.

## Plans and proposals

- **No time estimates.** No hour, day, week, or sprint sizing on phases or work items. Duration estimates are almost always wrong and are not what gets reviewed.
- **No phase-sequencing nudges.** Phases are useful as natural chunks of work that can be built and tested independently. They are not a calendar. Do not suggest shipping phase 1 first and deferring the rest, or starting with phase X to see how it goes. Present all phases as parts of one cohesive plan.
- **Open decisions are still welcome.** If a choice genuinely changes how the plan is built, surface it so it can be answered before the plan continues. Skip rhetorical "what should we do next" closers.
