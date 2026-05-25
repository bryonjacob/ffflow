# Justfile cartridge: Tier 4 — polyglot orchestration

## Purpose

Tier 4 of the justfile maturity ladder: multi-language orchestration. The structural shape of the root justfile — fan-out helpers, subproject targets, check-all aggregation — lives in [the polyglot stack cartridge](../stack/cartridges/polyglot.md). It owns that shape because polyglot is a stack-level decision; the recipe bundle is downstream of it.

This skill carries the **additional polyglot-specific recipes** that don't belong in the root template but are useful at Tier 4.

Loaded by `stack-init` when the project uses the polyglot stack cartridge.

## What lives in the polyglot stack cartridge

- Root justfile structural template (`templates/root-justfile`).
- Subproject directory layout (`backend/`, `frontend/`, etc.).
- Per-subproject `level_override` configuration.
- Subproject lifecycle (add / remove / list).

If you need to change how `just check-all` fans out, edit the polyglot stack cartridge and its template.

## Polyglot-specific recipe extensions (Tier 4)

Beyond the structural fan-out, projects at Tier 4 commonly want:

### Cross-subproject contracts

```just
# Regenerate frontend types from backend OpenAPI; fail if anything drifted
contracts:
    cd backend && just export-openapi
    cd frontend && just regenerate-types
    git diff --exit-code frontend/src/api/types.ts
```

Pair with `contract-enforcement` (L2+) — this is how that rulebook becomes an enforced gate.

### Cross-cutting integration

```just
# Full integration suite — each subproject's plus the e2e layer
integration:
    cd backend && just integration-test
    cd frontend && just integration-test
    cd e2e && just e2e-test
```

### Selective fan-out

```just
# Run RECIPE only in subprojects whose name matches PATTERN
match RECIPE PATTERN:
    @for d in $(ls -d */ | grep "{{PATTERN}}"); do \
        (cd "$d" && just {{RECIPE}}) || exit 1; \
    done
```

Useful when a check applies to only some subprojects (e.g., `mutate` on backend + core, not frontend).

## Rules

- **Structural changes belong in the polyglot stack cartridge.** This skill only adds recipes; it doesn't redefine the layout.
- **Cross-subproject recipes are last-resort.** Prefer keeping subprojects independent; only add cross-cutting recipes when there's a real concern that spans them (contracts, integration, security).
- **Match the polyglot stack cartridge's idioms.** If the polyglot stack cartridge uses `_all` for fan-out, don't introduce a parallel `_run-all`.

## Anti-patterns

- Restating the fan-out shape. It lives in the polyglot stack cartridge — point there.
- Adding cross-cutting recipes that hide subproject failures. Each subproject's failure must remain visible.
- Letting cross-subproject contracts run silently — the `git diff --exit-code` check is the gate.

## Friction addressed

- Cross-language contract drift between backend and frontend.
- Integration tests run inconsistently across subprojects.
- Tier 4 recipe sprawl when the structural shape is the same.
