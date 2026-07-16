# Project engineering profile

<!--
This file declares applicability and points to repo-owned truth. It does not
prescribe directory layout or repeat the methods owned by /ci, /qa,
/eval-design, /factory-apps, codebase-design, or shared references.

State is one of: applicable | not-applicable | waived.
Use `gap: <durable pointer>` when an applicable surface is missing.
-->

## Identity

| Field | Declaration |
|---|---|
| Project | `<name>` |
| Kind | `<runtime application | library | CLI | model workload | website | support repo | mixed>` |
| Profile owner | `<team or role>` |
| Reviewed | `<YYYY-MM-DD>` |

## Proof map

| Proof class | State | Driver / grader | Evidence pointer |
|---|---|---|---|
| Declaration | `applicable` | `<this profile and owning policy>` | `<profile/policy path>` |
| Deterministic gate | `<state>` | `<fast/full command>` | `<reports>` |
| Live probe | `<state>` | `<CLI/browser/API/consumer/runtime/restore driver>` | `<receipt>` |
| Capability eval | `<state>` | `<held-out task + grader>` | `<report/receipt or reason>` |
| Fresh judgment | `<state>` | `<artifact + fresh critic>` | `<report/receipt or reason>` |

## Fitness function

| Obligation | State | Authority / command / evidence pointer |
|---|---|---|
| Fast gate | `<state>` | `<repo-owned command; report path>` |
| Full gate | `<state>` | `<repo-owned command; report path>` |
| Architecture policy | `<state>` | `<policy path; allowed dependency directions>` |
| Unit tests | `<state>` | `<driver; evidence path or reason>` |
| Integration tests | `<state>` | `<driver; evidence path or reason>` |
| End-to-end tests | `<state>` | `<driver; evidence path or reason>` |
| Changed-line coverage | `<state>` | `<threshold/ratchet policy; report path>` |
| Coverage non-regression | `<state>` | `<baseline policy; report path>` |
| Mutation testing | `<state>` | `<command/threshold; survivor report>` |
| Supply chain | `<state>` | `<profile/policy; evidence path>` |

## Factory and operations

| Obligation | State | Authority / service / evidence pointer |
|---|---|---|
| Canary | `<state>` | `<mode; live service identity; probe/readback>` |
| Work ledger | `<state>` | `<provider; project/repo identity; live query evidence>` |
| Landmark / release | `<state>` | `<mode; manifest/workflow/evidence or reason>` |
| Performance | `<state>` | `<budget/benchmark policy; report path>` |
| Accessibility | `<state>` | `<standard/driver; report path>` |
| Backup and restore | `<state>` | `<policy/driver; restore evidence>` |
| Data lifecycle | `<state>` | `<classification/retention/deletion policy; evidence>` |

## Capability evals and fresh judgment

Add one row per real decision or seam. If none exist, keep one
`not-applicable` row and give the project-specific reason.

| Decision or seam | State | Task/artifact | Grader/critic | Evidence pointer |
|---|---|---|---|---|
| `<decision or architecture seam, or none>` | `<state>` | `<fresh task, reviewed artifact, or reason>` | `<grader, fresh critic, or none>` | `<report/receipt or reason>` |

## Waivers

| Obligation | Owner | Reason | Current evidence | Review date | Expiry |
|---|---|---|---|---|---|
| `<obligation>` | `<person or role>` | `<project-specific reason>` | `<path/URL/receipt>` | `<YYYY-MM-DD>` | `<YYYY-MM-DD>` |
