---
name: hexagonal-architecture
description: Domain / Application / Infrastructure layers — ports, adapters, the dependency rule, and how layers map to spec types and test strategies. L1+ reference rulebook.
---

# hexagonal-architecture

## Purpose

Reference rulebook (L1+). Loaded as context by `plan-chat`, `work-issue`, and `/audit --type architecture`. Not invoked as a tool.

Three layers. Dependencies point inward. Nothing else.

## The three layers

### Domain

Pure business logic. Zero external dependencies. No database, no HTTP, no framework, no I/O.

Contains:
- **Entities** — objects with identity and lifecycle (`User`, `Order`).
- **Value Objects** — immutable, defined by attributes (`Password`, `EmailAddress`, `Money`).
- **Domain Services** — stateless logic not owned by a single entity.
- **Domain Events** — records of things that happened.

Domain code is fully deterministic and testable in isolation.

### Application

Orchestration. Depends on domain. Defines ports.

Contains:
- **Use Cases** — coordinate domain objects to fulfill a request (`LoginUseCase`, `PlaceOrderUseCase`).
- **Ports** — interfaces that abstract external dependencies (`UserRepository`, `TokenService`, `EmailService`).
- **Commands and Queries** — input/output DTOs.

Application code depends on domain and port interfaces. It never depends on concrete infrastructure.

### Infrastructure

Adapters that implement ports using concrete technologies.

Contains:
- **Repository implementations** — `PostgresUserRepository`, `RedisSessionStore`.
- **External service clients** — `StripePaymentGateway`, `SendGridEmailService`.
- **Framework integration** — HTTP controllers, CLI handlers, message consumers.

Infrastructure depends on application (implements ports) and domain (uses domain types).

## Dependency rule

```
Domain ← Application ← Infrastructure
```

Domain knows nothing about application or infrastructure. Application knows nothing about infrastructure. Infrastructure depends on both. No exceptions.

Enforced by `/audit --type architecture` at L1+.

## Directory structure

```
project-root/
├── src/
│   ├── domain/<context>/
│   ├── application/<context>/
│   └── infrastructure/<adapter-type>/
└── tests/
    ├── domain/<context>/
    ├── application/<context>/
    └── infrastructure/<adapter-type>/
```

L2+ adds Gherkin specs:

```
specs/
└── <context>/
    ├── <feature>.feature                 # Acceptance specs
    ├── domain/<entity>.feature           # Domain specs
    └── application/<use-case>.feature    # Application specs
```

Specs in `specs/`. Source in `src/`. Tests in `tests/`. No mixing.

## Layer-to-spec mapping (L2+)

| Layer          | Spec type         | What it specifies                                    |
|----------------|-------------------|------------------------------------------------------|
| Domain         | Domain specs      | Entity invariants, value object rules, service contracts |
| Application    | Application specs | Use case orchestration, port interactions            |
| Infrastructure | (none)            | Adapters have no Gherkin specs                       |
| Cross-cutting  | Acceptance specs  | Stakeholder-visible end-to-end behavior              |

## Layer-to-test mapping

| Layer          | Spec tests (L2+) | Unit tests | What each covers                                                   |
|----------------|------------------|------------|--------------------------------------------------------------------|
| Domain         | Yes              | Yes        | Spec tests: behavioral rules. Unit tests: branches, edge cases.    |
| Application    | Yes              | Yes        | Spec tests: orchestration flows. Unit tests: internal logic.       |
| Acceptance     | Yes              | No         | Spec tests only. Drive system through application ports.           |
| Infrastructure | No               | Yes        | Unit/integration tests only. Real infra (testcontainers, etc.). No RIDs. |

Domain and application get both test types. Acceptance is spec-only. Infrastructure is unit-only.

### Domain tests
- Zero external dependencies.
- Call domain objects directly.
- Property tests use `@property-based` at L2+ (Hypothesis / fast-check).
- Fastest tests in the system.

### Application tests
- Mock infrastructure ports; use real domain objects.
- Step definitions call use cases through their public API.

### Acceptance tests
- Drive through application ports.
- Infrastructure mocked at the port boundary.
- Integration across domain and application.

### Infrastructure tests
- Not Gherkin-driven.
- Real infrastructure (testcontainers, test servers, temp directories).
- No RIDs — they verify infrastructure contracts, not business behavior.

## Per-level expectations

| Level | Hex enforcement |
|---|---|
| L0 | Optional. Encouraged for projects expecting growth. |
| L1 | Recommended. Layer separation, no audit enforcement yet. |
| L2 | Required if `architecture.style: hexagonal` in config. `/audit --type architecture` runs. |
| L3 | Required. Full enforcement; violations are blocking. |

## Conventions

- Ports defined in `application/`. Adapters in `infrastructure/`. Never co-locate.
- Domain types crossing layers: fine (`Money` can be passed everywhere).
- Adapter types in domain: never (`PostgresConnection` in `User`: forbidden).
- DTOs for crossing the application boundary inward. Plain dicts/objects are fine.

## Anti-patterns

- Anemic domain models (data + getters/setters with logic elsewhere).
- "Manager" or "Helper" classes in domain that depend on infrastructure.
- Ports defined in domain. Domain knows nothing about external dependencies; ports are application's concern.
- Mocking domain in domain tests. Domain is the lowest layer — there's nothing below it to mock.
- Skipping layer separation "until later." Later never comes for free.

## Friction addressed

- Layering decisions made in CLAUDE.md but never enforced.
- Drift across releases as junior devs add convenient imports.
- Test strategies that don't match the layer (mocking domain, real-DB-ing every test).
