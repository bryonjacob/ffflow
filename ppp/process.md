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
| **facilitator** | turn order, checks, retros, findings, status (this is the plugin itself) | change PRD content: what it notices goes in round summaries as findings |

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
    facts.md               the one canonical fact sheet; the analyst keeps it (§Data requests)
    inputs/                source material: requests, KR docs, research
    limits.json            optional; overrides the defaults in the service parameters
  <slug>/
    <slug>-prd.md          the PRD: the shape, nothing else
    parking-lot.md         ideas, splits and planning questions that are not this PRD
    evidence/              requests.md is the queue; <nn>-<topic>.md are the answers
    rounds/<n>-summary.md  the retro for round n
    turns/<n>-<seat>.md    turn memos
    state.json             round, round cap, next seat, status, sign-offs, split links
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
5. **Data is cited, not pasted.** Key numbers appear with a link to an `evidence/` file or to
   `_shared/facts.md`.
6. **Key decisions: 0 to 3.** Only high-impact choices likely to be relitigated. The best PRDs need
   none because the requirements already say it.
7. **Provisional values are tagged.** Any seat writing a value no one has evidence or authority for
   writes it `[provisional]` or `[provisional: <reason>]`; both forms count, and a reason is
   encouraged. A PRD can converge with provisional values; it cannot be ratified with them.
   Clearing one needs a reason: the memo's **Provisional cleared** lines name each value and the
   evidence file, or the role from `_shared/roles.md` whose authority settles it.
8. **Soft ceiling about 2,500 words.** Any turn that grows the PRD must justify the growth in its
   memo as net-new information the final PRD needs. This holds in every round.
9. **Questions keep their rows.** Answered, deferred and dropped rows stay in the table, and a `Q-n`
   is never reused. Each fact lives once: an answered question's Resolution only points to where
   the answer lives (`→ R-15`, `→ §6 Turnaround`), in at most 15 words. Deferred: an owner role and
   a trigger, never a date. Dropped: the reason.

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

**Handing over is a conditional yes.** Every turn that passes the PRD on means: "I'd sign this
exactly as it stands, if you will."

1. Get the current bundle as `medium.md` says and read all of it.
2. Respond to the other seat's last turn: accept, push back with evidence, offer one alternative.
   Answer, by ID, every facilitator finding addressed to your seat (§Retro).
3. Edit the PRD in place. Close what you can; add questions with the next free ID.
4. Park anything that doesn't belong.
5. Optionally file data requests in `evidence/requests.md`.
6. Write the memo (`templates/memo.md`, ≤ 500 words). Limits are ceilings, not targets.
7. Run `prd-check` (on a local copy if the medium isn't local). The turn lands only when it passes.
8. Write back and hand off as `medium.md` says. A turn never changes `status` in `state.json`;
   only `prd-retro` sets it.

**Agreement is a no-edit turn.** A seat that would sign the PRD as it stands takes a turn that
leaves it byte-identical to what it received (only trailing whitespace and line endings may
differ); its memo says `agreed`. The parking lot, evidence requests and the memo may still change.
Any change to the PRD is a normal turn, and the ball goes back.

## Data requests

Either seat may ask. The analyst answers before the next turn into `evidence/<nn>-<topic>.md`:
question · method · result · as-of date · caveats. The analyst answers the question asked and
offers no opinion. Evidence is the main thing that moves positions; ask early. Requests may be
answered while the retro runs.

`_shared/facts.md` (`templates/facts.md`) is the portfolio's one fact sheet. When sources disagree,
the analyst records there, through `prd-data`, which source wins and why. PRDs cite `facts.md` or
evidence files, never a raw input that `facts.md` overrides.

## Rounds and convergence

A round is one turn per side, then a retro.

- **Round 1: data before rulings.** The opening seat drafts (usually builder, from inputs); the
  other responds. Each round-1 memo lists the data requests it filed, or says `none needed` and why.
- **Later rounds:** narrow. No new fronts unless critical.
- **Round cap** (`round_cap` in `state.json`, default 3) is an escalation trigger, not a closing
  rule: at the cap, the portfolio lead decides to split, park, or allow another round.

States, set only by `prd-retro`:
- `drafting`.
- `converged`: the latest turn is an agreement turn, zero questions are open, the check passes,
  and no facilitator finding is unanswered.
- `ratified`: converged, no `[provisional]` value in either form, and the medium's commit act done
  (worked example: PR marked ready for review, every seat approves the unchanged PRD, then merge).

**Sign-off is `yes` or `no`**, given through the medium's sign-off act once converged and recorded
in `state.json`. There are no conditions: a condition is a change, so it is made in another turn,
the ball goes back, and the PRD is drafting again. Status lives in `state.json` only; the PRD has
no status line, because the facilitator never edits the PRD.

## Retro (end of every round, on the record)

Each seat answers, in ≤ 150 words per answer (words of the answer only; headings and question
labels don't count):
1. What changed your mind this round, and on what evidence?
2. What worries you most in the PRD as it stands?
3. What would you give up to close faster?
4. What are you assuming that isn't written down?
5. Did anything you parked deserve to be its own PRD?

The facilitator tidies the parking lot (merges duplicates, marks routed `other-prd` and `split`
entries with where they went), then writes `rounds/<n>-summary.md` (≤ 300 words): what moved ·
still contested · parked · data gathered · convergence posture · what the next round must do ·
facilitator findings. Every seat reads it next.

**Facilitator findings.** What the retro surfaces (an unwritten assumption, a question, a gap) the
facilitator writes as a finding in the round summary, never in the PRD: `F-n` numbered across the
whole bundle and never reused, an owner seat, and the text. The owning seat's next memo answers
each by ID: `accepted` (and where the PRD now covers it) or `rejected` (with a reason). A finding
raised after the agreement turn that matters is a named blocker: the portfolio lead decides on
another round, as at the cap. Otherwise it is parked.

## Split signals

`prd-check` recommends a split when any of these hold after a trim pass: over the ceiling ·
more than 3 key decisions · more than 2 XL increments · size debates in two consecutive memos ·
journeys for distinct primary users who never interact.

A split is proposed in an ordinary turn: a `split` entry in the parking lot and the memo line
`Split P-n: accept`. The other seat answers in its next memo, `Split P-n: accept` or
`Split P-n: reject`. Both seats' acceptances are `prd-split`'s confirmation; there is no special
split mode. The facilitator may suggest a split only as a finding.

## Evidence rule (every seat)

Every decision cites a document in the bundle. A value with no evidence in the bundle and no
authority in the inputs is written `[provisional]`, or `[provisional: <reason>]` (a reason is
encouraged). Never present an invented person, date or number as firm. A PRD can converge with
provisional values; it cannot be ratified with them.

## Exit

A converged PRD, zero `?`, is ready for planning; parked `planning` items travel with it. PPP stops
there: any planning process can take it (for example, the `fff` plugin's `/fff:plan-roadmap` or
`/fff:plan-chat`).
