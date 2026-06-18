# Stack cartridge: Rust

## Purpose

Declare the canonical Rust toolchain for FFFlow projects and provide level-aware defaults. Loaded by `init-ffflow` and `stack-init` for tool detection and config generation.

## Maximum level: L3

**Rust projects can adopt FFFlow at any level, L0 through L3.** FFFlow's L3 RID-traceability gate is implemented by [`specdrive`](https://github.com/bryonjacob/specdrive), a language-agnostic CLI. It operates on Gherkin `.feature` files and JUnit XML test output — both universal formats — so it audits a Rust project exactly as it audits a TypeScript one. specdrive is distributed via npm, but that is its *install channel*, not a constraint on what it can audit: you run it via `npx specdrive` (no crates.io publication is needed — specdrive never touches Cargo). Mutation testing via `cargo-mutants` rounds out the L3 gates.

The only prerequisite for L3 on Rust is that Node.js/npm is available to run specdrive. `stack-init` checks for `npx` at L3 and tells you to install Node if it's missing.

## Dimensions

The stack's declared shape. Other skills (and `.ffflow/stack.yaml` overrides) read this.

```yaml
stack: rust
applies_to: rust
max_level: L3
dimensions:
  package_manager: { tool: cargo, version: ">=1.75" }
  formatter: { tool: rustfmt, command: "cargo fmt" }
  linter: { tool: clippy, command: "cargo clippy" }
  type_checker: { tool: rustc, mode: strict }     # built into cargo check
  test_runner: { tool: cargo-nextest }            # falls back to `cargo test` if not installed
  coverage_tool: { tool: cargo-llvm-cov }
  coverage_threshold_line: 95                     # L0–L2 default
  coverage_threshold_branch: 90
  complexity_limit: 25                            # clippy cognitive_complexity default; tunable
  # L2+
  bdd_runner: { tool: cucumber-rs, when: "level >= L2" }
  property_runner: { tool: proptest, when: "level >= L2" }
  bdd_property: { tool: cucumber-rs+proptest, when: "level >= L2" }
  # L3
  mutation_tool: { tool: cargo-mutants, when: "level == L3" }
  mutation_threshold: 80
  spec_audit_cli: { tool: specdrive, when: "level == L3", via: "npx" }  # language-agnostic CLI; needs Node/npm
```

`.ffflow/stack.yaml` can override any dimension.

## Per-level expectations

| Level | Tools active | Notes |
|---|---|---|
| L0 | cargo, rustfmt, clippy, cargo-nextest, cargo-llvm-cov | Prose specs in `docs/specs/`. Threshold 95% optional. |
| L1 | + hexagonal layout (crate-per-bounded-context recommended) | Same tools; layout matters. |
| L2 | + cucumber-rs + proptest | `.feature` files in `specs/`. |
| L3 | + cargo-mutants + specdrive (via npx) | RID traceability + mutation testing. Requires Node/npm for specdrive. |

## Workspace vs single crate

Rust supports both single-crate and workspace projects. FFFlow assumes a **workspace** is the default for non-trivial work:

```toml
# Cargo.toml at project root
[workspace]
members = ["crates/*"]
resolver = "2"
```

`stack-init` writes a workspace `Cargo.toml` unless a single-crate flag is passed (`--single-crate`). Inside a polyglot subproject (e.g., `backend-rust/`), the workspace is rooted at the subproject directory.

## Directory structure

L0/L1 (prose):
```
Cargo.toml                 # workspace root
crates/
  my-crate/
    Cargo.toml
    src/
      lib.rs
    tests/                 # integration tests (Rust convention)
docs/specs/
```

L2+ (Gherkin):
```
Cargo.toml
crates/
  my-domain/
    Cargo.toml
    src/
      domain/              # pure logic
      application/         # orchestration
      infrastructure/      # adapters
    tests/
      integration/
  my-application/
  my-infrastructure/
specs/                     # .feature files (cucumber-rs)
  acceptance/
  application/
  domain/
tests/                     # cross-crate integration; cucumber-rs glue lives here
```

Rust convention: **unit tests live alongside source** (`#[cfg(test)] mod tests` inside each `.rs` file). FFFlow respects this — the `tests/` directory at the crate root holds integration tests (cross-module / cross-crate), and at the workspace root holds the Gherkin step glue.

