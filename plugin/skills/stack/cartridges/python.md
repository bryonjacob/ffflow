# Stack cartridge: Python

## Purpose

Declare the canonical Python toolchain for FFFlow projects and provide level-aware defaults. Loaded by `init-ffflow` and `stack-init` for tool detection and config generation.

## Maximum level: L3

**Python projects can adopt FFFlow at any level, L0 through L3.** FFFlow's L3 RID-traceability gate is implemented by [`specdrive`](https://github.com/bryonjacob/specdrive), a language-agnostic CLI. It operates on Gherkin `.feature` files and JUnit XML test output — both universal formats — so it audits a Python project exactly as it audits a TypeScript one. specdrive is distributed via npm, but that is its *install channel*, not a constraint on what it can audit: you run it via `npx specdrive` (or a globally/locally installed `specdrive`) alongside `uv`, the same way you'd reach for any external CLI dev tool. Mutation testing via `mutmut` rounds out the L3 gates.

The only prerequisite for L3 on Python is that Node.js/npm is available to run specdrive (it ships no Python wheel — and doesn't need one). `stack-init` checks for `npx` at L3 and tells you to install Node if it's missing.

## Dimensions

The stack's declared shape. Other skills (and `.ffflow/stack.yaml` overrides) read this.

```yaml
stack: python
applies_to: python
max_level: L3
dimensions:
  package_manager: { tool: uv, version: ">=0.4" }
  formatter: { tool: ruff, command: "ruff format" }
  linter: { tool: ruff, command: "ruff check" }
  type_checker: { tool: mypy, mode: strict }
  test_runner: { tool: pytest }
  coverage_tool: { tool: coverage.py }
  coverage_threshold_line: 95          # L0–L2 default
  coverage_threshold_branch: 90
  complexity_limit: 10
  # L2+
  bdd_runner: { tool: pytest-bdd, when: "level >= L2" }
  property_runner: { tool: hypothesis, when: "level >= L2" }
  bdd_property: { tool: pytest-bdd-property, when: "level >= L2" }
  # L3
  mutation_tool: { tool: mutmut, when: "level == L3" }
  mutation_threshold: 80
  spec_audit_cli: { tool: specdrive, when: "level == L3", via: "npx" }  # language-agnostic CLI; needs Node/npm
```

`.ffflow/stack.yaml` can override any dimension.

## Per-level expectations

| Level | Tools active | Notes |
|---|---|---|
| L0 | uv, ruff, mypy, pytest, coverage.py | Prose specs in `docs/specs/`. Threshold 95% optional. |
| L1 | + hexagonal layout | Same tools; layout matters. |
| L2 | + pytest-bdd + Hypothesis + pytest-bdd-property | `.feature` files in `specs/`. |
| L3 | + mutmut + specdrive (via npx) | RID traceability + mutation testing. Requires Node/npm for specdrive. |

## Directory structure

L0/L1 (prose):
```
src/
tests/
docs/specs/
```

L2+ (Gherkin):
```
src/
  domain/
  application/
  infrastructure/
specs/                # .feature files
  acceptance/
  application/
  domain/
tests/
  unit/
  integration/
```

`stack-init` chooses based on level.

## Justfile recipes

The L0 baseline (`justfile`):

```just
set shell := ["bash", "-uc"]

default:
    @just --list

dev-install:
    uv venv --allow-existing .venv
    uv pip install -e ".[dev]"

# Private guard: detect an empty workspace (no Python files yet).
# Used by format/lint/typecheck/test/coverage to early-exit cleanly so the
# initial scaffolding commit can pass pre-commit hooks.
#
# Source paths come from uv workspace introspection — works for single-package
# (src/) and multi-package (any [tool.uv.workspace] members) without the
# cartridge knowing the project's directory shape. Falls back to "src" + "."
# for non-workspace projects.
_member_paths:
    @python3 -c "import sys; \
        try: import tomllib \
        except ImportError: import tomli as tomllib; \
        d=tomllib.load(open('pyproject.toml','rb')); \
        ws=d.get('tool',{}).get('uv',{}).get('workspace',{}); \
        members=ws.get('members',['src']) if ws else ['src']; \
        print('\n'.join(members))" 2>/dev/null || echo "src"

_empty:
    @test -z "$(just _member_paths | xargs -I{} find {} -name '*.py' 2>/dev/null | head -1)" && echo yes || echo no

_no_tests:
    @test -z "$(just _member_paths | xargs -I{} find {} \( -name 'test_*.py' -o -name '*_test.py' \) 2>/dev/null | head -1)" && echo yes || echo no

format:
    @if [ "$(just _empty)" = "yes" ]; then echo "format: no source files yet"; else uv run ruff format .; fi

lint:
    @if [ "$(just _empty)" = "yes" ]; then echo "lint: no source files yet"; else uv run ruff check --fix .; fi

typecheck:
    @if [ "$(just _empty)" = "yes" ]; then echo "typecheck: no source files yet"; else uv run mypy src; fi

test:
    @if [ "$(just _no_tests)" = "yes" ]; then echo "test: no tests yet"; else uv run pytest tests -v --durations=10; fi

coverage:
    @if [ "$(just _no_tests)" = "yes" ]; then echo "coverage: no tests yet"; else uv run pytest tests --cov=src --cov-fail-under=95 --cov-report=term-missing; fi

check-all: format lint typecheck coverage
    @echo "All checks passed"

clean:
    rm -rf .venv __pycache__ .pytest_cache .mypy_cache .coverage htmlcov dist build *.egg-info
    find . -type f -name "*.pyc" -delete
```

L2 additions (added by `stack-init` when level≥L2):

```just
spec-test:
    uv run pytest specs/ -v --durations=10

spec-coverage:
    uv run pytest specs/ --cov=src --cov-fail-under=80 --cov-report=term-missing
```

L3 additions:

```just
mutate:
    uv run mutmut run --paths-to-mutate=src/

# specdrive is a language-agnostic CLI distributed on npm; it audits the
# Gherkin specs + JUnit XML, not Python source, so it runs via npx rather
# than uv. Pin the version in package.json (or use `npx specdrive@<ver>`)
# for reproducibility.
spec-audit:
    npx specdrive audit
```

And `check-all` extends to include the active gates.

## pyproject.toml templates

Templates live in `templates/`. `stack-init` merges them per level:

| File | Template | When |
|---|---|---|
| `pyproject.toml` | `templates/pyproject.toml.L0` | L0/L1 baseline |
| `pyproject.toml` (merge) | `templates/pyproject.toml.L2-additions.toml` | L2+ adds pytest-bdd, hypothesis |
| `pyproject.toml` (merge) | `templates/pyproject.toml.L3-additions.toml` | L3 adds mutmut (specdrive comes via npx, not pyproject) |

## Dual coverage (L2+)

Unit tests enforce 95% line coverage. Spec tests enforce 80% line coverage. Both must pass.

Unit coverage measures code correctness. Spec coverage measures behavioral contract fulfillment. The gap between them reveals untested business rules.

## Notes

- pytest-bdd maps Gherkin steps to Python functions. Standard pytest execution.
- pytest-bdd-property handles `@property-based` tagged scenarios via Hypothesis.
- mutmut validates test strength. Cadence rule lives in `justfile` (mutate not in check-all; schedule it).
- specdrive audit checks RID traceability. It's a language-agnostic CLI run via `npx specdrive` — it reads the `.feature` specs and JUnit XML, so it works identically on Python and TypeScript projects. Run in CI when L3 (the CI job needs a Node setup step alongside the Python one).
- `--durations=10` monitors test performance. Keep unit tests under 5s total.

## Anti-patterns

- Skipping `mypy` because it slows things down. The bugs it catches are exactly the ones that survive into prod.
- Lowering coverage thresholds rather than writing tests. The threshold is a floor.
- Running mutation testing on every PR. (See `justfile` for the cadence rule.)
- Mixing `pytest-bdd` and unit-test config such that both run via `pytest` without separation. Keep `tests/` and `specs/` distinct.
