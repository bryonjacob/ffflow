# Tier 2 security — Java recipes

Implements the [Tier 2 security](../tier-2-security.md) recipe contract for the Java stack. See that file for the recipe list, rules, CI integration, and anti-patterns.

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
