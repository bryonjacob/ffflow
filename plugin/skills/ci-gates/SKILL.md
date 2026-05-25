---
name: ci-gates
description: GitHub Actions workflow templates for FFFlow projects — runs level-appropriate audits and quality gates as PR checks.
---

# ci-gates

## Purpose

Provide CI workflow templates that run FFFlow's keep-honest checks as PR gates. The workflow is level-aware: more checks engage at higher levels.

At every level, the workflow invokes `/audit --ci` to run the active auditors and produce machine-readable output GitHub Actions can act on.

## When to invoke

- `stack-init` invokes this when scaffolding CI.
- Standalone to refresh or upgrade an existing workflow.

## Inputs

- `.ffflow/config.yaml` — level, stack.
- Optional `--workflow-file <path>` to override default `.github/workflows/ffflow-ci.yml`.

## Outputs

- `.github/workflows/ffflow-ci.yml` written or updated.
- Optional: branch protection guidance for the user to apply manually (this skill doesn't `gh repo edit` settings).

## Gate model

Four gates, but only the ones active at the project's level run.

| Gate | What it checks | Active at level |
|---|---|---|
| 1. Structure | lint, format, typecheck, spec-code traceability | L0+ |
| 2. Correctness | unit tests, spec tests (if L2+) | L0+ |
| 3. Coverage | unit coverage threshold, spec coverage at L2+ | L0+ |
| 4. Maintainability | complexity budgets, mutation tests (L3) | L1+ |

`/audit` decides which auditors run per level; CI just orchestrates the gates.

## Template (TypeScript stack, L1)

`.github/workflows/ffflow-ci.yml`:

```yaml
name: FFFlow CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  gate-1-structure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - name: Format check
        run: pnpm prettier --check .
      - name: Lint
        run: pnpm eslint . --max-warnings 0
      - name: Typecheck
        run: pnpm tsc --noEmit

  gate-2-correctness:
    needs: gate-1-structure
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - name: Unit tests
        run: pnpm vitest run tests --reporter=junit --outputFile=unit-results.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: test-results, path: '*-results.xml' }

  gate-3-coverage:
    needs: gate-2-correctness
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - name: Unit coverage
        run: pnpm vitest run tests --coverage --coverage.lines=95
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: coverage, path: coverage/ }

  gate-4-maintainability:
    needs: gate-3-coverage
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - name: FFFlow audits
        run: pnpm dlx claude-code --ci /audit --ci > audit-report.json
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: audit-report, path: audit-report.json }
```

## Template additions (L2)

Add spec tests + spec coverage to gates 2 and 3:

```yaml
      - name: Spec tests
        run: pnpm vitest run specs --reporter=junit --outputFile=spec-results.xml

      - name: Spec coverage
        run: pnpm vitest run specs --coverage --coverage.lines=80
```

## Template additions (L3)

Add mutation testing to gate 4 on a schedule (see `justfile` for the cadence rule — mutate is not in check-all; runs weekly here):

```yaml
  mutation-weekly:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install --frozen-lockfile
      - name: Stryker
        run: pnpm stryker run
      - name: specdrive audit (RID)
        run: pnpm specdrive audit
```

And in the workflow trigger:
```yaml
on:
  schedule:
    - cron: '0 6 * * 1'   # Mondays 06:00 UTC
```

## Python variant

Same structure; replace steps:

| Gate | TypeScript | Python |
|---|---|---|
| 1 | `pnpm prettier --check` + `pnpm eslint` + `pnpm tsc --noEmit` | `uv run ruff format --check` + `uv run ruff check` + `uv run mypy src` |
| 2 | `pnpm vitest run tests` | `uv run pytest tests` |
| 3 | `pnpm vitest --coverage` | `uv run pytest --cov` |
| 4 (L3 weekly) | `pnpm stryker run` | `uv run mutmut run` |

## Branch protection

Require all gate jobs to pass on `main`. Tell the user to apply via GitHub UI or:
```bash
gh api -X PUT repos/<org>/<repo>/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["gate-1-structure","gate-2-correctness","gate-3-coverage","gate-4-maintainability"]}'
```

Don't run this automatically. Branch protection is a permissions-sensitive change.

## Idempotency

- Re-running detects existing `ffflow-ci.yml`. Offers diff against the level-appropriate template; user confirms.
- Custom workflows the user added stay untouched.

## Notes

- Thresholds in the workflow come from the stack skill's dimension YAML, not hardcoded here.
- The `audit --ci` invocation lets new auditors join the gate without editing the workflow each time.
- Mutation gates run on a schedule, not every PR. Expensive checks should be amortized.

## Anti-patterns

- Hardcoding L3 tools into every level's workflow. Use level branches.
- Running every check every PR. Mutation testing belongs on a weekly cron.
- Failing PRs on `low` severity audit findings. Default the gate to `medium` or higher.
- Touching branch protection without confirmation.
