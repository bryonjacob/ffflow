# Stack cartridge: TypeScript

## Purpose

Declare the canonical TypeScript toolchain for FFFlow projects and provide level-aware defaults. Loaded by `init-ffflow` and `stack-init`.

## Dimensions

```yaml
stack: typescript
applies_to: typescript
dimensions:
  package_manager: { tool: pnpm, version: ">=9" }
  formatter: { tool: prettier, command: "prettier --write" }
  linter: { tool: eslint, command: "eslint --fix" }
  type_checker: { tool: tsc, mode: strict }
  test_runner: { tool: vitest }
  coverage_tool: { tool: v8 }              # via @vitest/coverage-v8
  coverage_threshold_line: 95
  coverage_threshold_branch: 90
  complexity_limit: 10
  # L2+
  bdd_runner: { tool: quickpickle, when: "level >= L2" }
  property_runner: { tool: fast-check, when: "level >= L2" }
  bdd_property: { tool: "quickpickle-property", when: "level >= L2" }
  # L3
  mutation_tool: { tool: stryker, when: "level == L3" }
  mutation_threshold: 80
  spec_audit_cli: { tool: specdrive, when: "level == L3" }
```

`.ffflow/stack.yaml` can override any dimension.

## Per-level expectations

| Level | Tools active |
|---|---|
| L0 | pnpm, prettier, eslint, tsc, vitest, v8 coverage |
| L1 | + hexagonal layout |
| L2 | + quickpickle + fast-check + quickpickle-property |
| L3 | + Stryker + specdrive |

## Directory structure

L0/L1:
```
src/
tests/
docs/specs/
```

L2+:
```
src/
  domain/
  application/
  infrastructure/
specs/
  acceptance/
  application/
  domain/
tests/
  unit/
  integration/
```

## Justfile recipes

L0 baseline:

```just
set shell := ["bash", "-uc"]

default:
    @just --list

dev-install:
    pnpm install

# Private guard: detect an empty workspace (no source files yet).
# Used by format/lint/typecheck/test/coverage to early-exit cleanly so the
# initial scaffolding commit can pass pre-commit hooks.
#
# Source paths come from pnpm workspace introspection — works for single-package
# (src/) and multi-package (any pnpm-workspace.yaml `packages:` layout) without
# the cartridge knowing the project's directory shape.
_member_paths:
    @pnpm m ls --json --depth=-1 2>/dev/null | python3 -c "import json,sys; data=json.load(sys.stdin); print('\n'.join(p['path'] for p in data if p.get('path')))" 2>/dev/null || echo "."

_empty:
    @test -z "$(just _member_paths | xargs -I{} find {} \( -name '*.ts' -o -name '*.tsx' \) 2>/dev/null | grep -v node_modules | grep -v -E '\.d\.ts$' | head -1)" && echo yes || echo no

_no_tests:
    @test -z "$(just _member_paths | xargs -I{} find {} \( -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.spec.ts' -o -name '*.spec.tsx' \) 2>/dev/null | grep -v node_modules | head -1)" && echo yes || echo no

format:
    @if [ "$(just _empty)" = "yes" ]; then echo "format: no source files yet"; else pnpm prettier --write .; fi

lint:
    @if [ "$(just _empty)" = "yes" ]; then echo "lint: no source files yet"; else pnpm eslint . --fix --max-complexity 10; fi

typecheck:
    @if [ "$(just _empty)" = "yes" ]; then echo "typecheck: no source files yet"; else pnpm tsc --noEmit; fi

test:
    @if [ "$(just _no_tests)" = "yes" ]; then echo "test: no tests yet"; else pnpm vitest run tests --reporter=verbose; fi

coverage:
    @if [ "$(just _no_tests)" = "yes" ]; then echo "coverage: no tests yet"; else pnpm vitest run tests --coverage --coverage.lines=95; fi

check-all: format lint typecheck coverage
    @echo "All checks passed"

clean:
    rm -rf node_modules dist coverage .vitest reports
```

L2 additions:

```just
spec-test:
    pnpm vitest run specs/ --reporter=verbose

spec-coverage:
    pnpm vitest run specs/ --coverage --coverage.lines=80
```

L3 additions:

```just
mutate:
    pnpm stryker run

spec-audit:
    pnpm specdrive audit
```

## Config files

Templates live in `templates/`. `stack-init` reads them and writes the per-level set into the project:

| File | Template path | When |
|---|---|---|
| `vitest.config.ts` | `templates/vitest.config.ts.L0` | L0/L1 |
| `vitest.config.ts` | `templates/vitest.config.ts.L2` | L2+ (adds quickpickle plugin) |
| `stryker.config.mjs` | `templates/stryker.config.mjs` | L3 only |
| `tsconfig.json` | `templates/tsconfig.json` | All levels |
| `package.json` devDeps | `templates/package.devDeps.L0.json` | L0/L1 baseline |

L2 adds devDeps: `quickpickle`, `quickpickle-property`, `fast-check`.
L3 adds devDeps: `@stryker-mutator/core`, `@stryker-mutator/vitest-runner`, `specdrive`.

## Dual coverage (L2+)

Unit tests enforce 95%. Spec tests enforce 80%. Both must pass.

## Notes

- QuickPickle runs `.feature` files through Vitest. No separate runner needed.
- `quickpickle-property` handles `@property-based` tagged scenarios.
- Stryker validates test strength. Run weekly or pre-release.
- specdrive audit checks RID traceability. Run in CI when L3.

## Anti-patterns

- Skipping `tsc --noEmit` because vitest sees the types. Vitest doesn't catch every TS error your editor does.
- Mixing `tests/` and `specs/` in one vitest pattern at L2. Keep them separate so spec-coverage can have its own threshold.
- Lowering coverage thresholds rather than writing tests.
- Running Stryker on every PR. (Cadence rule lives in `justfile`.)
