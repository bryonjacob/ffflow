# Justfile cartridge: Tier 2 — security # justfile-security compliance

## Purpose

Add Tier 2 justfile recipes — security scanning and compliance. Adopted when a project is deploying to production, handling sensitive data, or under regulatory requirements.

## Recipes

```just
# Vulnerability scanning (CRITICAL severity, fixable only)
vulns:
    <stack-specific scanner>

# License compliance check (fail on GPL/LGPL/AGPL in prod deps unless allowlisted)
lic:
    <stack-specific tool>

# Generate Software Bill of Materials (CycloneDX format)
sbom:
    <stack-specific tool>

# Environment health check (tools, versions, configuration)
doctor:
    <validate dev environment>
```

## Per-stack implementations

### Python

```just
vulns:
    uv run pip-audit --severity-threshold critical --fix

lic:
    uv run pip-licenses --format=markdown --fail-on='GPL;LGPL;AGPL'

sbom:
    uv run cyclonedx-py -o sbom.json

doctor:
    @python --version
    @uv --version
    @just --version
    @command -v ruff && ruff --version
    @command -v mypy && mypy --version
    @echo "Environment OK"
```

### TypeScript

```just
vulns:
    pnpm audit --audit-level critical --fix

lic:
    pnpm dlx license-checker --failOn 'GPL-3.0;LGPL-3.0;AGPL-3.0'

sbom:
    pnpm dlx @cyclonedx/cyclonedx-npm --output-file sbom.json

doctor:
    @node --version
    @pnpm --version
    @just --version
    @command -v tsc && tsc --version
    @echo "Environment OK"
```

### Java

```just
vulns:
    mvn -q org.owasp:dependency-check-maven:check -DfailBuildOnCVSS=9

lic:
    mvn -q license:check

sbom:
    mvn -q org.cyclonedx:cyclonedx-maven-plugin:makeAggregateBom

doctor:
    @java -version
    @mvn --version
    @just --version
    @echo "Environment OK"
```

### Rust

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

## Rules

- **`vulns` runs on every PR in CI** (gates the merge).
- **`lic` runs on every PR in CI** (gates the merge for prod-dep changes).
- **`sbom` runs in CI on release builds** (artifact).
- **`doctor` is local-only** (helps new developers).
- **None of these go in `check-all` by default** — they're CI gates, not dev-loop fast checks.

## CI integration

`ci-gates` workflow includes (at justfile maturity ≥ 2):

```yaml
  gate-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: <stack install>
      - name: Vulnerabilities
        run: just vulns
      - name: Licenses
        run: just lic
```

This is a separate gate from the four-gate spec model — security/compliance is its own track. Failures block.

## Allowlists

For licenses, an allowlist file declares acceptable variants:

```
# license-allowlist.txt
GPL-2.0 with classpath exception
LGPL with linking exception
```

Match the stack's tool format. Audit the file as part of `/audit --type architecture` if it changes.

## Anti-patterns

- Suppressing vulnerability findings without an issue tracking the suppression. Each suppression has an expiry date.
- Permitting all licenses ("we'll deal with it later"). Pick the policy and enforce it.
- Running `sbom` on every commit. It's slow and the artifact is only needed at release.
- Skipping `doctor` for new developers. Ten minutes of "doctor failed → fix" saves an hour of "tests fail mysteriously."

## Friction addressed

- Vulnerabilities discovered at audit time, not at introduction.
- License surprises in legal review.
- Dev environment drift causing "works on my machine" issues.
