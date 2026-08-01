# Design audit assessment — omp-config design-skill stack

- Date started: 2026-07-30
- Audited surfaces: `global/skills/{design,improve-ui,baseline-ui,image-gen,qa-users,dispatch}`
- Entrypoints exercised: N/A — the audited product is a markdown skill stack with no rendered surface
- Target state: `global/skills/design-audit/references/design-md-contract.md` (this change)
- Target-state scan: not external — authored in-repo from primary sources (designmd.sh/docs, stitch.withgoogle.com DESIGN.md specification, mobbin.com/mcp, cuelume.dev, cuelume.dev/agents.md)
- Named references consulted: designmd.sh — registry trust model — external DESIGN.md files are dependencies, scan before use; Cuelume — agents.md — restrained semantic cues, mute/volume, no autoplay, one attribute per behavior; Mobbin — MCP — shipped-product screens as named references

## Findings

| # | Phase | Surface | Problem | Evidence | Governing rule | Correction | Decision | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | source | design, improve-ui | `DESIGN.md` read and updated with no content contract; no section requirements anywhere in the stack | design/SKILL.md pin-the-brief and closing lines; improve-ui/SKILL.md §2 | Contract: required sections | Point both skills at `design-md-contract.md`; keep `DESIGN.md` complete against it | accepted | verified |
| 2 | source | whole stack | No interaction-sound doctrine; only rule was "avoid autoplaying media with sound" | grep sound/audio/autoplay/mute across the 6 stack skills → baseline-ui Sound section | Contract: Sound rules | Add `## Sound` section to baseline-ui per Cuelume doctrine | accepted | verified |
| 3 | source | design, improve-ui | External or imported `DESIGN.md` treated as trusted authority without a scan | design/SKILL.md §1; improve-ui/SKILL.md §2 | Contract: untrusted-dependency scan | Add scan-first sentences pointing at the contract | accepted | verified |
| 4 | source | whole stack | No shipped-product reference source; no Mobbin, designmd, or cuelume mention anywhere in `global/` | grep Mobbin/mobbin/designmd/cuelume across `global/` → zero hits | Contract: named visual references | Contract's Named visual references section routes through Mobbin MCP or operator-named products | accepted | verified |
| 5 | source | design §5, dispatch routing | No route to a whole-product audit-assess-remediate program; routing topped out at single-surface `improve-ui` | design/SKILL.md §5; primitive-routing.md skill routes | Skill ownership | Add `design-audit` routing line to design §5 and one skill-route row to dispatch | accepted | verified |
| 6 | rendered | N/A | No rendered surface exists for a markdown skill stack | — | — | — | N/A | N/A |

Preserved strengths (no finding): design's Not-list already rejects purple-gradient SaaS and generic defaults; baseline-ui already bans purple and multicolor gradients; image-gen already blocks raster mockups from shipping as UI.

## Evidence index

- `global/skills/design/SKILL.md` — §1 scan sentence, §5 routing line, closing contract sentence
- `global/skills/improve-ui/SKILL.md` — §2 scan sentence
- `global/skills/baseline-ui/SKILL.md` — `## Sound` section
- `global/skills/dispatch/references/primitive-routing.md` — `design-audit` skill-route row
- `global/skills/design-audit/` — SKILL.md plus two references (new)

## Remediation record

| # | Change | Files | Landed change id | Evidence |
|---|---|---|---|---|
| 1,3 | Contract pointers and untrusted scan | design/SKILL.md, improve-ui/SKILL.md | this jj change | evidence index above |
| 2 | Sound section | baseline-ui/SKILL.md | this jj change | evidence index above |
| 4 | Reference-source doctrine | design-audit/references/design-md-contract.md | this jj change | evidence index above |
| 5 | Program route | design/SKILL.md, dispatch/references/primitive-routing.md | this jj change | evidence index above |

## Remaining

None. Verification for this document-stack audit: `bin/check` pass plus `tests/test_skill_ownership.py`.
