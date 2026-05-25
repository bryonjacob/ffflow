---
name: git-hooks
description: Pre-commit and pre-push hooks that call justfile recipes. Level-aware: pre-commit is fast; pre-push runs the level's gates.
---

# git-hooks

## Purpose

Catch problems before code leaves the developer's machine. Pre-commit is fast (format/lint/typecheck); pre-push is thorough (tests + level-appropriate audits).

Hooks delegate to justfile recipes — they don't reimplement gates.

Loaded by `stack-init` when scaffolding a project. Standalone to add hooks to an existing project.

## Pre-commit hook

Fast (a few seconds). Run on every commit.

```bash
#!/bin/bash
set -e
echo "Running pre-commit checks..."
just format
just lint
just typecheck
echo "Pre-commit checks passed"
```

Recipes used: `format`, `lint`, `typecheck`. These are baseline at every level.

## Pre-push hook

Thorough. Run on every push (slower, but still local).

```bash
#!/bin/bash
set -e
echo "Running pre-push checks..."
just check-all
echo "Pre-push checks passed"
```

`check-all` is level-aware (see `justfile`). At L2+ it includes `spec-coverage`; at L3 it includes `spec-audit`. Hooks don't have to know — they just call `check-all`.

If `check-all` is too slow for pre-push (large project), document an opt-out: `git push --no-verify` is the user's escape hatch. Don't make hooks so slow that everyone bypasses them.

## Installation

### Direct (simple)

```bash
mkdir -p .git/hooks
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/bash
set -e
just format
just lint
just typecheck
EOF
chmod +x .git/hooks/pre-commit

cat > .git/hooks/pre-push <<'EOF'
#!/bin/bash
set -e
just check-all
EOF
chmod +x .git/hooks/pre-push
```

### Via pre-commit framework (recommended for teams)

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: ffflow-format
        name: just format
        entry: just format
        language: system
        pass_filenames: false
        stages: [pre-commit]
      - id: ffflow-lint
        name: just lint
        entry: just lint
        language: system
        pass_filenames: false
        stages: [pre-commit]
      - id: ffflow-typecheck
        name: just typecheck
        entry: just typecheck
        language: system
        pass_filenames: false
        stages: [pre-commit]
      - id: ffflow-check-all
        name: just check-all
        entry: just check-all
        language: system
        pass_filenames: false
        stages: [pre-push]
```

Install: `pre-commit install --hook-type pre-commit --hook-type pre-push`.

The framework path is the recommended one for teams — it survives clones and stays in the repo.

## Justfile recipes

Add to the project's justfile:

```just
# Install git hooks
hooks-install:
    @if command -v pre-commit >/dev/null; then \
        pre-commit install --hook-type pre-commit --hook-type pre-push; \
    else \
        cp .githooks/pre-commit .git/hooks/pre-commit; \
        cp .githooks/pre-push .git/hooks/pre-push; \
        chmod +x .git/hooks/*; \
    fi
    @echo "Hooks installed"

# Remove git hooks
hooks-remove:
    @if command -v pre-commit >/dev/null; then \
        pre-commit uninstall --hook-type pre-commit --hook-type pre-push; \
    else \
        rm -f .git/hooks/pre-commit .git/hooks/pre-push; \
    fi
    @echo "Hooks removed"
```

## Best practices

- **Fast pre-commit.** Format / lint / typecheck only. Tests are pre-push.
- **Thorough pre-push.** `check-all` mirrors what CI runs.
- **Match CI.** Hooks should fail for the same reasons CI does. Surprises in CI = hooks aren't tight enough.
- **Fail fast.** `set -e` exits on first error.

## When to skip

`git commit --no-verify` and `git push --no-verify` bypass hooks. The user owns the choice. Reasons that justify the bypass:

- WIP commit on a feature branch (not main).
- Pre-existing failure unrelated to current change (and an issue is filed to fix it).

Reasons that don't:
- "It's a small change." Hooks catch small-change bugs.
- "The CI will catch it." CI rejects after the user already context-switched.

## Anti-patterns

- Hooks that bypass the justfile (running tools directly). Drift between hook and `check-all`.
- Hooks so slow nobody uses them. Either speed them up or move work to pre-push.
- Installing hooks without committing the config (so other devs don't get them). Use the pre-commit framework.

## Friction addressed

- Format/lint problems shipping to CI when they could've been caught locally.
- "Works on my machine but fails in CI" → hooks force the same checks locally.
- Onboarding new developers without hooks installed.
