# FFFlow — repository root

This repo is both a **Claude Code marketplace** and the **plugin** it ships. The plugin's own design docs live in [`plugin/CLAUDE.md`](plugin/CLAUDE.md) and [`plugin/docs/architecture.md`](plugin/docs/architecture.md) — read those for skill design. This file covers repo-level process.

## Layout

```
ffflow-plugin/
├── .claude-plugin/marketplace.json    # marketplace manifest (this repo as a marketplace)
├── plugin/                            # the actual plugin (source: "./plugin")
│   ├── .claude-plugin/plugin.json     # plugin manifest
│   ├── docs/migrations.md             # migration ledger read by /fff:upgrade-ffflow
│   └── CLAUDE.md                      # plugin design (authoritative for skills)
├── CHANGELOG.md                       # human-facing release history
├── README.md
└── LICENSE
```

## How we version

**Three version fields, kept in lockstep.** Bump all three together on every release:

1. `.claude-plugin/marketplace.json` → `metadata.version`
2. `.claude-plugin/marketplace.json` → `plugins[0].version`
3. `plugin/.claude-plugin/plugin.json` → `version`

They track the same thing because there's one plugin in this marketplace. Keeping them aligned is the simplest mental model — don't let them drift.

**Semver, content-based:**

- **patch** (`0.2.0 → 0.2.1`) — additive or backward-compatible: new recipes/cartridges, restructured-but-equivalent content, doc fixes, new stack/language support.
- **minor** (`0.2.x → 0.3.0`) — new skills, new user-facing capability, or a meaningful workflow addition.
- **major** (`0.x → 1.0`) — removing/renaming a skill or changing a documented interface (recipe names, `--type` values, config schema, anything in [`plugin/docs/integration-surface.md`](plugin/docs/integration-surface.md)) in a breaking way.

**Why bump at all?** Claude Code picks up the latest commit on plugin update regardless of the number — the version is the *human* signal that something changed (and what the update UI compares). A static version across a real change is a footgun; always bump.

## Every release updates two ledgers

Versioning is only half the job. A release also has to tell **existing projects** what changed for them.

1. **`CHANGELOG.md`** (repo root) — for humans. Every release gets an entry.
2. **`plugin/docs/migrations.md`** — for `/fff:upgrade-ffflow`. Only **repo-affecting** releases get an entry: ones where an already-adopted project would be wrong or incomplete until something in it changes.

The test: *"If I upgrade the plugin and change nothing in my repo, is my repo now inconsistent with FFFlow?"* Yes → migration entry required. New skill that only reads existing artifacts, or a bug fix in a skill's own logic → changelog only.

**This is not optional bookkeeping.** The upgrade path is only as good as the ledger. A repo-affecting change shipped without a migration entry is invisible to every existing project forever — which is precisely the failure 0.4.0 exists to fix. Ledger entry schema and the full decision table live in `plugin/docs/migrations.md`.

Migration entry ids are permanent: never rename or reuse one, because unstamped repos duck-type against the whole ledger from 0.1.0 forward.

**Process:** bump the three fields → update `CHANGELOG.md` → add a `migrations.md` entry if repo-affecting → commit (include all of it in the same commit as the change) → push. No tags or release artifacts are required today; if that changes, document it here.
