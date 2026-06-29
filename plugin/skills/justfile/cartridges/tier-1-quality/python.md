# Tier 1 quality — Python recipes

Implements the [Tier 1 quality](../tier-1-quality.md) recipe contract for the Python stack. See that file for the recipe list, rules, and anti-patterns.

```just
test-watch:
    uv run pytest-watch tests/ -- -v

integration-test:
    uv run pytest tests/integration -v

complexity:
    uv run radon cc src --total-average

loc:
    @find src -name "*.py" -exec wc -l {} + | sort -rn | head -20

duplicates:
    uv run pylint --disable=all --enable=R0801 src

slowtests:
    uv run pytest --durations=0 -v | head -50
```
