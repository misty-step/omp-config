---
disable-model-invocation: true
name: deliver
description: |
  Deliver one routed ticket end to end. Make the contract executable, build
  the smallest coherent change, prove the live outcome, review it, and leave
  it merge-ready or ship when explicitly asked. Trigger: /deliver.
argument-hint: "[ticket|description]"

---

# /deliver

Read `../deliver-core/SKILL.md` before starting.
That linked skill is the canonical delivery contract.
This adapter keeps OMP's composer, route, review, gate, and Powder closeout surfaces local.


## OMP composition

`/deliver` composes one routed work card from intent through durable proof.
Specialist skills own shaping, verification, review, CI, and closeout.
Keep the OMP `/dispatch` runtime local.
Do not move its composition or recipe behavior into the canonical core.


| Signal | Route |
|---|---|
| Goal, acceptance, or tradeoff is unresolved | `curator` with `/groom` |
| External facts would change the design | `magellan` with `/research` |
| Product identity or long-lived direction is unsettled | `curator` with `/vision` |
| Running behavior needs proof | `qa` |
| Non-trivial diff needs fresh-context judgment | `reviewer` |
| The repository gate is absent, weak, or red | `/ci` |
| Independent heavy lanes materially shorten the critical path | `/sprites` |
| Delivery exposed a reusable repo-technical lesson | `/compound` after proof |

Route only when the corresponding OMP oracle is needed.
For disputed proof loops, load `global/references/verification-system-first.md`.
For public API, CLI, UI, performance, compatibility, migration, or operator-workflow changes, load `global/references/works-critique.md` before pre-ship review.


## OMP prove and closeout

Apply the canonical core's live-card, falsifier, clean-cutover, live-driver,
review, and exact-proof requirements.
OMP then:

- dispatches `qa` against the live surface and retains its reviewable evidence;
- dispatches a fresh-context `reviewer` with the diff and oracle, resolves
  blocking findings, and re-proves affected behavior;
- runs `/ci` after live behavior works and keeps its gate disposition;
- reconciles the routed Powder card with exact proof links or commands,
  including deviation ledger, review and gate dispositions, and residual risk;
- commits by concern and pushes when the OMP workflow requires it.
  Stop at merge-ready unless the operator explicitly asks for merge or deploy.


OMP's shared operating spine and global references remain authoritative:
`global/AGENTS.md`, `global/references/verification-system-first.md`, and
`global/references/works-critique.md`.
