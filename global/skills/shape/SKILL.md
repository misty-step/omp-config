---
name: shape
description: |
  Shape an unresolved idea into a decision and executable context packet.
  Use when: "shape this", "write a spec", "design this feature", "plan this",
  "spec out", "context packet", "technical design".
  Trigger: /shape, /spec, /plan, /cp.
argument-hint: "[idea|ticket] [--spec-only|--design-only]"
---

# /shape

Turn an unresolved idea into the decision contract `/deliver` can execute.
Specify the outcome, boundaries, and proof; leave routine implementation
decomposition to the builder.

## Ready contract

A shape is ready only when:

- **The premise survived challenge.** Name the underlying user or operator
  outcome; the requested mechanism is only one candidate.
- **Live evidence anchors it.** Cite the load-bearing code, tests, contracts,
  prior decisions, and relevant repo learnings. Subagent summaries may widen
  coverage but do not replace direct reads of the execution seam.
- **Direction is settled.** For product identity or long-lived direction, read
  root `VISION.md`; route missing or stale direction to `/vision`.
- **The choice is real.** When the design is contestable, compare the boring
  path and alternatives that fail differently, reject the losers, and recommend
  one. A menu is not a decision.
- **Taste is made visible.** For layout, copy, feel, or other perceptual
  acceptance, route to `/design` for artifacts the operator can react to;
  prose cannot settle an unseen interface.
- **Scope is fenced.** State the outcome, explicit non-goals, and invariants
  that must survive.
- **The oracle is executable.** Name exact commands, routes, observations, or
  acceptance artifacts plus a falsifier. Pin mutable fixtures or goldens by
  digest when they carry the contract.
- **The proof loop exists.** Name driver, grader, evidence packet, cadence, and
  gaps. If the running outcome needs a driver and the repo has none, building
  it becomes the first milestone.
- **A stranger can execute it.** Include the surprising current state, 3–10
  repo anchors, one convention exemplar, and stop conditions. No hidden chat
  context or “decide during implementation” placeholders.
- **The premise source is durable.** Cite `sha256:<digest> <path-or-url>` or an
  explicit waiver with residual risk.

Resolve facts from the repo and tools. Ask the operator only for a product or
architecture decision the evidence cannot settle, batched with a
recommendation and the cost of being wrong for each. For a substantial
unknown, load `primitives/shared/references/interrogate-first.md` (batching
doctrine); do not manufacture an interview when the evidence already decides
the branch.

## Context packet

Sections carry weight or they do not appear. A one-file fix may need a short
packet; a public interface or architecture choice needs the full contract.

```markdown
# Context Packet: <title>

## Outcome         — one sentence, not a mechanism
## Deliverable     — code, research, docs, or decision
## Non-Goals       — tempting scope that stays out
## Invariants      — behavior that must survive
## Repo Anchors    — 3–10 files and one convention exemplar
## Alternatives    — how credible options fail; chosen verdict
## Design          — chosen surfaces and data/control flow
## Oracle          — claim, falsifier, driver, grader, evidence
## Premise Source  — digest + artifact, or explicit waiver
## Risks + Rollout — failure, rollback, stop conditions
```

For substantial product work, load `references/prd-ticket-quality.md`; for CLI
surfaces, `references/cli-design.md`; for disputed proof loops,
`primitives/shared/references/verification-system-first.md`; for public API,
UI, performance, compatibility, migration, or operator workflow,
`primitives/shared/references/works-critique.md`.

## Render and critique

Non-trivial or contestable shapes become a standalone HTML plan using
`templates/html-plan.html`: publish through `/artifact`, slug it with the
Powder card ID, attach the URL to the card, verify it is reachable, and inspect
the rendered page without auto-opening it. Lead with the decisions the operator
is most likely to change; use visual structure for tradeoffs, flow, risk, and
proof rather than wrapping prose in HTML. Trivial work or an explicit waiver
may stay text-only.

When the choice is contestable, give fresh-context critics the packet and
oracle only (Shared Operating Spine: `Prove`) and ask which production failure
the shape missed. Resolve blockers before marking the card ready. Delegate per
the Shared Operating Spine (`Act`).

## Completion Gate

Apply the Shared Operating Spine (`Prove`; `Durable State and Closeout`). Add:

- chosen design and rejected alternatives;
- exact executable oracle and retained packet;
- source digest or waiver;
- critic dispositions; and
- Powder card promoted only when dependencies and proof are executable.

## Gotchas

- **Mechanism lock-in:** shaping the requested feature instead of the outcome
  preserves the first framing, not the best decision.
- **Over-specced how:** pseudocode and micro-task lists transfer design errors
  to the builder. Keep interfaces, invariants, and stop conditions.
- **Ready-but-vague:** “preferably,” “later,” or “decide during implementation”
  on a load-bearing choice means the packet is not ready.
- **Decorative artifact:** a plan page dependent on chat context is not a
  stranger-executable contract.
