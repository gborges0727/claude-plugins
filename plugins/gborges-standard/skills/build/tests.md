# Good and bad tests

## A good test

A good test calls the public interface and checks the result a caller would
see. It reads like a statement of what the code can do, and it still passes
when the code underneath is rewritten.

```typescript
// GOOD: checks what a caller sees
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

- The name says what the code does for its caller.
- Only public functions are called.
- One logical check per test.
- The expected value is a known literal, not a recomputation.

## A test tied to the implementation

```typescript
// BAD: checks how checkout works inside
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

The signs are a mocked internal collaborator, a private method under test, a
check on how many times something was called, a name that describes the
steps instead of the outcome, and a test that breaks on a refactor that
changed no behaviour.

## A test that bypasses the interface

```typescript
// BAD: reads the database to check what createUser did
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD: checks through the next public call
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

## A test that passes by construction

When the expected value is computed the same way the code computes it, the
test can never disagree with the code.

```typescript
// BAD: the expected value repeats the implementation
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, i) => sum + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// GOOD: the expected value is a known literal
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```

The expected value comes from somewhere the code cannot influence: a
worked example, the spec, a number you checked by hand.
