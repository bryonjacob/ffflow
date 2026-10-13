---
name: prd-check
description: Run the mechanical rules of the PPP process on a PRD bundle — fixed headings, size and growth, person names, effort/schedule time units, sizes, history in the PRD, key-decision count, question-table form and resolution pointers, removed questions, agreement turns, facilitator findings, cleared provisional values, provisional values at ratification, evidence links, parking-lot kinds, and split signals. A turn lands only when this passes.
---

# prd-check

## Plan Mode

This skill does NOT invoke Plan Mode. It reads files and reports.

## Run

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/prd-check/check.py" <bundle-dir | prd-file> [--shared DIR] [--prev FILE --memo FILE] [--summary FILE --seat SEAT] [--agree] [--ratify] [--json]
```

(`check.py` sits beside this file.)

## Input

- **The PRD:** a file argument; else the single `*-prd.md` in the directory; else `prd.md`.
- **The parking lot:** `parking-lot.md` beside the PRD.
- **Turn inputs:** `--prev` is the PRD as this seat received it and needs `--memo`, this seat's own memo. `--summary` is the latest round summary and needs `--memo` and `--seat`. `--agree` (an agreement turn) needs `--prev`. `prd-turn` says exactly which files to pass.
- **Shared:** `--shared` defaults to `<bundle>/../_shared`. `roster.txt` there feeds NAME; `roles.md` feeds PROVISIONAL-CLEARED. An optional `limits.json` overrides the defaults: `ceiling` (2500), `key_decisions` (3), `memo_words` (500), `xl_increments` (2), `near_ceiling_pct` (90), `parking_entry_words` (30).
- **Local files only.** For a non-local medium the caller copies first (`${CLAUDE_PLUGIN_ROOT}/process.md` §The check runs on local files).
- **Exit codes:** 0 pass (warnings allowed), 1 fail, 2 input error (no PRD, more than one `*-prd.md`, unreadable `--prev`/`--memo`/`--summary`, `--prev` without `--memo`, `--agree` without `--prev`, `--summary` without `--memo` and `--seat`, bad `limits.json`).

## Rules

| Code | Fails when | Why |
|---|---|---|
| HEADINGS | the `##` headings are not exactly the template's eleven `## n. Title`, in order | one shape for every PRD |
| GROWTH | the PRD grew and the memo has no growth justification | stop bloat |
| NAME | a name from `_shared/roster.txt` appears in the PRD or `parking-lot.md` | roles, never people |
| TIME | a duration, effort unit, quarter, month or date appears outside Service parameters and Metrics | no effort or schedule |
| SIZE | XXL or bigger appears | decompose instead |
| HISTORY | "round n" appears (other history phrases warn) | the PRD is the shape, not the story |
| DECISIONS | more key decisions than the limit (3) | the rest belong in requirements, or a split |
| QUESTIONS | a row is malformed or has empty question text, `?` doesn't match status, deferred lacks owner/trigger, closed lacks resolution; an answered resolution has no `R-n` / `§n` pointer, points to an R-id or section not in the PRD, or exceeds 15 words | convergence is mechanical; each answer lives once, in the PRD |
| QUESTIONS-REMOVED | `--prev` and a `Q-n` in the previous version is missing now | closed rows stay; IDs are never reused |
| AGREE | `--agree` and the PRD differs from `--prev` beyond trailing whitespace and line endings | agreement is a no-edit turn; any change is a normal turn |
| OPEN-QUESTIONS | `--agree` or `--ratify`, and any question still open | converging needs none open |
| FINDINGS | `--summary` and a facilitator finding owned by `--seat` isn't mentioned by its `F-n` in the memo | every finding gets accepted or rejected |
| PROVISIONAL-CLEARED | `--prev`: the provisional count dropped by N and the memo has fewer than N **Provisional cleared** entries with an `evidence/` link or a role from `_shared/roles.md` | a value becomes firm only on evidence or authority |
| PROVISIONAL | `--ratify` and any `[provisional]` or `[provisional: …]` remains | a ratified PRD has no unsupported values |
| EVIDENCE | a link into `evidence/` doesn't resolve | cited data must exist |
| PARKING | no parking lot, or an entry with an unknown kind | the lot is part of every turn |

## Warnings

| Code | Warns when |
|---|---|
| CEILING | over the soft ceiling |
| CEILING-NEAR | at or above `near_ceiling_pct` of the ceiling: trim before adding |
| DECISIONS-AT-LIMIT | key decisions exactly at the limit: could a requirement carry one? |
| XL-AT-LIMIT | XL increments exactly at the limit: could one be smaller, or split? |
| PROVISIONAL-CLEARED | no `roles.md`: any non-empty cleared entry is accepted |
| SIZE | a size appears outside Increments |
| HISTORY | soft history phrases ("previously", "accepted by", …) |
| MEMO | the memo is over the memo limit |
| NAME | no roster found; the name check was skipped |
| PARKING-LONG | a parking-lot entry's item + why exceeds `parking_entry_words` |
| SPLIT | split signals: over the ceiling, more key decisions than the limit, more XL increments than the limit |

Limits are ceilings, not targets.

## Reports

Words and growth, key-decision count, questions by status (open / answered / deferred / dropped), provisional count (both tag forms), XL increments.

`--json` prints:
```
{"result": "PASS|FAIL", "prd": "<path>", "words": n, "growth": {"before": n, "after": n} | null,
 "key_decisions": n, "questions": {"open": n, "answered": n, "deferred": n, "dropped": n},
 "provisional": n, "xl_increments": n,
 "fails": [{"code", "file", "line", "message"}], "warns": [...]}
```
On an input error it prints `{"result": "ERROR", "message": "..."}` and exits 2.

## Known limits

Names are caught only from the roster, not detected. The time check is pattern-based: it cannot tell "before the account owner leaves" is schedule talk. A reviewer seat still reads for both.
