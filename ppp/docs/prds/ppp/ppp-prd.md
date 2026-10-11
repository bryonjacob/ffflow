# PPP: product ping-pong plugin

## 1. Problem
Product briefs arrive as one-liners, and engineering answers with plans product can't check. When the
two sides do negotiate a PRD, it bloats into a record of the negotiation, names the people of the day
instead of the roles that last, drifts into estimating, and loses good side ideas or chases them
mid-stream. A first trial run tripled in length, collected 37 "key decisions" and hundreds of
person and schedule references while still converging on substance ([E-01](evidence/01-v0-experiment.md)).
The convergence worked; the discipline didn't.

## 2. Roles
- **Builder seat:** the people who will build the thing; owns feasibility, shape and relative size.
- **Product seat:** the people who own the outcome; owns commitments, service levels and scope.
- **Analyst seat:** answers data requests neutrally.
- **Facilitator:** the plugin; runs turns, checks, retros and findings, and sets status. Never edits the PRD.
- **Portfolio lead:** starts PRDs, accepts splits, takes converged PRDs into planning.
- **Stakeholder:** reads PRDs and summaries without taking turns.

## 3. Outcomes and non-goals
**Outcomes**
- A PRD either side can hand to a new engineer or a new account lead and be understood without the
  negotiation that produced it.
- Two parties converge in a bounded number of rounds with every question closed or owned.
- Side ideas are kept, routed, and never derail the PRD in hand.
- The same process runs whoever holds a seat; nothing in it depends on who that is.
- A converged PRD is ready for a planning step with no reformatting (for example fff's
  `plan-roadmap` / `plan-chat`).

**Non-goals:** scheduling, capacity planning and estimation (they belong to the planning step);
prescribing the collaboration medium (agreed per PRD); replacing human sign-off.

## 4. Journeys
**Portfolio lead**
1. Starts a portfolio: drops source material into shared inputs, lists the roles, lists the real people
   named in the inputs so the check can keep them out.
2. Starts a PRD from a charter, names who holds each seat, and agrees the medium: points to a medium
   document or accepts the worked example.
3. Reads the portfolio status: what's converged, what's ratified, what's parked as planning, which
   splits exist, which routed ideas have no PRD yet.
4. Hands a converged PRD and its planning items to the planning step.

**Builder or product seat**
1. Opens the bundle and reads everything, including the other seat's memo and the latest round summary.
2. Responds point by point, revises the PRD in place, parks what doesn't belong, asks for data.
3. Runs the check; fixes what it flags; the turn lands only when it passes.
4. Answers the retro questions on the record at the end of the round, and every finding addressed to it in its next memo.
5. Hands the PRD back unchanged when it would sign it as it stands; once converged, signs off yes or no.

**Analyst seat**
1. Picks up open data requests and answers each with a repeatable method, without a position.

**Stakeholder**
1. Reads the PRD and round summaries wherever the medium makes them readable.

