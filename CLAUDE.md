# FFFlow — repository root

This repo is both a **Claude Code marketplace** and the **plugin** it ships. The plugin's own design docs live in [`plugin/CLAUDE.md`](plugin/CLAUDE.md) and [`plugin/docs/architecture.md`](plugin/docs/architecture.md) — read those for skill design. This file covers repo-level process.

## Layout

```
ffflow-plugin/
├── .claude-plugin/marketplace.json    # marketplace manifest (this repo as a marketplace)
├── plugin/                            # the actual plugin (source: "./plugin")
│   ├── .claude-plugin/plugin.json     # plugin manifest
│   └── CLAUDE.md                      # plugin design (authoritative for skills)
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
- **major** (`0.x → 1.0`) — removing/renaming a skill or changing a documented interface (recipe names, `--type` values, config schema) in a breaking way.

**Why bump at all?** Claude Code picks up the latest commit on plugin update regardless of the number — the version is the *human* signal that something changed (and what the update UI compares). A static version across a real change is a footgun; always bump.

**Process:** bump the three fields → commit (include the bump in the same commit as the change) → push. No tags or release artifacts are required today; if that changes, document it here.
