# Tier 3 production — Python hints

Implements the [Tier 3 production](../tier-3-advanced.md) recipe contract for the Python stack. These are starting hints — Tier 3 recipes are highly project-specific. See the concept file for rules, safety guards, and per-environment configuration.

```just
test-smart:
    uv run pytest --testmon  # incremental test runner

migrate:
    uv run alembic upgrade head      # or django migrate, etc.

deploy ENV:
    uv build
    docker build -t myapp:$(git rev-parse HEAD) .
    docker push myapp:$(git rev-parse HEAD)
    kubectl --context={{ENV}} rollout restart deployment/myapp
```
