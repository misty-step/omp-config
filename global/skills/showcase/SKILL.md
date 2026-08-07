---
disable-model-invocation: true
name: showcase
description: Turn a working repo into credible external proof. Use when: productize, make demoable, make polished, marketing site, show off, demo video, case study, portfolio, consulting asset, launch page, or sales demo. Trigger: /showcase, /productize, /demoability.
argument-hint: "[audit|plan|site|video|case-study|polish] [repo-or-product]"
---

# /showcase

Make a real product showable without presenting weak product truth as proof.

## Route

| Need | Load |
|---|---|
| Audit | `references/demoability-audit.md` |
| Position | `references/consulting-positioning.md` |
| Launch | `references/launch-page-contract.md` |
| Video | `references/demo-video-contract.md` |
| Evidence | `references/evidence-gate.md` |
| Plan | `templates/showcase-plan.md` |
| Landing | `templates/landing-page-outline.md` |
| Script | `templates/demo-script.md` |
| Case study | `templates/case-study.md` |

Use `designer` with `/groom` for unsettled direction, `/design`
for visible critique, `verifier` with `verify-live` for live verification,
and `builder` for the accepted slice. The chief or operator retains acceptance.

## Contract

- Establish product truth before copy, brand, or video; polish follows proof.
- Provide a one-command demo path: command, route, fixture, or seed/reset flow that recreates visible state and writes evidence.
- Map each public assertion to a route, command, screenshot, video frame, CI run, dogfood packet, customer example, or `groom`/vision label.
- Show taste, technical judgment, operator empathy, and working software from ambiguous AI systems.
- Keep demo mode honest: synthetic data preserves real constraints and failure modes; seed the hard edge.
- Remove agent-process leakage, caveats, apologies, and `if published` text from public copy.
- Keep the operator involved in positioning, buyer, pricing, consulting-offer, and public-claim choices.

## Output shapes

- **Audit:** Rank `proof gap / demo gap / polish gap / story gap`; name the smallest slice and verification path.
- **Plan:** Write `showcase-plan.md` with audience, offer, scenario, assets, gates, non-goals, and first deliverable.
- **Build:** Create independently verifiable tickets for demo harness, polish, site, video, or case study.
- **Review:** Adversarially test public assets against prospect actions and questions.

## Delegation

Delegate through the Shared Operating Spine (`Act`):

- Product critic: weakest public promise.
- Demo verifier: cold demo path and trust breaks.
- Design critic: screenshots, site, and video hierarchy, taste, accessibility, and generic AI signals.
- Copy critic: hype, process leakage, and unsupported assertions.

Give critics only the artifact and oracle, including the evidence map, not the
author's reasoning trail (`Prove`).

## Failure controls

Show one consequential job, not a feature tour. Explain the operator change;
`AI-powered` alone does not distinguish a product. Manual screenshots are not a
harness. Pin commit, command, fixture, viewport, and generated artifacts. Make
portfolio assets answer why a prospect should hire this operator without sounding like a resume.

## Completion Gate

See `global/references/verification-system-first.md` for the shared proof contract.
Showcase adds:

```markdown
## Showcase Gate
- Audience and offer: who this is for, and what action the asset asks for.
- Demo path: exact command, route, fixture, seed/reset flow, or waiver.
- Proof artifacts: screenshots, video, logs, CI, dogfood, release, or case-study evidence.
- Evidence map: each public assertion mapped to proof or labeled as vision.
- Product polish: visible product moment inspected, not just marketing wrapper.
- Design/copy review: artifact-backed critique result and unresolved findings.
- Fresh verifier: cold run or adversarial review result.
- Public risk: what a prospect could click, ask, or run that would still fail.
```
