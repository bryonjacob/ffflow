# The PPP process: product ping-pong

The process contract every `ppp:prd-*` skill implements. It describes documents and turns, not where
they live: each PRD's medium is agreed when it starts (see `media.md`) and recorded in the bundle's
`medium.md`.

## Seats

A seat is a role in the process. The process defines what a seat owns, never who holds it or how
they work.

| Seat | Owns | Must not |
|---|---|---|
| **builder** | feasibility, shape of the solution, relative sizes, risks | set product commitments or service levels |
| **product** | outcomes, client experience, commitments, service levels, priorities | dictate implementation |
| **analyst** | answering data requests with evidence, neutrally | argue a position |
| **facilitator** | turn order, checks, retros, convergence (this is the plugin itself) | change PRD content |

**Everyone sees everything.** Every file in the bundle is readable by every seat at every turn.
No private channels. `medium.md` may name the people who hold seats and how to reach them; the PRD
and parking lot never name people.

## The bundle

```
<root>/                    wherever the medium puts it; the worked example uses docs/prds/
  _shared/                 one per portfolio
    roles.md               role glossary: every role a PRD may name
    glossary.md            domain terms
    roster.txt             names of real people in the inputs (used only by prd-check)
    inputs/                source material: requests, KR docs, research
    limits.json            optional; overrides the defaults in the service parameters
  <slug>/
    <slug>-prd.md          the PRD: the shape, nothing else
    parking-lot.md         ideas, splits and planning questions that are not this PRD
    evidence/              requests.md is the queue; <nn>-<topic>.md are the answers
    rounds/<n>-summary.md  the retro for round n
    turns/<n>-<seat>.md    turn memos
    state.json             round, next seat, status, sign-offs, split links
    medium.md              the agreed medium: where each part lives, how versions,
                           hand-off, sign-off and the commit work
```

These are the default names. A medium may hold a part differently (a page, a doc, a tracker item)
as long as `medium.md` says where, and a local copy under these names can be made for `prd-check`.
`rounds/` and `turns/` appear when first written.

A medium must keep a version of the PRD per turn (git commits, doc versions). The process never
stores history inside the PRD.

## Finding a bundle

Every skill after `prd-start` takes a bundle pointer: a local folder, a URL, or whatever
`medium.md`'s Reference says identifies the bundle. With no pointer, the skill looks under the
working directory for folders holding both `medium.md` and `state.json`. One match: use it.
Several: ask. The skill reaches a non-local medium through whatever access the session has; if it
has none, it says so and stops.

**A bundle with no `medium.md`** (started before `medium.md` existed; its PRD may be named
`prd.md`) is never a failure. Ask the user how the bundle is being managed, offering the worked
example in `media.md`, write `medium.md` from `templates/medium.md`, then continue.

### The check runs on local files

`prd-check` reads files on disk. For a non-local medium, the skill copies the PRD, the parking lot,
the evidence files, the previous PRD version, `_shared/roster.txt` and `_shared/limits.json` into a
scratch folder under the default names (`<scratch>/<slug>/…`, `<scratch>/_shared/…`), runs the
check there, and writes back only after PASS. The worked example is already local.

### What a medium may decide

A medium document defines *where and how* only: locations, versions, hand-off, sign-off and the
commit act. It never changes the process: seats, turns, rules, rounds and the check stay as this
document says. Any outward-facing or irreversible act it calls for (sharing with people,
publishing, opening or merging a pull request) is confirmed with the user before it is done.

## What goes in the PRD

Fixed headings (`templates/prd.md`): Problem · Roles · Outcomes and non-goals · Journeys ·
Requirements · Service parameters · Metrics · Increments · Risks · Key decisions · Open questions.

Rules:
1. **Shape, not history.** No "accepted by", "proposed by", "previously", "corrected", round
   numbers or who-said-what. Memos and round summaries hold the history.
