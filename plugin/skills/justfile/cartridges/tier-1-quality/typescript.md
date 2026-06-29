# Tier 1 quality — TypeScript recipes

Implements the [Tier 1 quality](../tier-1-quality.md) recipe contract for the TypeScript stack. See that file for the recipe list, rules, and anti-patterns.

```just
test-watch:
    pnpm vitest tests

integration-test:
    pnpm vitest run tests/integration

complexity:
    pnpm eslint src --rule 'complexity: [warn, 10]' --no-eslintrc

loc:
    @find src -name "*.ts" -exec wc -l {} + | sort -rn | head -20

duplicates:
    pnpm dlx jscpd src/

slowtests:
    pnpm vitest run --reporter=verbose tests | grep -E "duration" | sort -rn | head -50
```
