# Tier 2 security — Rust recipes

Implements the [Tier 2 security](../tier-2-security.md) recipe contract for the Rust stack. See that file for the recipe list, rules, CI integration, and anti-patterns.

`cargo-deny` covers vulnerabilities, licenses, and dependency policy in one tool. Config lives in `deny.toml` at the workspace root (the `stack` skill's `rust.md` cartridge supplies the template).

```just
vulns:
    cargo deny check advisories

lic:
    cargo deny check licenses

sbom:
    cargo cyclonedx --format json --output-pattern bom

doctor:
    @rustc --version
    @cargo --version
    @cargo nextest --version 2>/dev/null || echo "(cargo-nextest not installed)"
    @cargo llvm-cov --version 2>/dev/null || echo "(cargo-llvm-cov not installed)"
    @just --version
    @echo "Environment OK"
```

Install: `cargo install --locked cargo-deny cargo-cyclonedx`.
