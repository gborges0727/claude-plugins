# CONTEXT.md format

## Structure

```md
# {Context name}

{One or two sentences on what this area of the system is and why it exists.}

## Language

**Order**:
{A one or two sentence definition.}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## Rules

- **Pick one word.** When several words exist for one concept, choose the
  best and list the others under `_Avoid_`.
- **Keep definitions short.** One or two sentences. Say what the thing is,
  not what it does.
- **Only this project's terms belong.** A general programming concept
  (timeout, error type, retry) stays out even when the project uses it
  everywhere. Before adding a term, ask whether it is unique to this
  project.
- **Group under subheadings** when the terms fall into natural clusters. A
  flat list is fine when they do not.

## One glossary or several

Most repos keep one `CONTEXT.md` at the root.

A repo whose parts speak different languages (an ordering system and a
billing system that mean different things by "account") keeps a
`CONTEXT-MAP.md` at the root and one `CONTEXT.md` per part, next to that
part's code. The map lists the parts, where each glossary lives, and how the
parts talk to each other:

```md
# Context map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md): receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md): generates invoices and processes payments

## Relationships

- **Ordering → Billing**: Ordering emits `OrderPlaced` events and Billing reads them to raise invoices
- **Ordering ↔ Billing**: both use the shared `CustomerId` and `Money` types
```

Read the map when it exists to find the glossary for the current topic. With
only a root `CONTEXT.md`, that is the glossary. With neither, create a root
`CONTEXT.md` when the first term settles.
