# E-01: what the first simulated ping-pong produced

**Question:** what happens when two blind agents negotiate a PRD with only a loose protocol? (builder)
**Method:** three rounds on a client-request pipeline PRD; after every turn a small measurement
script recorded the PRD's word count, open questions, key decisions and churn against the previous
version; the final PRD was run through `prd-check`.
**Result:**

| Measure | First draft | Final |
|---|---|---|
| Words | 4,463 | 12,657 |
| Open questions | 19 | 0 |
| Key decisions | — | 37 |
| Person names (prd-check) | — | 236 hits |
| Effort/schedule time units (prd-check) | — | 77 hits |
| Churn vs previous turn | — | 64% → 11% |

Converged in three rounds with product sign-off "yes with conditions". Evidence (real request counts,
a branch-protection check) moved positions; argument did not. The candid content appeared in private
interviews, not in the PRD.
**As of:** the end of the v0 experiment.
**Caveats:** one PRD, one run; the product seat was an agent guessing at real people.
