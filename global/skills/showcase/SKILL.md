---
disable-model-invocation: true
name: showcase
description: |
  Turn a working repo into credible external-facing proof.
  Use a demoability audit, deterministic demo path, marketing site, case study,
  screenshots, demo video, launch copy, and consulting portfolio assets.
  Use when: "productize this",
  "make this demoable", "make this polished", "make a marketing site",
  "show this off", "demo video", "case study", "portfolio piece",
  "consulting asset", "launch page", "sales demo". Trigger: /showcase,
  /productize, /demoability.
argument-hint: "[audit|plan|site|video|case-study|polish] [repo-or-product]"
---

# /showcase

Make a real product showable without giving weak product truth a false appearance of proof.

This skill closes the gap between local success and external trust.
It serves serious buyers, clients, collaborators, and prospects.
It is not a marketing checklist. The primitive is **showable proof**:
a deterministic demo surface, an evidence-backed story, polished product
moments, and assets that make the operator credible.

## Route

| Need | Load |
|---|---|
| Decide if the repo is demoable yet | `references/demoability-audit.md` |
| Position for consulting or portfolio use | `references/consulting-positioning.md` |
| Plan a marketing site or launch page | `references/launch-page-contract.md` |
| Script or verify a demo video | `references/demo-video-contract.md` |
| Keep external copy tied to real proof | `references/evidence-gate.md` |
| Write a reusable execution plan | `templates/showcase-plan.md` |
| Draft a landing page outline | `templates/landing-page-outline.md` |
| Draft a demo video script | `templates/demo-script.md` |
| Draft a case study | `templates/case-study.md` |

Use `curator` with `/groom` when product direction is unsettled.
Use `/design` for visible artifact critique or implementation polish.
Dispatch `qa` for live surface verification.
Dispatch `builder` to build the groomed slice.
This skill decides which showcase work is worth doing and what proof must exist
before it becomes public.

## Contract

- Product truth first. If the product cannot produce a believable live or replayed demo, build that before copy, brand, or video.
- One-command demo path. A showpiece needs a command, route, fixture, or seed/reset flow that recreates the visible state and writes evidence.
- Evidence-backed story. Map every public assertion to a route, command, screenshot, video frame, CI run, dogfood packet, customer example, or explicit "vision" label.
- Consulting lens. Assets should prove taste, technical judgment, operator empathy, and ability to turn ambiguous AI systems into working software.
- Demo mode is honest. Synthetic data may be used, but it must preserve the product's real constraints and failure modes.
- **Polish follows proof.** Do not build a polished interface around unverified behavior. Make the product moment credible first.
- External copy has no agent-process leakage. Remove closeout prose, caveat scaffolding, implementation apology, and "if published" meta-copy.
- Keep the operator in the loop for positioning choices that affect the consulting offer, target buyer, pricing implication, or public claim.

## Output Shapes

**Audit**: rank gaps as `proof gap / demo gap / polish gap / story gap`. Name the smallest next slice and its verification path.

**Plan**: produce a `showcase-plan.md` packet with audience, offer, demo scenario, asset list, gates, non-goals, and first deliverable.

**Build**: create shaped tickets for a demo harness, product polish, site, video, or case study. Keep each slice independently verifiable.

**Review**: run an adversarial pass over public assets. Ask which action or question from a prospect could expose a failure.

## Delegation Judgment

Delegate per the Shared Operating Spine (`Act`).

Useful lanes:

- Product critic: find the weakest public promise.
- Demo verifier: run the demo path cold and report where trust breaks.
- Design critic: inspect screenshots, site, and video frames for hierarchy, taste, accessibility, and generic AI tells.
- Copy critic: remove hype, process leakage, and unsupported assertions.

Critics get the artifact and oracle only — never the author's reasoning trail
(Shared Operating Spine: `Prove`); here the artifact includes the evidence map.

## Gotchas

- **Polished false claims are worse than plain true weakness.** If proof is weak, fix the proof.
- A feature tour does not show value. Show one consequential job from start to finish.
- AI-powered alone does not distinguish a product. Say what changes for the operator.
- Fake data can destroy trust when it avoids the hard edge the product exists to handle. Seed the hard edge.
- Screenshots taken after manual interaction are not a demo harness. Capture the reproduction command or route.
- Demo videos become stale. Pin the commit, command, fixture, viewport, and generated artifacts.
- Portfolio assets are sales assets. They must answer "why hire this operator?" without sounding like a resume.

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
