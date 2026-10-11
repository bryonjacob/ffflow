# Medium: ppp

Agreed by every seat when this PRD started. Every PPP skill reads this first and follows it.

## Reference
worked example: repo + draft PR (`ppp/media.md` §A worked example), applied to the ffflow-plugin
repo with the bundle root at `ppp/docs/prds/`.

## Seat holders
| Seat | Held by | Reached by |
|---|---|---|
| builder | <to be filled by the portfolio lead> | draft PR comment mention |
| product | <to be filled by the portfolio lead> | draft PR comment mention |
| analyst | <to be filled by the portfolio lead> | draft PR comment mention |

## Where the documents live
| Part | Location |
|---|---|
| PRD | `ppp/docs/prds/ppp/ppp-prd.md` on branch `prd/ppp` |
| Parking lot | `ppp/docs/prds/ppp/parking-lot.md` |
| Evidence and requests | `ppp/docs/prds/ppp/evidence/` (`requests.md` is the queue) |
| Round summaries | `ppp/docs/prds/ppp/rounds/<n>-summary.md` |
| Turn memos | `ppp/docs/prds/ppp/turns/<n>-<seat>.md` |
| State | `ppp/docs/prds/ppp/state.json` |
| Shared (roles, glossary, roster, inputs, limits) | `ppp/docs/prds/_shared/` (not created yet; the check warns that the roster is missing) |

## Reading and writing
Pull branch `prd/ppp`, edit the files in place, commit, push. The repo is local, so `prd-check` runs
on the working tree directly.

## Versions
One commit per turn, `ppp(ppp): round <n> <seat>`. The previous PRD version for `prd-check --prev`
is `git show <previous turn commit>:ppp/docs/prds/ppp/ppp-prd.md`.

## Hand-off
A comment on the draft PR naming the next seat and mentioning its holder. Evidence answers and round
summaries are commits on the same branch, announced the same way.

## Converged, sign-off and commit
Converged: mark the draft PR ready for review and request a review from every seat holder. Sign-off:
approve for `yes` or `yes-with-conditions` (conditions in the review text), request changes for
`no`. Commit: merge to the default branch once every seat has approved and no `[provisional]` is
left.
