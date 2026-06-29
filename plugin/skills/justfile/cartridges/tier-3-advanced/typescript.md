# Tier 3 production — TypeScript hints

Implements the [Tier 3 production](../tier-3-advanced.md) recipe contract for the TypeScript stack. These are starting hints — Tier 3 recipes are highly project-specific. See the concept file for rules, safety guards, and per-environment configuration.

```just
test-smart:
    pnpm vitest run --changed origin/main

migrate:
    pnpm prisma migrate deploy

deploy ENV:
    pnpm build
    docker build -t myapp:$(git rev-parse HEAD) .
    docker push myapp:$(git rev-parse HEAD)
    kubectl --context={{ENV}} rollout restart deployment/myapp
```
