# Skill Design Principles

Apply this when `/harness-engineering` improves first-party skills, creates a
new skill, or audits the catalog after external skill-system research.

Source prompt: Anthropic's "Lessons from building Claude Code: How we use
skills" (2026-06-03).
omp-config adapted it to the filesystem-first contract.

## Translate External Principles

| Principle | omp-config rule |
|---|---|
| Skill is a folder | Prefer `references/`, `scripts/`, `examples/`, `assets/`, `templates/`, and `evals/` over long inline prose. |
| Clean category | Each skill owns one workflow category; multi-category skills compose other skills or split. |
| Verification skills matter | Verification behavior gets a real system: driver, grader, evidence packet, and cadence before extra prose. |
| Do not state the obvious | Delete generic SWE advice unless it names an omp-config-specific failure mode. |
| Gotchas carry signal | Add gotchas from observed failures, receipts, audits, or failing gates; avoid speculative warnings. |
| Progressive disclosure | `SKILL.md` routes; references hold depth; scripts and assets hold repeatable mechanics. |
| Avoid railroading | Give constraints, choices, and oracles; do not force one procedure when repo evidence should choose. |
| Description is trigger classifier | Frontmatter must include concrete `Use when:` phrases plus `Trigger:` aliases. |
| Help the skill remember | Repeated workflows may use append-only JSONL, ledgers, or invocation data under approved state roots. |
| Store scripts | If the model would rebuild boilerplate twice, add a helper script or template. |
| On-demand hooks | Use skill-active hooks only for bounded, high-friction guardrails that would be annoying globally. |
| Distribution matters | Global first-party skills are default; repo-local skills are for substantial repo-specific context. |
| Compose explicitly | Name the owner skill instead of copying its method. |
| Measure | Use invocation and work-ledger data to find hot, cold, undertriggering, stale, and overlapping skills. |

## Skill-Prose Compression

Authoring rules live in `global/references/skill-authoring-standard.md`.
Keep this file for harness-specific catalog gates and upgrade-loop mechanics.

- **Leading words.** A pretrained token helps the agent think.
  (*ratchet*, *mundane harvest*, *plausible-but-wrong*, *unknown unknowns*)
  anchors behavior in few tokens.
  It also acts as an invocation hook when it recurs in descriptions and
  prompts.
  Use the Upgrade Loop to find restatements such as "fast, deterministic,
  low-overhead" that collapse into one word (*tight*).
  You get fewer tokens and a sharper behavioral hook.
- **No-op test, per sentence.** Ask whether each sentence changes behavior
  versus the model's default.
  If not, delete it instead of trimming it.
  This is the per-sentence form of the standing gotcha: each new frontier model
  can turn judgment prose into railroading.
- **Premature completion.** This named failure makes the oracle doctrine
  important.
  Attention slips to *being done* before the completion criterion is met.
  First sharpen the criterion so it is checkable and exhaustive.
  Split the sequence only when you observe the rush.
- **Invocation cost accounting.** Every model-facing description pays context
  load in every session.
  A skill fired only by hand can drop its model-facing description with
  `disable-model-invocation: true` (or `hide: true`).
  Telemetry (`/groom audit`) names the candidates.

## Upgrade Loop

1. Classify the target skill's single primary category.
2. Read live usage, recent receipts, active backlog, and failure evidence when
   available.
3. Delete generic instructions that the model already knows.
4. Move detail into references, scripts, assets, or templates when it repeats.
5. Tighten description triggers and aliases before you change body prose.
6. Convert each repeated gotcha into a script, hook, eval, or gate when
   feasible.
   Use `../../../shared/references/verification-system-first.md` for eval,
   benchmark, QA, or smoke-path design.
7. Run `bin/check` and the full repo gate before shipment.

## New Skill: Eval Scaffold Is Not Optional

Every new first-party skill ships with eval coverage or an explicit waiver.
Ship it in the first commit, not as a follow-up.
`bin/check` verifies referenced paths.
Review the eval's behavioral claim and run it through `/skill-eval`.
Do not reduce the eval to a structural string-matching gate.

When scaffolding a new skill:

1. Copy `../../skill-eval/templates/eval-spec.md` to
   `global/skills/<name>/evals/<name>-eval.md`.
   Fill in the one claim the skill must earn, 2–3 fixtures, objective checks,
   and a pass condition.
   The run may not have happened yet.
   See `global/skills/dispatch/evals/dispatch-eval.md` for a current instance.
2. If the skill's claim genuinely cannot be evaluated yet, write
   `global/skills/<name>/evals/WAIVER.md`.
   Reasons include an external live dependency, a taste-heavy rubric that
   needs a human anchor, or no fixture budget yet.
   Include a reason and an `expires: YYYY-MM-DD` line.
   See any file under `global/skills/*/evals/WAIVER.md` for the expected shape.
   A waiver is a time-boxed deferral, not a permanent opt-out.
   An expired waiver fails the gate like a missing eval.
3. Never satisfy the gate with an empty or placeholder eval file.
   An honest waiver is better.
   A placeholder looks covered to `/harness-engineering` health audits and
   telemetry-driven pruning.

## Catalog-Wide Application

Start with machine-checkable hygiene before subjective rewrites:

- no missing `Trigger:` definitions;
- no trigger collisions;
- no stale local references in routes or examples;
- no skill over 500 lines without progressive disclosure;
- no substantial workflow skill without the shared operating-spine floor
  pointer;
- no generated docs/index drift after a skill change.

Then spend attention on taste:
category fit, gotcha quality, excess prose, and whether a workflow should split,
merge, or compose.
