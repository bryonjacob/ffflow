# The Audit Subsystem

Authoritative source for audit design is [`architecture.md`](architecture.md) §5.6 and §4.2. This doc is the friendly summary.

## What audit is for

Anything worth keeping aligned with reality gets an auditor.

The audit subsystem is the **keep-honest layer**. It detects drift between artifacts and the reality they claim to describe — CLAUDE.md vs. the code it documents, spec vs. the behavior it specifies, characterization tests vs. the safety net they're supposed to be, architecture rules vs. the actual dependency graph.

## The shape

One coordinator, six per-type auditors. The coordinator dispatches. The auditors do the work.

```
audit                            Coordinator skill. Dispatch + aggregate + render.
  cartridges/
    ├─ claude-md.md              CLAUDE.md coverage, freshness, sanity
    ├─ spec.md                   Spec freshness against current code
    ├─ char-tests.md             Characterization tests still passing
    ├─ architecture.md           No drift from declared architecture
    ├─ refactor.md               Complexity, LoC, duplication, hot spots
    └─ rid.md       (L3 only)    Wraps specdrive audit
```

## How auditors run

Three modes, same auditors:

- **Interactively** — `audit` or `audit --type spec` produces a human-readable report.
- **As CI checks** — each auditor produces machine-readable output that `ci-gates` workflows act on.
- **On schedules** — periodic background runs that surface findings as plans.

## State file

Audit state lives in `.ffflow/audit.yaml`. Each auditor records what it has validated, when, and against which commit. See [`architecture.md`](architecture.md) §4.2 for the schema.

The state file lets auditors detect drift cheaply: if the code in scope hasn't changed since last validation, no re-validation is needed.

## Findings → plans

`audit --plan` converts above-threshold findings into a plan at `plan/audit-<slug>/`. That plan flows through the normal pipeline (`plan-breakdown → plan-capture → work`). Drift becomes work, not a wall of warnings.

Small fixes auto-resolve (e.g., one stale CLAUDE.md → regenerate). Large fixes surface as plan tasks (e.g., dozens of stale specs → triage and queue).

## Per-level applicability

- **L0** — `/audit --type claude-md` only (if CLAUDE.md exists), `/audit --type refactor` (basic)
- **L1** — + `/audit --type architecture`
- **L2** — + `/audit --type spec`, + `/audit --type char-tests`
- **L3** — + `/audit --type rid` (wraps specdrive)

## See also

- [`architecture.md`](architecture.md) §5.6 — full auditor specs
- [`architecture.md`](architecture.md) §4.2 — `.ffflow/audit.yaml` schema
- [`workflows.md`](workflows.md) — the maintenance loop
