# Decision record format

A decision record (ADR) lives in `docs/adr/` and is numbered in order:
`0001-slug.md`, `0002-slug.md`. Create the folder when the first record is
written. To number a new one, find the highest number in the folder and add
one.

## Template

```md
# {Short title of the decision}

{One to three sentences: the situation, what was decided, and why.}
```

A record can be one paragraph. Its value is that the decision and its reason
are written down, not that every section is filled.

## Optional sections

Add one only when it says something the paragraph does not.

- **Status** in frontmatter (`proposed`, `accepted`, `deprecated`,
  `superseded by ADR-NNNN`), for a decision that gets revisited.
- **Considered options**, when the rejected alternatives are worth
  remembering.
- **Consequences**, when the decision has downstream effects a reader would
  not expect.

## When to write one

All three must hold.

1. **Hard to reverse.** Changing your mind later costs real work.
2. **Surprising without context.** A future reader would look at the code
   and wonder why it was done this way.
3. **A real trade-off.** There were alternatives and one was chosen for
   specific reasons.

An easy-to-reverse decision needs no record, since you would reverse it.
An unsurprising one raises no question. A decision with no alternative has
nothing to record beyond "we did the obvious thing".

## What qualifies

- **How the system is put together.** "One repo for every package."
  "Writes are event-sourced and reads come from a Postgres projection."
- **How parts talk to each other.** "Ordering and Billing exchange events,
  never synchronous HTTP calls."
- **Technology choices that would take a quarter to swap.** The database,
  the message bus, the auth provider, the deployment target. Not every
  library.
- **Ownership and scope.** "Customer data belongs to the Customer area.
  Other areas hold only the id." A decision about what a part will not do
  is as useful as one about what it will.
- **A deliberate departure from the obvious.** "Hand-written SQL instead of
  an ORM, because X." The record stops the next engineer from "fixing" it.
- **A constraint the code does not show.** "No AWS, for compliance." "Under
  200 ms per response, per the partner contract."
- **A rejected alternative when the reason is not obvious.** Record why REST
  won over GraphQL, or someone will propose GraphQL again in six months.
