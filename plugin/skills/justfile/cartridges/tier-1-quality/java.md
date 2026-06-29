# Tier 1 quality — Java recipes

Implements the [Tier 1 quality](../tier-1-quality.md) recipe contract for the Java stack. See that file for the recipe list, rules, and anti-patterns.

```just
test-watch:
    mvn -q fizzed-watcher:run -Dwatcher.touchFile=src/main/java

integration-test:
    mvn -q failsafe:integration-test

complexity:
    mvn -q spotbugs:check -Dspotbugs.includeFilterFile=spotbugs-complexity.xml

loc:
    @find src/main/java -name "*.java" -exec wc -l {} + | sort -rn | head -20

duplicates:
    mvn -q org.codehaus.mojo:cpd-maven-plugin:cpd

slowtests:
    mvn -q test -Dsurefire.printSummary=true | grep -E "ran in" | sort -rn | head -50
```
