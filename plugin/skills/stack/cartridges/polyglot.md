# Stack cartridge: Polyglot

## Purpose

For repos that house multiple languages (e.g., a Python backend + TypeScript frontend, or a Go service with a Rust extension). Provides root-level orchestration; per-language work delegates to the appropriate stack skill.

## Dimensions

```yaml
stack: polyglot
applies_to: polyglot
dimensions:
  orchestrator: { tool: justfile }
  subprojects:
    - { path: backend/, stack: python }
    - { path: frontend/, stack: typescript }
  shared_test_runner: null               # each subproject runs its own
  coverage_aggregation: { strategy: per_subproject }
```

Subprojects are declared in `.ffflow/config.yaml`:

```yaml
stack: polyglot
polyglot:
  subprojects:
    - path: backend/
      stack: python
    - path: frontend/
      stack: typescript
    - path: extension/
      stack: rust-stack             # user-provided stack skill if needed
```

## Per-level expectations

Level applies to the whole repo. Each subproject inherits the level. If a subproject needs a different level (rare but real), declare it explicitly:

```yaml
polyglot:
  subprojects:
    - path: backend/
      stack: python
      level_override: L3
    - path: frontend/
      stack: typescript
      # inherits L1
```

**Why per-subproject overrides are allowed:** real polyglot repos often have mature core service (L3, full FFFlow rigor) alongside young supporting code (L1, light hex layering). Forcing both to the same level either under-protects the core or over-burdens the new code. The override exists for this case. Use sparingly — divergent levels complicate every audit. When in doubt, keep them equal.

## Directory layout

```
project-root/
├── .ffflow/config.yaml
├── justfile                     # root orchestration
├── backend/
│   ├── justfile                 # python cartridge justfile
│   ├── pyproject.toml
│   └── src/
└── frontend/
    ├── justfile                 # typescript cartridge justfile
    ├── package.json
    └── src/
```

## Root justfile

```just
— see `templates/root-justfile` for the canonical template (subproject list expanded by `stack-init`).
```

`cd <dir> && just <recipe>` runs the recipe inside `<dir>`'s justfile. Each subproject has its own. (Earlier versions used `just -d <dir>`, but `just` 1.16+ requires `--justfile` paired with `--working-directory`; the `cd` form works on every version.)

## CI integration

The `ci-gates` workflow for polyglot projects has a matrix:

```yaml
strategy:
  matrix:
    subproject: [backend, frontend]

steps:
  - name: Setup tools for subproject
    run: |
      cd ${{ matrix.subproject }}
      # stack-specific setup
  - name: check-all
    run: cd ${{ matrix.subproject }} && just check-all
```

Or, simpler: a single job that runs `just check-all` at the root, since the root recipe fans out. Tradeoff: matrix gives parallelism; single job is easier to read.

## Audit integration

`/audit` walks subprojects:

1. For each subproject, run the applicable auditors against that subproject's tree.
2. Aggregate findings into a single report, grouped by subproject.

Subprojects share `.ffflow/audit.yaml` (one source of truth), but each auditor's `files:` section uses repo-absolute paths.

## Cross-subproject dependencies

When a backend contract change must reach a frontend type:

- Use `contract-enforcement` (L2+).
- The OpenAPI / type-generation step runs in the root `check-all` via:
  ```just
  contracts:
      cd backend && just export-openapi
      cd frontend && just regenerate-types
      git diff --exit-code frontend/src/api/types.ts
  ```

## Anti-patterns

- Mixing source for two languages in the same directory. Subproject = directory boundary.
- Sharing a `node_modules/` or `.venv/` across subprojects. Each subproject installs its own.
- Running mutation testing across all subprojects on every PR. (See `justfile` for the per-PR-vs-scheduled rule.)
- Letting one subproject's `check-all` skip on failure of another. Each subproject's failure is fatal.

## Friction addressed

- Coordinating per-language tooling without making each subproject know about the others.
- CI workflows that have to be edited any time a new subproject is added (root justfile takes the change).
- Drift between front and back when nobody enforces the contract.
