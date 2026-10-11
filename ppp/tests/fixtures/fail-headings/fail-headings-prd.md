# Request intake

Status: drafting

## 1. Problem
Client requests arrive by email and get lost between account owners. Half of them wait without an
owner ([E-01](evidence/01-requests.md)).

## 2. Roles
- **Account owner:** triages and answers client requests.
- **Client:** raises requests and reads their status.

## 3. Outcomes and non-goals
**Outcomes:** every request has an owner role and a visible status.
**Non-goals:** billing changes.

## 4. Journeys
**Client**
1. Raises a request and sees it acknowledged.

**Account owner**
1. Picks up any unowned request from a shared queue.

## 5. Requirements
| ID | Requirement (testable) | Journey step |
|---|---|---|
| R-1 | Every request is acknowledged within the acknowledgement window | Client 1 |
| R-2 | Any account owner can pick up any unowned request | Owner 1 |

## 6. Service parameters
| Parameter | Unit | Calculation (start · pause · stop · calendar) | Default · configurable by | Measured by | At risk / at breach |
|---|---|---|---|---|---|
| Acknowledgement window | business days | from receipt to first reply; pauses on holidays | 2 business days · per client | queue log | at risk: flagged · at breach: escalated |

## 7. Metrics
| Metric | Definition | Source | Baseline | Target |
|---|---|---|---|---|
| Unowned requests | share of requests with no owner over a 30-day window | queue log | 50% | 5% [provisional] |

## 8. Increments
1. **Shared queue (XL):** one queue for every request; unlocks pickup by any owner.
2. **Status page (XL):** clients see status; unlocks fewer chase emails.
3. **Escalation (M):** breach routing.

## 9. Dangers
- **Queue ignored:** the acknowledgement window makes neglect visible.

## 10. Key decisions
1. **One queue for all clients.** Rules out per-client inboxes.
2. **Status is visible to clients.** Rules out internal-only tracking.

## 11. Open questions
| ID | ? | Question | Raised by | Owner (role) | Status | Resolution |
|---|---|---|---|---|---|---|
| Q-1 | ? | Which channel do clients use to raise requests? | builder | product | open | |
| Q-2 | | Is the window set per client? | product | product | answered | Yes, configurable per client |
| Q-3 | | Should requests close on their own? | builder | account owner | deferred | Revisit when the unowned share meets its target |
| Q-4 | | Should owners rotate? | product | product | dropped | Any owner can pick up any request |

## 12. Appendix
Notes.
