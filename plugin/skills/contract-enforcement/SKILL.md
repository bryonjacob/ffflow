---
name: contract-enforcement
description: Mocks must be anchored to verifiable contracts — typed mocks against ports, adapter tests on the same interface, OpenAPI schema generation, consumer-driven contracts. L2+ reference rulebook.
---

# contract-enforcement

## Purpose

Reference rulebook (L2+). Loaded as context by `work-issue` and `plan-chat` when ports are involved. Not invoked as a tool.

Every mock is a claim about how a dependency behaves. That claim can become a lie. Anchor every mock to a verifiable contract.

## The Rule

If you mock a dependency, there must be a corresponding test that proves the real dependency behaves the way your mock claims. No exceptions.

## Within Hexagonal Architecture

The ports ARE the contracts. This is free when done right.

- **Port interface** (TypeScript type or Python Protocol/ABC) defines the contract.
- **Unit tests** mock against the interface type. Not ad-hoc mocks. Not partial mocks. The full typed interface.
- **Adapter tests** verify the real implementation satisfies the same interface.
- **CI gate:** If a port interface changes, both mock-based unit tests and adapter tests must update together. A change to one without the other fails review.

The hexagonal architecture makes this natural. The port is the single source of truth. Mocks are typed against it. Adapters implement it. Both sides are tested against the same contract.

## Cross-Language Boundaries

When a FastAPI backend serves a TypeScript frontend, types drift. Schema generation prevents it.

```
1. Pydantic models define the source of truth
2. FastAPI's app.openapi() exports the OpenAPI schema
3. openapi-typescript generates TypeScript types from the schema
4. Frontend imports generated types
```

If the backend changes shape, the frontend won't compile. The contract is enforced at build time, not at runtime.

CI check:

```bash
python scripts/export_openapi.py
npx openapi-typescript openapi.json -o frontend/src/api/types.ts
git diff --exit-code frontend/src/api/types.ts
```

If the generated types changed without being regenerated and committed, the build fails. No silent drift.

## Service-to-Service Boundaries

When you don't control both sides, or services live in separate repos with separate teams, use **Pact** for consumer-driven contract testing.

- The consumer defines what it expects from the provider.
- The provider verifies it can satisfy every consumer's contract.
- Contracts are versioned and published to a Pact Broker.
- Provider builds verify against all consumer contracts before deploying.

This inverts the usual integration test model. Instead of the provider defining the API and hoping consumers adapt, consumers declare their needs and the provider proves it meets them.

## CI Gate

Contract types must be regenerated and committed in every PR that changes a port interface. Gate 4 (Maintainability) enforces this. A PR that changes a Pydantic model without updating the generated TypeScript types fails the build.

The contract is the boundary. The boundary is tested from both sides. Neither side can change without the other knowing.
