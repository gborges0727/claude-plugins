# Learning record format

Learning records live in `learning-records/`, numbered in order:
`0001-slug.md`, `0002-slug.md`. Create the folder with the first record.
To number a new one, find the highest number in the folder and add one.

A record captures something the user has shown they understand, a piece of
prior knowledge they told you about, or a misconception that got corrected.
Together the records say what to teach next.

## Template

```md
# {Short title of what was learned or established}

{One to three sentences: what was learned, and why it changes what to teach
next.}
```

A record can be one paragraph. Its value is that the fact is written down,
not that every section is filled.

## Optional sections

Add one only when it says something the paragraph does not.

- **Status** in frontmatter (`active`, `superseded by LR-NNNN`), when a
  later record replaces this one.
- **Evidence**: how the user showed it. A question answered, an exercise
  completed, prior experience described. Useful when the claim might be
  doubted later.
- **Implications**: what this opens up or rules out for later sessions.

## When to write one

Any one of these:

1. **The user showed they understand something.** Evidence they can use
   the concept correctly, not that they saw it once. This raises the floor
   for what to teach next.
2. **The user told you what they already know.** Record it, with how deep
   they said it goes, so no session re-teaches it.
3. **A misconception was corrected.** The user believed something wrong
   and now sees why. These predict where they will stumble next in related
   topics.
4. **The mission moved because of what they learned.** Record the change
   and update `MISSION.md`.

## What does not get a record

- Material that was covered. Covering is not learning. Wait for evidence.
- A term already defined in `GLOSSARY.md`.
- A log of what happened in the session. Records hold insights, not
  activity.

## When a later record contradicts an earlier one

Mark the old record `Status: superseded by LR-NNNN` instead of deleting
it. How the user's understanding changed is useful later.
