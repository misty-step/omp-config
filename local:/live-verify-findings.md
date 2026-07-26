# Live Verification Findings — Skill Null-Case Evidence Sweep

**Stage:** live_verify, round 1
**HEAD:** f7f992087a03cb7f6b54429a91a8aa01a12fc296
**Worktree:** clean before and after

## AC1: Every global skill classified

**Surface:** `global/skill-catalog.json` + `bin/check` (gate function `check_skill_catalog`)

**Evidence:**
- Catalog contains 39 entries matching 39 skill directories in `global/skills/`.
- Classifications used: "evidence-backed workflow" (3: code-review, groom, research), "narrow live operations contract" (7: estate-infrastructure, factory-apps, herdr-fleet-ops, mint, overmind-feed-post, powder, sprites), "merged guidance" (29: all remaining).
- The gate function (bin/check:283-293) restricts classifications to exactly these three values; any other string triggers `fail()`.
- `test_real_catalog_passes_the_real_gate` confirms parity between catalog keys and disk directories against the real tree.
- `test_bin_check_passes_and_rejects_a_corrupt_catalog` confirms end-to-end enforcement.

**Verdict: PASS**

## AC2: Workflow skills beat no-skill baseline with Crucible evidence and disclosed limits

**Surface:** `global/skill-catalog.json` evidence blocks + gate enforcement in `bin/check:297-309`

**Evidence:**
- `code-review`: report=`~/Development/crucible/runs/local/skill-null-sweep/report.md`, fixtures=3, trials_per_cell=1, verdict=keep, limits="One worker trial per arm and one grader family; proxy result is unanchored."
- `groom`: report=(same), fixtures=2, trials_per_cell=1, verdict=keep, limits="Two fixtures only, one worker trial per arm, and one grader family; proxy result is unanchored."
- `research`: report=(same), fixtures=3, trials_per_cell=1, verdict=keep, limits="Three fixtures, one worker trial per arm, one grader family, and a fixture rubric defect; proxy result is unanchored."
- Gate enforces: fixtures ≥ 2, trials_per_cell ≥ 1, verdict == "keep", non-empty limits, report path containing "crucible". Non-workflow entries with evidence are rejected.
- Tests defend: too few fixtures, missing evidence, wrong verdict, missing limits, invalid trials, non-Crucible report.

**Verdict: PASS**

## AC3: Duplicate copies removed, one authority

**Surface:** `bin/check` SHA-256 tripwire (lines 313-336) + `global/external/registry.yaml`

**Evidence:**
- Gate computes SHA-256 of every first-party `SKILL.md` in `global/skills/` and every external `SKILL.md` in `global/external/`; byte-exact duplicates trigger `fail()`.
- `bin/check` passed (exit 0) — no byte-exact duplicates found.
- `test_duplicate_payload_between_tiers_is_rejected` defends the tripwire.
- External skills are vendored from pinned SHA sources via `registry.yaml` (370 lines, multiple sources) with `.sync-meta.json` receipts. Each source has `alias_prefix` to avoid naming collisions.
- First-party skills live exclusively under `global/skills/`, governed by the single `skill-catalog.json` authority.
- No first-party copies appear duplicated under `global/external/`.

**Verdict: PASS**

## AC4: Installed catalog and all presets pass omp-config source and installed gates

**Surface:** `python3 bin/check` (source gate) + `python3 bin/check --installed` (installed gate)

**Evidence:**
- Source gate: `OMP source configuration OK` — exit 0.
- Installed gate: `OMP source/projection configuration OK (14 symlinks and digests verified)` — exit 0.
- Preset validation inside `check_presets()`: each preset YAML (`design.yml`, `ops.yml`, `research.yml`) is validated via `omp config list --json` with the preset overlay applied; skill names in includeSkills/ignoredSkills are verified against `global/skills/` directories. All three presets pass.
- `test_preset_naming_a_missing_skill_is_rejected` and `test_bin_check_rejects_a_preset_naming_a_missing_skill` defend the preset missing-skill rule.
- CI workflow `.github/workflows/omp-config.yml` runs: skill-catalog tests → omp-config source gate → omp-config installed gate in sequence.

**Verdict: PASS**

## Test suite

- `python3 -m unittest tests/test_skill_catalog.py -v`: **18/18 tests passed** (OK).

## Summary

| AC | Surface | Verdict |
|----|---------|---------|
| 1 | skill-catalog.json + gate | PASS |
| 2 | Crucible evidence blocks + gate | PASS |
| 3 | Duplicate tripwire + registry | PASS |
| 4 | source + installed gates | PASS |

All acceptance criteria pass. Worktree unchanged.
