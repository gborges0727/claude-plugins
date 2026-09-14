---
name: teach
description: Teach the user a topic over many sessions, keeping the lessons, references, and what they have learned as files in the current directory. Explicit invocation only.
argument-hint: "What would you like to learn about?"
disable-model-invocation: true
---

# Teach

The user wants to learn something, over more than one session. The current
directory is the classroom, and its files hold where the learning stands.

## The files

- `MISSION.md` says why the user wants to learn this. Every lesson traces
  back to it. Format in [MISSION-FORMAT.md](MISSION-FORMAT.md).
- `RESOURCES.md` lists the trusted sources you teach from and the
  communities where the user can test what they learned. Format in
  [RESOURCES-FORMAT.md](RESOURCES-FORMAT.md).
- `GLOSSARY.md` holds the terms the user now understands, one definition
  each. Format in [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md).
- `learning-records/NNNN-<slug>.md` record what the user has shown they
  understand, one insight per file. They tell you what to teach next.
  Format in [LEARNING-RECORD-FORMAT.md](LEARNING-RECORD-FORMAT.md).
- `lessons/NNNN-<slug>.html` are the lessons, one self-contained HTML file
  each, numbered in order.
- `reference/*.html` are the cheat sheets: syntax, algorithms, sequences,
  anything the user will come back to look up.
- `assets/*` are pieces shared across lessons: the stylesheet, quiz
  widgets, diagrams, simulators.
- `NOTES.md` is your own scratch file for how the user likes to be taught.

Create a file or folder the first time you have something to put in it.

## How people learn

The user needs three things. Knowledge comes from trusted sources.
Skills come from practising with feedback, in lessons you design from that
knowledge. Judgement comes from other people who do the thing, so the
final step of learning is a community.

Until `RESOURCES.md` has good sources in it, finding them is the first
job. Never teach from memory alone.

Some topics are mostly knowledge (theoretical physics). Some are mostly
skill (yoga). Weight the lessons to match.

Being able to recall something right after reading it feels like mastery
and is not. Long-term retention is the goal, and it comes from effort:
recalling from memory instead of rereading, spacing practice over days,
and mixing related skills in one practice session.

## The mission

When `MISSION.md` is missing or vague, your first job is to ask why the
user wants this, until the answer is concrete. "Run a half marathon by
October" and "ship a Rust CLI to my team" are missions. "Understand X" is
not. Without a mission, lessons come out abstract and you cannot tell what
to teach next.

Missions change as the user learns. Confirm with the user, then update the
file and write a learning record.

## What to teach next

When the user names the thing, teach that. Otherwise read the learning
records and the mission, and pick the most useful thing that sits just past
what they can already do. Each lesson should feel like a stretch and not a
wall.

## A lesson

A lesson is one HTML file that teaches one small thing tied to the mission
and gives the user one win they can build on. Keep it short. Working memory
is small.

Publish it as a Claude artifact by default, so the user can open it on any
device, and save the same file under `lessons/`. Send it somewhere else
only when the user asks.

Each lesson:

- links its stylesheet and any widgets from `assets/`, so every lesson
  looks like part of one course. Read `assets/` before writing, reuse what
  is there, and put anything a second lesson could reuse there too.
- teaches the knowledge first, then has the user practise the skill with
  immediate feedback: a quiz, a small in-browser task, or a checklist of
  real-world steps.
- cites its sources inline, so every claim can be checked.
- links to related lessons and reference pages by anchor.
- names the one best source to read or watch next.
- reminds the user they can ask you follow-up questions.

For a quiz, give every answer the same number of words, so the formatting
gives nothing away. Keep the layout clean and readable, so a lesson reads
well when the user returns to it.

## Reference pages

While writing lessons, also write the reference pages the user will look
things up in later: syntax and snippets for a language, steps and
flowcharts for a process, poses and sequences for yoga, routines for
fitness, a glossary for anything with its own words. Lessons are read once.
Reference pages are read many times, so make them dense and quick to scan.

## The community

When the user asks something that needs judgement from experience, answer
as best you can and then point them at people. Find a well-moderated
forum, a subreddit, a local class, or an interest group where they can try
what they learned on others. When the user says they do not want a
community, drop it.

## NOTES.md

When the user says how they like to be taught, or asks you to keep
something in mind, write it here and read it before designing a lesson.
