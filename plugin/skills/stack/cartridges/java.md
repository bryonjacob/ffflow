# Stack cartridge: Java

## Purpose

Declare the canonical Java toolchain for FFFlow projects. Loaded by `init-ffflow` and `stack-init`.

## Maximum level: L2 (until specdrive ships for Java)

**Java projects can adopt FFFlow at L0, L1, or L2 — not L3.** FFFlow's L3 RID-traceability gate is implemented by [`specdrive`](https://github.com/specdrive/specdrive), which currently only ships as an npm package (no Maven Central publication). Mutation testing via PIT works at L3, but the `spec-audit` recipe and the `rid` cartridge of `/fff:audit` cannot engage against Java code.

- **Java-only projects:** `init-ffflow` will refuse `level: L3` for stack `java`. Pick L2.
- **Polyglot projects with a Java subproject:** declare `level_override: L2` on the Java subproject in `.ffflow/config.yaml`.
- **Workaround for "I want L3 anyway":** PIT mutation testing still works; you'll get the structural and coverage gates. The RID traceability gate is what's missing.

If a Java distribution of specdrive lands later, this restriction will be relaxed.

## Dimensions

```yaml
stack: java
applies_to: java
max_level: L2                          # specdrive has no Maven Central publication
dimensions:
  build_tool: { tool: maven, version: ">=3.9" }
  formatter: { tool: spotless, plugin: "com.diffplug.spotless:spotless-maven-plugin" }
  linter: { tool: spotbugs, plugin: "com.github.spotbugs:spotbugs-maven-plugin" }
  test_runner: { tool: junit5 }
  coverage_tool: { tool: jacoco }
  coverage_threshold_line: 95
  coverage_threshold_branch: 90
  complexity_limit: 10
  # L2+
  bdd_runner: { tool: cucumber-jvm, when: "level >= L2" }
  property_runner: { tool: jqwik, when: "level >= L2" }
  # L3 partially supported — mutation works, spec-audit does not
  mutation_tool: { tool: pitest, when: "level == L3" }
  mutation_threshold: 80
  spec_audit_cli: { tool: specdrive, when: "level == L3", supported: false }
```

`.ffflow/stack.yaml` can override any dimension.

## Per-level expectations

| Level | Tools active |
|---|---|
| L0 | Maven, Spotless, SpotBugs, JUnit 5, JaCoCo |
| L1 | + hexagonal layout |
| L2 | + Cucumber JVM + jqwik (property-based). **Max level for Java today.** |
| L3 | (not supported) | specdrive has no Maven Central publication. |

## Directory structure

```
project-root/
├── pom.xml
├── src/
│   ├── main/java/<package>/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   └── test/java/<package>/
└── (L2+) src/test/resources/specs/
              └── <context>/*.feature
```

## pom.xml essentials

L0 baseline lives in `templates/pom.xml.L0`. `stack-init` merges it into the project's `pom.xml`.

L2 adds: `cucumber-java`, `cucumber-junit-platform-engine`, `jqwik`.
L3 adds: `pitest-maven-plugin`, `specdrive` (if a Java distribution exists; otherwise call the CLI from the justfile).

## Justfile recipes

L0:

```just
set shell := ["bash", "-uc"]

default:
    @just --list

dev-install:
    mvn -q -DskipTests install

# Private guard: detect an empty workspace (no Java sources yet).
# Used by gates to early-exit cleanly so the initial scaffolding commit
# can pass pre-commit hooks.
#
# Module paths come from Maven multi-module introspection — `mvn help:evaluate`
# returns the configured <modules>. Falls back to "." for single-module poms,
# which then probes src/main directly.
_member_paths:
    @mvn help:evaluate -Dexpression=project.modules -q -DforceStdout 2>/dev/null | \
        grep -oP '<string>\K[^<]+' || echo "."

_empty:
    @test -z "$(just _member_paths | xargs -I{} find {}/src/main -name '*.java' 2>/dev/null | head -1)" && echo yes || echo no

_no_tests:
    @test -z "$(just _member_paths | xargs -I{} find {}/src/test -name '*.java' 2>/dev/null | head -1)" && echo yes || echo no

format:
    @if [ "$(just _empty)" = "yes" ]; then echo "format: no Java sources yet"; else mvn -q spotless:apply; fi

lint:
    @if [ "$(just _empty)" = "yes" ]; then echo "lint: no Java sources yet"; else mvn -q spotbugs:check; fi

test:
    @if [ "$(just _no_tests)" = "yes" ]; then echo "test: no tests yet"; else mvn -q test; fi

coverage:
    @if [ "$(just _no_tests)" = "yes" ]; then echo "coverage: no tests yet"; else mvn -q verify; fi

check-all: format lint coverage
    @echo "All checks passed"

clean:
    mvn -q clean
```

L2 adds:

```just
spec-test:
    mvn -q -Dtest=*Spec test
```

L3 adds:

```just
mutate:
    mvn -q org.pitest:pitest-maven:mutationCoverage

spec-audit:
    specdrive audit
```

## Dual coverage (L2+)

JaCoCo provides line and branch coverage. At L2+, configure JaCoCo with two checks — one against the BDD-driven coverage, one against unit-only. Configuration uses JaCoCo's `excludes`/`includes` to split.

## Anti-patterns

- Using JUnit 4. JUnit 5 is the standard.
- Coupling Cucumber step defs to Spring `@Autowired` — domain step defs should be plain.
- Running PIT on every PR. It's slow; schedule it weekly.
- Skipping Spotless because "the team disagrees on style." Pick the style; commit to it.
