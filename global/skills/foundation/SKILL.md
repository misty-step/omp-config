---
disable-model-invocation: true
name: foundation
description: |
  Audit, plan, and remediate a repo's public and agent foundation: core files,
  marketing site, docs site, README proof assets, and Landmark release
  automation. Hand-only. Trigger: /foundation, /establish-baseline.
argument-hint: "[audit|plan|remediate|check] [repo-path]"
---

# /foundation

Establish a checkable product foundation for one repository. Ignore Misty Step
aesthetic chrome and DESIGN.md brand-kit adoption. Focus on truth, proof, and
release machinery.

Structural skill shape follows `/writing-for-agents` (projected
`mattpocock-writing-for-agents`).

## Route

| Need | Load |
|---|---|
| Checklist dimensions, severity, and pass rules | `references/foundation-checklist.md` |
| Marketing + docs site minimum contract | `references/public-surfaces.md` |
| Landmark versioning, notes, changelog, CI | `references/landmark-floor.md` |
| Audit packet shape | `references/audit-packet.md` |

Compose with `/document` for reference docs, `/showcase` for public proof
assets, `/factory-apps` → Landmark for release intelligence, and `/vision` when
`VISION.md` is missing or stale.

## Contract

- Work one repo at a time. Default to the current checkout.
- Produce an audit packet before remediation. Do not polish without a gap list.
- Remediate only accepted gaps. Prefer the smallest change that closes a check.
- Map every public claim to a file, route, screenshot, GIF, or Landmark artifact.
- Require Landmark integration for automated versioning, release notes, and
  changelogs when the repo ships versions.
- Do not require Aesthetic tokens, house CSS, or DESIGN.md brand adoption.
- Keep `disable-model-invocation` skills hand-fired; do not invent auto loops.

## Steps

1. **Recon** — Inventory root files, `site/` or public pages, `docs/`, README
   media, Landmark config/workflows, and release history.
   Done when the inventory names every foundation surface that exists or is
   absent.
2. **Audit** — Score each checklist dimension from
   `references/foundation-checklist.md`.
   Done when every dimension is `pass`, `gap`, or `n/a` with evidence paths.
3. **Plan** — Order remediation by user-visible risk, then release risk, then
   docs depth.
   Done when the plan lists ordered cards or patches with an oracle each.
4. **Remediate** — Close accepted gaps only. Use `/document`, `/showcase`, and
   Landmark surfaces instead of one-off invention.
   Done when each accepted gap has proof or an explicit waiver.
5. **Check** — Re-run the checklist against the working tree.
   Done when the completion gate below is filled with evidence.

## Boundaries

- Out of scope: Misty Step aesthetic kit adoption, token rethemes, DESIGN.md as
  brand law, and portfolio positioning strategy beyond a clear product pitch.
- `/showcase` owns demo video and consulting packaging. This skill owns the
  durable foundation those assets stand on.
- `/document` owns deep reference IA. This skill requires a public or committed
  docs surface and links it from README/marketing.
- Do not mark Landmark done from memory. Use `landmark describe --json` or the
  live workflow evidence named in `references/landmark-floor.md`.

## Completion Gate

Shared Operating Spine (`Prove`; Durable State and Closeout) first. Then:

```markdown
## Foundation Gate
- Core files: VISION.md, README.md present and current; DESIGN.md noted only if
  already present (not required by this skill).
- Pitch: one outsider-legible pitch in README and/or marketing site.
- Proof media: screenshot and/or GIF present in README and/or marketing site,
  or explicit n/a with reason.
- Marketing site: public URL or in-repo site/ with deploy path, or n/a waiver.
- Docs site: committed docs/ or published docs URL linked from README/marketing.
- Landmark: automated versioning + release notes/changelog path proven, or n/a
  for non-releasing repos with reason.
- Gaps closed or waived: list with evidence.
- Follow-ups: Powder cards filed for deferred work, if any.
```