## 5. Requirements
| ID | Requirement (testable) | Journey step |
|---|---|---|
| R-1 | A PRD bundle holds exactly: PRD, parking lot, evidence, round summaries, turn memos, state and the medium record | Lead 2 |
| R-2 | The PRD uses the fixed headings in the template and no others | Seat 2 |
| R-3 | Every seat and every PPP skill can read and write every document in the bundle, through the agreed medium, at every turn | Seat 1 |
| R-4 | A turn is refused when it isn't that seat's turn | Seat 1 |
| R-5 | A turn lands only when the check passes | Seat 3 |
| R-6 | The check fails on: unjustified growth, rostered names, effort or schedule time units outside service parameters and metrics, sizes beyond XL, round references, more than the key-decision limit, malformed or unowned questions, broken evidence links, a missing or malformed parking lot, headings other than the template's, an edited PRD on an agreement turn, removed question rows, unanswered findings | Seat 3 |
| R-7 | The check warns on: the soft size ceiling, sizes outside Increments, soft history phrases, split signals | Seat 3 |
| R-8 | Every turn writes a memo with accepted, pushed back, findings answered, parked, data asked, and growth justification | Seat 2 |
| R-9 | Parking-lot entries carry one of four kinds: idea, planning, other-prd, split | Seat 2 |
| R-10 | Either seat can file a data request; the analyst's answer is a file with question, method, result, as-of and caveats | Analyst 1 |
| R-11 | Every round ends with the five retro questions answered by each seat and a shared summary | Seat 4 |
| R-12 | A seat agrees by handing the PRD back unchanged apart from trailing whitespace and line endings; any change is a normal turn and hands it back | Seat 5 |
| R-13 | Sign-off is yes or no; a condition is a change, made in another turn | Seat 5 |
| R-14 | A split moves every affected requirement, question and parked entry to the child; nothing is duplicated or lost | Lead 3 |
| R-15 | Every seat follows one evidence rule: each decision cites a bundle file, and a value with no evidence or authority is tagged provisional | Seat 2 |
| R-16 | Status distinguishes drafting, converged (an agreement turn, zero open, check clean, every finding answered) and ratified (converged, every seat signed off yes, nothing provisional, the medium's commit act done); only the facilitator sets it | Lead 3 |
| R-17 | Portfolio status lists every planning entry across all PRDs and every routed idea with no PRD | Lead 3 |
| R-18 | Skills read, write and hand off as the bundle's medium record says; the check runs on a local copy whatever the medium | Seat 1 |
| R-19 | Every skill is idempotent and resumes from state on disk | Seat 1 |
| R-20 | A converged PRD is valid input to a planning step without edits | Lead 4 |
| R-21 | Starting a PRD accepts a pointer to a medium document and records its instructions as the medium record; with none given, the worked example is offered and confirmed | Lead 2 |
| R-22 | The facilitator writes what a retro surfaces as numbered findings with an owner seat in the round summary, never in the PRD; the owner's next memo accepts or rejects each by ID | Seat 4 |
| R-23 | Closed questions keep their rows and IDs; an answered question's resolution only points, in at most 15 words, to the requirement or section holding the answer | Seat 2 |
| R-24 | Clearing a provisional value names, in the memo, the evidence file or the role whose authority settles it | Seat 2 |

## 6. Service parameters
| Parameter | Unit | Calculation | Default · configurable by | Measured by | At risk / at breach |
|---|---|---|---|---|---|
| Round cap | rounds | a round = one turn per seat + retro | 3 · per portfolio | state | at the cap: lead decides split, park or another round |
| Soft size ceiling | words in the PRD | word count of the PRD file | 2,500 · per portfolio | check | over: warning + split signal |
| Key-decision limit | decisions | entries in Key decisions | 3 · per portfolio | check | over: fail |
| Memo length | words | word count of the memo | 500 · per portfolio | check | over: warning |
| Retro answer length | words per answer | word count | 150 · per portfolio | retro | over: trimmed in summary |

## 7. Metrics
| Metric | Definition | Source | Baseline | Target |
|---|---|---|---|---|
| Rounds to converge | rounds until an agreement turn with zero open | state | 3 ([E-01](evidence/01-v0-experiment.md)) | ≤ 3 |
| Final size | words in converged PRD | check | 12,657 | ≤ 2,500 |
| Check failures at landing | failed rules on the final PRD | check | hundreds | 0 |
| Provisional at ratification | provisional tags | check | n/a | 0 |
| Parked items routed | parked entries with a kind and destination | parking lots | n/a | 100% |

## 8. Increments
1. **Process kit (S):** process document, templates, seat briefs. Usable by hand today.
2. **Check (M):** the mechanical rules as a tool; unlocks enforced turns.
3. **Turn and retro skills (M):** prd-start, prd-turn, prd-retro, prd-data; unlocks full rounds.
4. **Portfolio (M):** prd-status and prd-split; unlocks many PRDs at once and routing between them.
5. **Worked-example medium (S):** the repo and draft-PR protocol, offered by prd-start; unlocks a
   first real PRD with no new service.
6. **Medium documents (S each, on demand):** published medium documents that prd-start takes as its
   argument; no plugin change needed.

## 9. Risks
- **Rules gamed by paraphrase** ("a couple of weeks" spelled out): the check catches patterns only; the
  reviewing seat still reads, and retro question 4 surfaces unwritten assumptions.
- **A seat sounds more certain than its evidence:** the provisional tag and the converged-versus-ratified
  split keep unsupported values from passing as agreement.
- **Over-strict checks stall turns:** warnings for judgment calls, failures only for the hard rules.

## 10. Key decisions
1. **Seats, not people.** The process defines what a seat owns, never who holds it or how they work.
   Rules out person-specific flows, private channels, and special modes for any kind of participant.
2. **Rules are enforced by the check, not by instruction.** A turn that fails does not land. Rules out
   relying on prompts alone to prevent bloat, names and estimates.
3. **The medium is an agreement, not a mechanism.** The process is defined over text documents; where
   they live and how turns hand off is agreed per PRD and recorded in the bundle. Rules out building
   around any single collaboration tool, and any per-tool plug-in mechanism.

## 11. Open questions
| ID | ? | Question | Raised by | Owner (role) | Status | Resolution |
|---|---|---|---|---|---|---|
| Q-1 | | Which medium is the default? | builder | portfolio lead | answered | → R-21 |
| Q-2 | ? | Should the check detect person names beyond the roster? | builder | builder | open | |
| Q-3 | ? | Does a reviewer seat that reads for paraphrased schedule talk belong in the process, or in retro question 4? | product | portfolio lead | open | |
| Q-4 | | Does ratification need every seat held by a person, or only the product seat? | product | portfolio lead | dropped | Moot: the process never distinguishes who holds a seat; ratification needs every seat's sign-off |
