# Justfile cartridge: Tier 3 — production patterns

## Purpose

Add Tier 3 justfile recipes — production deployment, database migrations, observability. Adopted by projects with deployed services and databases.

These are highly project-specific. The skill provides shape and conventions; each project fills in the details.

## Recipes

```just
# Run tests for files that changed since main (git-aware)
test-smart:
    <changed-file detection + targeted test runner>

# Deploy to an environment (env required as arg)
deploy ENV:
    <push image, run migrations, swap traffic>

# Run database migrations forward
migrate:
    <stack-specific migration tool>

# Stream service logs (env arg, defaults to local)
logs ENV='local':
    <kubectl logs / docker logs / cloud-provider tool>

# Service status / health (env arg, defaults to local)
status ENV='local':
    <kubectl get / docker ps / cloud-provider tool>
```

## Per-stack hints

### Python

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

### TypeScript

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

### Java

```just
test-smart:
    mvn -q test -Dtest=$(git diff --name-only origin/main | grep Test.java | xargs -n1 basename)

migrate:
    mvn -q liquibase:update

deploy ENV:
    mvn -q package
    docker build -t myapp:$(git rev-parse HEAD) .
    docker push myapp:$(git rev-parse HEAD)
    kubectl --context={{ENV}} rollout restart deployment/myapp
```

## Rules

- **`deploy` always takes an explicit env arg.** Never default to prod.
- **`migrate` is one-way forward.** Rollback is a separate `migrate-rollback` recipe; `migrate` itself only moves forward.
- **`test-smart` is for the dev loop**, not CI. CI always runs full `test`.
- **`logs` and `status` accept env args.** Default to local for safety.

## Safety guards

For destructive operations:

```just
deploy ENV:
    @if [ "{{ENV}}" = "production" ]; then \
        read -p "Type the production deployment confirmation: " confirm; \
        [ "$$confirm" = "deploy to production" ] || (echo "Aborted." && exit 1); \
    fi
    <do the deploy>
```

Confirmation prompts on `production`. Other envs go through.

## Per-environment configuration

`.ffflow/env/<env>.yaml`:

```yaml
context: gke-prod-us-east1
namespace: myapp
image_repo: gcr.io/myorg/myapp
domain: myapp.example.com
```

Recipes read this file when `ENV` is set.

## Anti-patterns

- `deploy` recipes that hardcode the env. Always parameterize.
- Recipes that pipe sensitive output to logs. Redact before logging.
- `migrate` recipes that run on every deploy without idempotency. Migrations must be idempotent.
- Using `kubectl exec` from recipes for "quick fixes." That's an ops decision, not a build recipe.

## Friction addressed

- Hand-typed deploy commands that drift across environments.
- "Which env was that staged on?" — recipe + env arg makes it discoverable.
- Migrations forgotten in PRs that change schemas.
