---
disable-model-invocation: true
name: foundation
description: |
  Establish everything every project must have: application floor, access faces,
  gates, tests, release, onboarding, and Factory hooks. Always full audit then
  remediate. Hand-only. Trigger: /foundation, /establish-baseline.
argument-hint: "[repo-path]"
---

# /foundation

Bring one repository up to the **every-project floor**. No modes. Every run
scores **every** dimension, then remediates accepted gaps until the gate holds
or each residual has a named waiver.

SSOT for product obligations: `global/references/application-floor.md`.  
SSOT for score rows and severity: `references/foundation-checklist.md`.

## Route

| Need | Load |
|---|---|
| Full scorecard (every dimension) | `references/foundation-checklist.md` |
| Product floor law | `global/references/application-floor.md` |
| Marketing + docs minimum | `references/public-surfaces.md` |
| Landmark / release path | `references/landmark-floor.md` |
| Audit packet shape | `references/audit-packet.md` |
| Gate design | `global/references/quality-gates.md`, `/ci` |
| Live proof design | `global/references/verification-system-first.md` |
| Factory method (Canary, Powder, Landmark) | `/factory-apps` |

Compose with `/document`, `/showcase`, `/vision`, `/ci`, and
`mattpocock-codebase-design` (`global/external/mattpocock-skills/codebase-design/SKILL.md`)
when a gap needs that owner. Stay on this skill for the run.

## Proof

Keep these five classes distinct. Never substitute a weaker class for a stronger
one. A path that exists is only a **declaration**.

1. **Declaration** — applicability, policy path, command name, service identity,
   owner, waiver metadata.
2. **Deterministic gate** — formatting, lint, types, tests, supply chain,
   coverage/mutation thresholds; the command ran and the report exists.
3. **Live probe** — real CLI, browser, API, consumer, runtime, restore, or
   production boundary exercised; receipt required.
4. **Capability eval** — held-out task, fresh model/agent output, grader score.
5. **Fresh judgment** — artifact-only critic for irreducible architecture or
   product judgment.

Use a declaration to route proof. Do not mark `pass` on declaration alone when
the dimension requires a gate, live probe, eval, or judgment.

## Contract

- One repo per run. Default: current checkout.
- **Full front every time.** Score every checklist dimension. Do not sample.
- **Audit before patch.** Write the packet, then remediate.
- **Remediate in the same run** for accepted gaps. File a Powder card only when
  the gap is blocked on secrets, human policy, or multi-PR scope the operator
  defers.
- Prefer the smallest change that closes a dimension.
- `n/a` and `waived` need a project-specific reason. Silence is a gap.
- Incomplete face (including stub MCP) is a gap. Prefer deleting a stub over
  claiming the face.
- Do not require a shared brand-kit package. Pitch and proof still required
  for public products.
- Do not invent paths or commands to green a row. `gap: <card-or-path>` is
  honest; a fake pointer is not.

## Steps

1. **Recon** — Inventory root files, faces (API/CLI/MCP/skill/UI), gates, tests,
   docs/site, release/Landmark, onboarding/doctor, deploy targets, Factory
   hooks, and typing stack.
   Done when every checklist dimension has a candidate path, command, or
   explicit absence.
2. **Score** — Mark each dimension `pass`, `gap`, `n/a`, or `waived` with
   evidence. Run safe probes (help, doctor, gate dry commands, URL checks).
   Done when the packet covers **every** checklist row with evidence or reason.
3. **Remediate** — Close gaps in severity order from the checklist. Use owning
   methods (`/ci`, `/document`, `/showcase`, Landmark, codebase-design) inside
   this run.
   Done when each former gap is `pass`, `waived` with metadata, or deferred on
   a Powder card the operator accepted.
4. **Recheck** — Re-score the full checklist against the tree.
   Done when the completion gate below is filled with evidence.

## Boundaries

- Out of scope: portfolio positioning strategy; optional brand chrome.
- Full remediate is chief/builder work. Architect may score read-only; it does
  not own the foundation run.
- Deep reference IA stays `/document`; this skill still requires a linked docs
  surface.
- Capability evals and fresh-judgment seams: declare and wire when the repo has
  model decisions; otherwise `n/a` with reason — still score the row.

## Completion Gate

Shared Operating Spine (`Prove`; Durable State and Closeout) first. Then:

```markdown
## Foundation Gate
- Packet: every checklist dimension scored with evidence or reason
- Floor: application-floor items 1–9 closed, waived, or deferred on cards
- Faces: API + CLI + MCP + skill + UI cover core verbs (or waiver per face);
  no stub MCP
- Gates: fast + full commands real; CI runs the full gate; no weakened gate
- Tests: unit / integration / e2e applicability proven; HTML surfaces use
  real-engine tiers where applicable
- Release: Landmark (or documented equivalent) path proven, or n/a with reason
- Onboarding: zero-to-running path + doctor (or waiver)
- Typing: Go/Rust default (TS distant third); weaker stack constraint named
- Factory: work ledger + Canary applicability declared with proof or n/a
- Residuals: Powder cards listed with owners; no silent gaps
```
