---
name: stack
description: FFFlow stack toolchain reference — dimensions (package manager, formatter, linter, test runner, coverage, mutation testing) and level-aware defaults. Cartridges for python, typescript, java, rust, and polyglot.
---

# stack

## Purpose

The "stack" is the language-specific toolchain a project uses. FFFlow declares stack defaults via a dimension model: each tool category (package manager, formatter, linter, etc.) has a canonical choice per language, with level-aware additions (`pytest-bdd` at L2+, `mutmut` at L3, etc.).

This skill is the reference for that model. Other skills (`stack-init`, `stack-assess`, `work-issue`, etc.) consult it. The language-specific specifics live in cartridges under `cartridges/`.

## Cartridges

| `.ffflow/config.yaml stack:` | Cartridge | Templates |
|---|---|---|
| `python` | `cartridges/python.md` | `cartridges/python-templates/` |
| `typescript` | `cartridges/typescript.md` | `cartridges/typescript-templates/` |
| `java` | `cartridges/java.md` | `cartridges/java-templates/` |
| `rust` | `cartridges/rust.md` | `cartridges/rust-templates/` |
| `polyglot` | `cartridges/polyglot.md` | `cartridges/polyglot-templates/` |

Each cartridge declares its dimensions in a YAML block at the top, plus directory conventions, justfile recipe additions per level, and references to its config templates. Load the cartridge whose name matches `.ffflow/config.yaml stack:`.

## The dimension model

Every cartridge declares the same dimensions (with stack-specific values):

```yaml
dimensions:
  package_manager:        { tool: <name>, version: ">=X.Y" }
  formatter:              { tool: <name>, command: "<command>" }
  linter:                 { tool: <name>, command: "<command>" }
  type_checker:           { tool: <name>, mode: strict }
  test_runner:            { tool: <name> }
  coverage_tool:          { tool: <name> }
  coverage_threshold_line: <int>
  coverage_threshold_branch: <int>
  complexity_limit:        <int>
  # L2+
  bdd_runner:             { tool: <name>, when: "level >= L2" }
  property_runner:        { tool: <name>, when: "level >= L2" }
  # L3
  mutation_tool:          { tool: <name>, when: "level == L3" }
  mutation_threshold:     <int>
  spec_audit_cli:         { tool: <name>, when: "level == L3" }
```

`.ffflow/stack.yaml` can override any single dimension. This is how a project keeps the language stack but swaps (say) `vitest` for `jest`.

### Workspace member paths

Cartridges default to language-native workspace introspection for determining where source files live (`cargo metadata` for Rust, `pnpm m ls --json` for TS, `[tool.uv.workspace] members` for Python, `mvn help:evaluate -Dexpression=project.modules` for Java). Used by the empty-workspace guards in each justfile.

For projects with non-standard layouts that the native introspection can't reach, override via `.ffflow/stack.yaml`:

```yaml
source_globs:
  - "subprojects/*/src/**"
  - "vendored/*/lib/**"
```

The justfile's `_member_paths` recipe respects this override when present. Use sparingly — the native path covers the vast majority of cases. If you find yourself reaching for this often, that's a signal the project's layout is fighting the package manager and worth straightening out at that level instead.

## Per-level expectations

| Level | What activates |
|---|---|
| L0 | Package manager + formatter + linter + type checker + test runner + coverage. |
| L1 | Above + project assumed hexagonal-ish (rulebook loaded, not enforced). |
| L2 | + BDD runner + property-based testing. |
| L3 | + mutation testing + RID/spec audit CLI. |

Each cartridge details which tools cover which dimension at each level.

## Single source of truth

When `quality-gates` (or any other skill) needs to know a project's coverage threshold or mutation threshold, it reads the cartridge's `dimensions:` block — not its own restated value. The dimension YAML is the canonical record; it's documentation-for-humans (not machine-parsed), but skills grep it consistently.

## Friction addressed

- "What stack does FFFlow recommend for Python?" — one cartridge, with rationale.
- Stack drift: a project that started with mypy then forgot half its strict flags.
- Cross-stack inconsistency on coverage thresholds and complexity limits.

## Anti-patterns

- Inventing a new dimension. The model is fixed; extending it means amending this skill.
- Loading multiple cartridges. A project has one stack at a time (polyglot orchestrates subprojects, each with its own cartridge).
- Reading a cartridge's templates without reading the cartridge itself. Templates are scaffolding; the cartridge is the reference.
