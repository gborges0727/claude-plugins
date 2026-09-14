# When to mock

Mock only where the system meets something you do not control:

- a third-party API (payments, email)
- the database, when no local test database is practical
- the clock and random numbers
- the filesystem, when a real temp directory is not practical

Never mock your own modules, classes, or functions. A test that mocks an
internal collaborator checks how the code is wired, not what it does.

## Making the edges easy to mock

**Pass external dependencies in.** A function that builds its own client
cannot be tested without the real service.

```typescript
// Easy to mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**One function per external operation.** A single generic fetcher forces
every mock to branch on its arguments.

```typescript
// GOOD: each function is mocked on its own
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: one mock has to know every endpoint
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

With one function per operation, each mock returns one shape, a test shows
which endpoints it touches, and each function gets its own types.
