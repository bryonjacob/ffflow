# Tier 2 security — TypeScript recipes

Implements the [Tier 2 security](../tier-2-security.md) recipe contract for the TypeScript stack. See that file for the recipe list, rules, CI integration, and anti-patterns.

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