`stack-init` chooses based on level.

## Justfile recipes

The L0 baseline (`justfile`):

```just
set shell := ["bash", "-uc"]

default:
    @just --list

dev-install:
    rustup show active-toolchain || rustup toolchain install stable
    rustup component add rustfmt clippy llvm-tools-preview
    cargo install --locked cargo-nextest cargo-llvm-cov || true

# Private guard: detect an empty workspace (no member crates yet).
# Used by format/lint/typecheck/test/coverage to early-exit cleanly so the
# initial scaffolding commit can pass pre-commit hooks.
_empty:
    @test -z "$(cargo metadata --no-deps --format-version 1 2>/dev/null | python3 -c 'import sys,json; print(",".join(p["name"] for p in json.load(sys.stdin)["packages"]))' 2>/dev/null)" && echo yes || echo no

format:
    @if [ "$(just _empty)" = "yes" ]; then echo "format: workspace empty, nothing to format"; else cargo fmt --all; fi

lint:
    @if [ "$(just _empty)" = "yes" ]; then echo "lint: workspace empty, nothing to lint"; else cargo clippy --all-targets --all-features --workspace -- -D warnings; fi

typecheck:
    @if [ "$(just _empty)" = "yes" ]; then echo "typecheck: workspace empty, nothing to check"; else cargo check --all-targets --all-features --workspace; fi

test:
    @if [ "$(just _empty)" = "yes" ]; then echo "test: workspace empty, nothing to test"; else cargo nextest run --workspace --no-fail-fast || cargo test --workspace --no-fail-fast; fi

coverage:
    @if [ "$(just _empty)" = "yes" ]; then echo "coverage: workspace empty, nothing to measure"; else cargo llvm-cov --workspace --fail-under-lines 95 --lcov --output-path lcov.info; fi

check-all: format lint typecheck coverage
    @echo "All checks passed"

clean:
    cargo clean
    rm -f lcov.info
    rm -rf target/llvm-cov-target
```

The `_empty` guard solves a real chicken-and-egg: `stack-init` installs git hooks calling these recipes, but the very first commit (which captures the scaffolding itself) has no member crates yet. Without guards, every gate fails and the user is forced to `--no-verify` their first commit. With guards, `just check-all` exits 0 on an empty workspace; once Phase 1 adds the first crate, the guards become no-ops automatically.

L2 additions (added by `stack-init` when level≥L2):

```just
spec-test:
    cargo test --workspace --test '*' -- --include-ignored

spec-coverage:
    cargo llvm-cov --workspace --tests --fail-under-lines 80 \
        --include-ffi --lcov --output-path lcov-spec.info
```

L3 additions:

```just
mutate:
    cargo mutants --workspace --no-shuffle --timeout-multiplier 2.0

# specdrive is a language-agnostic CLI distributed on npm; it audits the
# Gherkin specs + JUnit XML, not Cargo, so it runs via npx.
spec-audit:
    npx specdrive audit
```

And `check-all` extends to include the active gates (no `mutate` in `check-all` — slow gates kill the loop; cadence rule per the `justfile` skill).

## Cargo.toml templates

Templates live in `templates/`. `stack-init` merges them per level:

| File | Template | When |
|---|---|---|
| `Cargo.toml` (workspace root) | `templates/Cargo.toml.workspace.L0` | L0/L1 baseline |
| `crates/<name>/Cargo.toml` | `templates/Cargo.toml.crate.L0` | per-crate baseline |
| `Cargo.toml` (merge dev-deps) | `templates/Cargo.toml.L2-additions.toml` | L2+ adds proptest, cucumber |
| `Cargo.toml` (merge dev-deps) | `templates/Cargo.toml.L3-additions.toml` | L3 adds cargo-mutants config |
| `rustfmt.toml` | `templates/rustfmt.toml` | All levels |
| `clippy.toml` | `templates/clippy.toml` | All levels |
| `.config/nextest.toml` | `templates/nextest.toml` | All levels |
| `deny.toml` | `templates/deny.toml.L2` | L2+ (license + vuln deny rules) |

## Dual coverage (L2+)

