# Migration ledger

The machine-readable half of [`CHANGELOG.md`](../../CHANGELOG.md). `/fff:upgrade-ffflow` reads **this** file, not the changelog.

## What belongs here

Only **repo-affecting** changes: releases that change what a project's own files should look like. A change is repo-affecting if, after upgrading the plugin, an existing project would be *wrong* or *incomplete* until something in it changes.

| Change | Repo-affecting? |
|---|---|
| New skill that reads existing artifacts | ❌ — nothing in the repo needs to change |
| New invariant that requires a new artifact | ✅ |
| New config field | ✅ |
| Changed default template | ✅ (existing generated files now differ from the template) |
| Bug fix in a skill's own logic | ❌ |
| New stack cartridge | ❌ (opt-in; only affects projects that choose it) |
| Renamed config field / skill / recipe | ✅ (and it's a major bump) |

When in doubt, ask: *"If I upgrade the plugin and change nothing in my repo, is my repo now inconsistent with FFFlow?"* Yes → it needs an entry.

## Entry schema

Each entry is one repo-affecting change. Entries are ordered oldest-first within a version, and versions oldest-first in the file.

```yaml
- id: example-entry-id                 # stable, unique across all versions; never reused or renamed
  version: 0.4.0                       # version that introduced the change
  title: Human-readable one-liner
  applies_when: always                 # always | a condition on .ffflow/config.yaml or repo state
  severity: high                       # high | medium | low — drives ordering and default selection
  detect: |                            # how to tell if this repo ALREADY has the change
    Prose or shell describing the check. MUST be decidable by reading the repo,
    never by trusting the version stamp.
  remediate: |                         # what to do when detect says "missing"
    What upgrade-ffflow should do. Delegate to an existing skill wherever one owns the artifact.
  autonomous: true                     # safe to apply without asking? (false → always confirm)
```

**`detect` must never consult `ffflow_version`.** The stamp is a hint for ordering and reporting; detection is always evidence-based against the repo itself. That is what makes duck-typing an unstamped repo work, and what makes the ledger self-correcting when a repo was hand-edited.

---

## Ledger

### 0.1.0 — initial release

```yaml
- id: ffflow-config
  version: 0.1.0
  title: .ffflow/config.yaml exists
  applies_when: always
  severity: high
  detect: |
    `.ffflow/config.yaml` exists and parses as YAML with a `level:` key.
  remediate: |
    The project is not on FFFlow at all. Do not upgrade — stop and direct the
    user to `/fff:adopt-ffflow`. upgrade-ffflow reconciles adopted projects;
    it does not adopt them.
  autonomous: false
```

### 0.2.0 — specdrive is language-agnostic

```yaml
- id: l3-unlocked-all-stacks
  version: 0.2.0
  title: L3 available on Python / Java / Rust
  applies_when: config.stack in [python, java, rust, polyglot]
  severity: low
  detect: |
    Nothing in the repo records the old cap, so this is an informational entry
    rather than a remediation. Consider it "present" if config.level is already
    L3, or if the user has never expressed interest in raising the level.
  remediate: |
    Inform only — do not change the level. Tell the user that L3 is available on
    their stack (it was incorrectly capped at L2 before 0.2.0) and that raising it
    is a deliberate methodology choice made via `/fff:init-ffflow`.
  autonomous: true
```

### 0.2.1 — per-language justfile cartridges

```yaml
- id: justfile-baseline-recipes
  version: 0.2.1
  title: Justfile implements the baseline recipe set
  applies_when: a justfile exists at the project root
  severity: medium
  detect: |
    The root `justfile` defines the baseline recipes named in the `justfile`
    skill (test, lint, format, check-all, and the stack's own additions).
    Missing recipes = gap. No justfile at all = not applicable (the project
    opted out; do not install one during an upgrade).
  remediate: |
    Delegate to `/fff:stack-init`, which owns justfile generation and is
    idempotent and non-destructive. Report which recipes were missing.
  autonomous: false
```

### 0.3.0 — view-layer purity

```yaml
- id: ui-view-layer-purity
  version: 0.3.0
  title: View-layer-purity structure adopted for UI projects
  applies_when: config.stack == typescript-ui, OR repo has UI signals (react, react-dom, lit, @awesome.me/webawesome, vue, svelte, @storybook/*, .storybook/)
  severity: medium
  detect: |
    Three things together: (1) `.ffflow/stack.yaml` sets `extends: typescript-ui`
    with a `ui_baseline` dimension; (2) a `.storybook/` directory exists;
    (3) a design-token layer exists. Any missing = gap.

    A project with UI signals but `stack: typescript` (not `typescript-ui`) is
    the common pre-0.3.0 shape — flag it, since switching stacks is a
    methodology decision the user must make.
  remediate: |
    Delegate to `/fff:adopt-ffflow --ui` (optionally `--lane react|web-components`),
    which is the purpose-built retrofit verb for exactly this migration.
  autonomous: false
```

### 0.4.0 — beliefs, hierarchy, and version stamping

```yaml
- id: version-stamp
  version: 0.4.0
  title: .ffflow/config.yaml carries ffflow_version
  applies_when: always
  severity: high
  detect: |
    `.ffflow/config.yaml` has an `ffflow_version:` key.
  remediate: |
    Write `ffflow_version` and `ffflow_upgraded`. This is the LAST step of any
    upgrade run — never stamp before the other remediations have been applied or
    explicitly declined, or the repo claims a version it hasn't reached.
  autonomous: true

- id: beliefs-block
  version: 0.4.0
  title: Managed beliefs block in root CLAUDE.md
  applies_when: always
  severity: high
  detect: |
    Root `CLAUDE.md` contains a matched pair of `<!-- ffflow:beliefs ... -->` and
    `<!-- ffflow:beliefs end -->` markers. If present, compare the version in the
    opening marker to the current plugin version — older = stale, needs refresh.
    An unmatched or malformed marker pair is a gap, not an error: rewrite it whole.
  remediate: |
    Write or refresh the block per the canonical text in the `init-ffflow` skill.
    Replace ONLY the bytes between the markers. If no markers exist, insert the
    block after the root file's opening purpose/overview section and before the
    first deep-detail section — high enough to be read, not so high it displaces
    the file's own introduction.
  autonomous: true

- id: hierarchical-claude-md
  version: 0.4.0
  title: Significant modules carry their own CLAUDE.md
  applies_when: always
  severity: high
  detect: |
    Run the `claude-md` audit cartridge's coverage scan (§1 of that cartridge).
    Any significant directory without a CLAUDE.md is a gap. Reuse the cartridge's
    significance criteria verbatim — do not reimplement them here.
  remediate: |
    Do NOT generate the files here. Delegate to
    `/fff:audit --type claude-md --fix`, which owns CLAUDE.md coverage,
    templates, and generation. Report the gap count and hand off.

    This entry is the reason 0.4.0 exists: a repo can be years into FFFlow and
    still have exactly one CLAUDE.md, because coverage was only ever an audit
    finding and never a stated belief.
  autonomous: false

- id: uncommit-session-notes
  version: 0.4.0
  title: Session notes and decision logs are not committed
  applies_when: always
  severity: high
  detect: |
    Any of these tracked by git (`git ls-files`):
      - `.ffflow/notes/**`
      - a `notetoself-*.md` anywhere in the tree
      - a decision log written by `/fff:autopilot --decision-log` to a repo path
    Tracked = gap. Present-but-gitignored = fine, that's the intended end state.
  remediate: |
    For each tracked file: `git rm --cached <path>` (keep the working copy —
    it's someone's session state and may still be in use), then add the pattern
    to `.gitignore`.

    Before removing, SHOW the user the file list and ask. A note may contain
    content that belongs to the project — if so, promote that content into the
    spec, an issue, or a module CLAUDE.md first, then untrack the note.

    Never delete the working copy, and never untrack without confirmation:
    someone may be mid-handoff.

    Cause: pre-0.4.0 `notetoself` advised copying notes into `.ffflow/notes/`
    for durability past /tmp cleanup, contradicting its own state table. That
    advice is gone; this entry cleans up after it.
  autonomous: false

- id: root-conventions-hierarchy
  version: 0.4.0
  title: Root CLAUDE.md Conventions block names the hierarchy rule
  applies_when: root CLAUDE.md has a Conventions section
  severity: low
  detect: |
    The Conventions section mentions per-module / hierarchical CLAUDE.md.
    Largely subsumed by `beliefs-block` — this entry catches projects whose
    Conventions section is hand-maintained outside the managed markers.
  remediate: |
    Suggest (do not auto-write) adding a hierarchy bullet to the human-owned
    Conventions section, or point out that the beliefs block already covers it
    and the Conventions duplicate can be trimmed.
  autonomous: false
```

### 0.4.1 — audit.yaml is written by auditors only

```yaml
- id: work-issue-no-self-stamp
  version: 0.4.1
  title: work-issue no longer instructs agents to stamp audit.yaml
  applies_when: always
  severity: high
  detect: |
    Two things to check:
    1. Does `.ffflow/audit.yaml` exist with commits recorded in it? For each
       recorded `last_pass_commit` (or equivalent per-file stamp), check
       whether that commit's message/diff looks like an ordinary feature/fix
       PR rather than an `/fff:audit` run (no audit report in the PR body, and
       the changed files are the stamped files themselves, not audit tooling).
       Any such commit is a self-certifying stamp — evidence nobody but the
       author validated it.
    2. This is a doc/instruction bug, not a schema change — there is nothing
       to detect in `.ffflow/config.yaml` or skill files themselves once the
       plugin is updated. The gap lives entirely in `audit.yaml`'s *content*,
       written under the old (pre-0.4.1) `work-issue` instruction.
  remediate: |
    Do not silently rewrite the file. Self-certifying stamps mean the recorded
    `validated_at` / `last_pass_commit` for those files is unreliable — the
    file was likely edited by ordinary work after being stamped, or the stamp
    itself was never backed by an actual audit run.

    Show the user the list of suspect entries and recommend running
    `/fff:audit --type <affected>` to re-validate for real and overwrite the
    bogus stamps with a genuine one. Do not hand-edit `audit.yaml` yourself —
    only an auditor cartridge writes that file.

    Cause: pre-0.4.1 `work-issue` (`SKILL.md` Outputs list) told agents to
    update `.ffflow/audit.yaml` "if any audited file is touched." That
    inverted the file's meaning — a stamp is supposed to mean an auditor
    validated the file, not that its own editor touched it. Fixed by removing
    the line and stating the invariant explicitly in `audit/SKILL.md`:
    "audit.yaml is written by auditors only. An editor never stamps its own
    work." The one sanctioned exception is `characterize`, which registers
    `characterized: true` for spec entries it just wrote — an auditor-shaped
    act, not self-certification of a code change.
  autonomous: false
```

### 0.4.3 — repo moved to zerotechdebt/ffflow

```yaml
- id: ffflow-repo-url
  version: 0.4.3
  title: Root CLAUDE.md links FFFlow at github.com/zerotechdebt/ffflow
  applies_when: root CLAUDE.md exists
  severity: low
  detect: |
    Search root `CLAUDE.md` for either old FFFlow repo URL:
      - `github.com/bryonjacob/ffflow-plugin` (never existed — a 404)
      - `github.com/bryonjacob/ffflow` (redirects, but stale)
    e.g. `grep -nE 'github\.com/bryonjacob/ffflow(-plugin)?\b' CLAUDE.md`.
    Any hit = gap. No hits = present. Do not touch other `bryonjacob/*`
    repos (e.g. `bryonjacob/specdrive` is a separate project that did not move).
  remediate: |
    Hits inside the `<!-- ffflow:beliefs ... -->` markers: refresh the block
    from the canonical text in `init-ffflow` (the same remediation as
    `beliefs-block`; if that entry already ran this upgrade, this is already
    done). Replace only bytes between the markers.

    Hits outside the markers are human-owned: show each line and offer to
    replace the URL with `https://github.com/zerotechdebt/ffflow`. Apply only
    on confirmation.

    Cause: pre-0.4.3 `init-ffflow` stamped `https://github.com/bryonjacob/ffflow-plugin`,
    a URL that never existed. The repo then moved from `bryonjacob/ffflow` to
    `zerotechdebt/ffflow`; the canonical block now links there.
  autonomous: true
```