2. **Roles, never people.** Only roles from `_shared/roles.md`. A fact about a person becomes a
   requirement about a role ("no step depends on one person; any trained staff member in the
   account-owner role can pick up any request").
3. **No effort or schedule.** No hours, days, weeks, sprints, dates, quarters or "before X" about
   building or delivering. Sizes are **S, M, L, XL** and appear only in Increments, only to compare.
   No XXL: an item that big is listed as its parts, each XL or smaller.
4. **Service levels are behaviour, specified exactly.** Every promise the product makes (a
   turnaround, a response time, a retention window) gets a row in Service parameters: unit · exact
   calculation (start, pause, stop, business-day and holiday rules) · default and whether it is
   configurable per client or by policy without a code change · how it is measured · what happens
   at risk and at breach. Time units are allowed here and in metric windows, nowhere else.
5. **Data is cited, not pasted.** Key numbers appear with a link to an `evidence/` file.
6. **Key decisions: 0 to 3.** Only high-impact choices likely to be relitigated. The best PRDs need
   none because the requirements already say it.
7. **Provisional values are tagged.** Any seat writing a value no one has evidence or authority for
   writes it `[provisional]` or `[provisional: <reason>]`; both forms count, and a reason is
   encouraged. A PRD can converge with provisional values; it cannot be ratified with them.
8. **Soft ceiling about 2,500 words.** Any turn that grows the PRD must justify the growth in its
   memo as net-new information the final PRD needs.

## The parking lot

Every turn asks: what doesn't belong here? Each entry is one line plus a kind:

| Kind | Meaning |
|---|---|
| `idea` | good, not this PRD |
| `planning` | scheduling, capacity, sequencing against other work: belongs to the planning step |
| `other-prd` | belongs to a named existing PRD |
| `split` | big enough to be its own PRD; `prd-split` turns it into a charter |

Parking is how a seat stays on the prize without losing the thought.

Parking costs nothing: never hesitate to park. Keeping the lot readable is the retro's job: each
entry stays one line (about 30 words).

## A turn

1. Get the current bundle as `medium.md` says and read all of it.
2. Respond to the other seat's last turn: accept, push back with evidence, offer one alternative.
3. Edit the PRD in place. Close what you can; add questions with the next free ID.
4. Park anything that doesn't belong.
5. Optionally file data requests in `evidence/requests.md`.
6. Write the memo (≤ 500 words): accepted · pushed back · parked · data asked · growth
   justification · **Cut** (the biggest thing removed this turn, and what you would cut next to
   reach about 80% of the ceiling) · **Key decisions kept** (for each, why a requirement can't
   carry it). Limits are ceilings, not targets.
7. Run `prd-check` (on a local copy if the medium isn't local). The turn lands only when it passes.
8. Write back and hand off as `medium.md` says.

## Data requests

Either seat may ask. The analyst answers before the next turn into `evidence/<nn>-<topic>.md`:
question · method · result · as-of date · caveats. The analyst answers the question asked and
offers no opinion. Evidence is the main thing that moves positions; ask early.

## Rounds and convergence

A round is one turn per side, then a retro. Default cap: 3 rounds.

- **Round 1:** the opening seat drafts (usually builder, from inputs); the other responds.
- **Round 2:** narrow. No new fronts unless critical.
- **Round 3 (closing):** builder proposes a resolution for every open question; product closes
  every one: `answered`, `deferred` (owner role and a trigger, never a date), or `dropped` (reason).
  Each seat records sign-off (`yes`, `yes-with-conditions` or `no`) in its closing memo, in
  `state.json`, and in the medium as `medium.md` says. A condition must exist in the PRD as a
  requirement or a deferred question.
- **Round 4** only to close a real blocker. Never a fifth.

States: `drafting` → `converged` (zero open questions, check clean) → `ratified` (converged, every
seat signed off `yes` or `yes-with-conditions`, no `[provisional]` left). Ratification is completed
by the medium's commit act (worked example: merge).

## Retro (end of every round, on the record)

Each seat answers, in ≤ 150 words:
1. What changed your mind this round, and on what evidence?
2. What worries you most in the PRD as it stands?
3. What would you give up to close faster?
4. What are you assuming that isn't written down?
5. Did anything you parked deserve to be its own PRD?

The facilitator tidies the parking lot (merges duplicates, marks routed `other-prd` and `split`
entries with where they went), then writes `rounds/<n>-summary.md` (≤ 300 words): what moved ·
still contested · parked · data gathered · sign-off posture · what the next round must do. Every
seat reads it next.

## Split signals

`prd-check` recommends a split when any of these hold after a trim pass: over the ceiling ·
more than 3 key decisions · more than 2 XL increments · size debates in two consecutive memos ·
journeys for distinct primary users who never interact. The facilitator proposes the split; the
seats accept or reject it in their next memo.

## Evidence rule (every seat)

Every decision cites a document in the bundle. A value with no evidence in the bundle and no
authority in the inputs is written `[provisional]`, or `[provisional: <reason>]` (a reason is
encouraged). Never present an invented person, date or number as firm. A PRD can converge with
provisional values; it cannot be ratified with them.

## Exit

A converged PRD, zero `?`, is ready for planning; parked `planning` items travel with it. PPP stops
there: any planning process can take it (for example, the `fff` plugin's `/fff:plan-roadmap` or
`/fff:plan-chat`).
