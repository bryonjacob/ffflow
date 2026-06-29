# Tier 1 quality — Rust recipes

Implements the [Tier 1 quality](../tier-1-quality.md) recipe contract for the Rust stack. See that file for the recipe list, rules, and anti-patterns.

```just
test-watch:
    cargo watch -x 'nextest run --workspace'

integration-test:
    cargo nextest run --workspace --test '*'

# clippy is the complexity gate (see stack/cartridges/rust.md). The blocking check
# lives in `lint` with -D warnings; here the complexity lints are dialed to warn for a report.
complexity:
    cargo clippy --workspace --all-targets -- \
        -W clippy::cognitive_complexity -W clippy::too_many_lines 2>&1 | grep -A3 complexity

# Largest files by real code lines (cloc separates code/comment/blank); find|wc fallback.
loc:
    @cloc --by-file --quiet crates/ 2>/dev/null | sort -k5 -rn | head -20 \
        || find crates -name "*.rs" -exec wc -l {} + | sort -rn | head -20

# No first-class Rust duplication tool (no CPD/jscpd equivalent). Honest stub.
duplicates:
    @echo "No first-class Rust duplication tool. clippy flags many copy-paste"
    @echo "smells; feed loc/complexity to /audit --type refactor for triage."

slowtests:
    cargo nextest run --workspace --no-fail-fast 2>&1 | grep -E "SLOW|\[.*s\]" | sort -rn | head -50
```

Notes: `test-watch` needs `cargo-watch` (or swap in `bacon`); `loc` prefers `cloc` and falls back to `find|wc` zero-install. `complexity` and `slowtests` reuse the already-declared clippy and cargo-nextest — no new dependency. `duplicates` is intentionally a stub: Rust lacks a mature CPD/jscpd equivalent, and a misleading dup report violates the "signal, not verdict" rule in the concept file.
