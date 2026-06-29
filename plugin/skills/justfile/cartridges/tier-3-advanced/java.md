# Tier 3 production — Java hints

Implements the [Tier 3 production](../tier-3-advanced.md) recipe contract for the Java stack. These are starting hints — Tier 3 recipes are highly project-specific. See the concept file for rules, safety guards, and per-environment configuration.

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
