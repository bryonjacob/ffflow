# Tier 2 security — Python recipes

Implements the [Tier 2 security](../tier-2-security.md) recipe contract for the Python stack. See that file for the recipe list, rules, CI integration, and anti-patterns.

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