Unit tests (`#[cfg(test)] mod tests` inside `src/`) enforce 95% line coverage.
Spec tests (`tests/` directory at crate root and Cucumber `.feature` files at workspace root) enforce 80% line coverage.
Both must pass.

Unit coverage measures code correctness. Spec coverage measures behavioral contract fulfillment. The gap between them reveals untested business rules.

`cargo-llvm-cov` supports `--ignore-filename-regex` to split the two; configure in `Cargo.toml` `[package.metadata.coverage]` or via justfile arguments.

## Notes

- **cargo-nextest** is preferred over `cargo test` for speed and ergonomics; the justfile falls back to `cargo test` if `cargo nextest` isn't installed, so projects work without it.
- **clippy** is treated as both linter and complexity gate; `-D warnings` makes lint findings fatal in CI. Cognitive-complexity threshold lives in `clippy.toml`.
- **cargo-llvm-cov** wraps `llvm-cov` via the `llvm-tools-preview` component; it's faster and more accurate than `tarpaulin` and works with `cargo-nextest`.
- **cucumber-rs** is the canonical Rust BDD runner. It plugs into Cargo's test harness via a `tests/cucumber.rs` shim — keep step definitions in a separate `tests/steps/` module so domain glue stays separate from infrastructure glue.
- **proptest** is the canonical property-based testing crate (over `quickcheck` — proptest's shrinking is materially better). At L2+, `@property-based` Gherkin scenarios route to proptest via cucumber-rs's regex-step + proptest's `Strategy` integration.
- **cargo-mutants** validates test strength. Cadence rule lives in `justfile` (mutate not in check-all; schedule it).
- **specdrive audit** checks RID traceability. It's a language-agnostic CLI run via `npx specdrive` — it reads the `.feature` specs and JUnit XML, so it works identically on Rust and TypeScript projects. Run in CI when L3 (the CI job needs a Node setup step alongside the Rust one).
- Edition: pin to `edition = "2021"` (or "2024" when stable). Don't auto-upgrade — that's a deliberate project decision.
- MSRV (Minimum Supported Rust Version): declare `rust-version = "1.75"` in workspace `Cargo.toml`. Audit checks freshness.

## Workspace dependency resolver

Always set `resolver = "2"` at the workspace root. Resolver 1 has subtle bugs with feature unification that surface as "works locally, fails in CI."

## Feature flags

Two kinds:
- **Cargo features** (`[features]` in Cargo.toml) — compile-time, public API. Use sparingly; each combination is a build matrix.
- **Runtime flags** — use `tracing` + env vars or a config crate.

Don't conflate them.

## Anti-patterns

- Using `cargo test` for both unit and integration tests without separation. Keep `#[cfg(test)] mod tests` for unit and `tests/` directory for integration; the spec-test recipe filters integration.
- Skipping `cargo clippy` because "it complains too much." The complaints are usually right. Allow specific lints in `clippy.toml` if a rule genuinely doesn't fit.
- Lowering coverage thresholds rather than writing tests. The threshold is a floor.
- Running mutation testing on every PR. (See `justfile` for the cadence rule — `cargo mutants` on a workspace can take >30 min.)
- Mixing unit and integration test entry points. Vitest-style mixing doesn't work in Rust's test harness; spec-coverage needs its own pass.
- Forgetting `resolver = "2"`. Quiet, painful, hard-to-debug.
- Using `unsafe` in domain code. FFFlow's hexagonal layering means unsafe belongs only in infrastructure adapters (FFI, performance-critical hot paths), never in domain.
- Pinning to nightly. Pick `rust-version` in Cargo.toml and stay on stable. Nightly-only features are not L1+ compliant.

## Polyglot notes

When this stack is one subproject of a polyglot workspace (e.g., `crates/` under a larger monorepo):

- The Rust subproject is itself a Cargo workspace rooted at its subproject directory.
- The root `justfile` (polyglot orchestrator) delegates: `cd crates && just check-all` invokes the Rust subproject's justfile.
- Cross-language contracts (e.g., emitting IR for Python/TS to consume) use the polyglot cartridge's `contracts:` recipe pattern.
- Each language has its own coverage report; aggregation is per-subproject (per the polyglot cartridge).
