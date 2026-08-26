# Canon — Misty Step operating philosophy

**Status: reference, not context.** This file states how we build software and
run agents. It is never auto-loaded into agent context, and `./install` does
not ship it. Harness artifacts (`global/AGENTS.md`, `global/RULES.md`,
`skills/*`) are derived views; they change deliberately, citing canon IDs.

Everything here is suggestion and encouragement, including this sentence
(ST-01). Reality outranks the document. Deviations get recorded, not hidden.

## How to use

- Cite IDs (`TE-03`) in ADRs, PR descriptions, review notes, and harness PRs.
- Consult by section, not whole-file: designing → TH, DE; verifying → TE;
  shipping → OP, CH; delegating → OR; adopting tools → CR, TL.
- Synthesis path: canon item → draft rule/skill/AGENTS.md line → trial in one
  project → promote or drop. Record every step in the synthesis ledger below.
- Canon changes via PR like code, rationale required. Two similar recorded
  deviations trigger a principle revision, not a third exception.

## Synthesis policy

Standing context is scarce attention; spend it on judgment, not procedure.

| Surface | Carries | Constraint |
| --- | --- | --- |
| `global/AGENTS.md` | decision policy needed most turns | stays under ~60 lines |
| `global/RULES.md` | strict precedence and ordering only | stays tiny |
| Skills, model-invocable | trigger-shaped procedures with cheap wrong-fire | loaded on demand |
| Skills, operator-only | heavyweight, attention-consuming, broadly mutating flows | explicit invocation |
| Project files (via `foundation`) | stack rules, test portfolio, docs surface, run instructions | per repository |
| `config.yml` | mechanical routing: model roles, search provider, retries | no prose |
| WATCHDOG | second-model closeout review; behavioral prompt prose by design | event-triggered, bounded, outside session context |
| Iron Forest and CI | everything checkable mechanically | gates over prose |

- Prose carries judgment; mechanisms carry enforcement. Never write prose
  enforcing what a gate already enforces.
- A skill is model-invocable iff its trigger is unambiguous, its cost is
  bounded, and firing at the wrong time is cheap. Otherwise operator-invoked.
- One skill name exposes one program; domain branches live in references
  loaded by that program, never as sibling skills. A domain splits out only
  when it gains a distinct invocation contract — proven by a shaped eval, not
  by reference length.
- An AGENTS.md candidate that breaks the budget is not universal — it becomes
  a skill or a project template.

## ST — Stance

- **ST-01** Nothing is gospel. Rules are suggestions with rationale. Override
  with judgment, out loud, citing the ID.
- **ST-02** Evidence first. Claims carry proof: command output, diff,
  screenshot, transcript. Say "inferred" when it is inferred. Never claim done
  while a finding or failed check stands.
- **ST-03** Taste over rule-following. Channel specific dispositions, not
  name-drops: Torvalds (data structures first, never break userspace, solve
  real problems), Ousterhout (deep modules, small interfaces, design it
  twice), Uncle Bob (screaming architecture, behavior-preserving refactor,
  tests are spec), Kent C. Dodds (test behavior not implementation, mostly
  integration), Hickey (simple vs easy, it's just data, every complexity buys
  something or it goes), Carmack (measure, linear code, ruthless focus).

## TH — Thinking

- **TH-01** Fan options only when the decision has material alternatives.
  Compare deletion, the current interface, and the smallest boring design
  before adding a new architecture. Cosmetic variants do not count.
- **TH-02** Exploration ends in a decision artifact: chosen approach, why,
  rejected alternatives, and the evidence that would change the decision.
- **TH-03** Reversibility triage. One-way doors (public API breaks, schema
  migrations, infra selection, security posture) get slow treatment and
  operator sign-off. Two-way doors get decided fast by whoever is closest.
- **TH-04** Review the premise before the implementation. Resolve material
  human-owned choices through `shape`; decide reversible implementation facts
  from source.

## DE — Design & architecture

- **DE-01** Simplest, most elegant system wins. Complexity must pay rent:
  every module, abstraction, and state field earns its keep or goes. Local
  simplicity that moves complexity elsewhere is not progress.
- **DE-02** Data first. Get types and schemas right; code follows. Model the
  domain as plain data. Make illegal states unrepresentable — parse, don't
  validate.
- **DE-03** Deep modules, small interfaces. Hide information. Few concepts,
  deep capability. Shallow wide APIs are debt.
- **DE-04** Boring technology by default. Innovation tokens spent
  deliberately, one experiment at a time, in a component chosen for cheap
  replacement.
- **DE-05** Walking skeleton first. Thin end-to-end vertical slice — UI to
  storage to deploy — before depth anywhere. Tracer bullets over layered
  construction.
- **DE-06** Strangler over big-bang. Replace incrementally behind stable
  interfaces. Never freeze traffic for a rewrite.
- **DE-07** Deletion-first order: challenge, delete, simplify, accelerate,
  automate. Codified in `global/RULES.md`.
- **DE-08** Rule of three before abstraction. Prefer replaceable parts over
  flexible frameworks. Design for deletion.

## CH — Change discipline

- **CH-01** Smallest possible change that completes the ask — including
  caller migration and dead-path removal. Smallest never means incomplete.
- **CH-02** Root cause only. Fix sources; never suppress symptoms, swallow
  errors, or special-case inputs to make failures disappear. Three failed
  fixes in a loop: stop, question the architecture (`diagnose`).
- **CH-03** Clean cutover internally: migrate every caller, delete obsolete
  paths, no shims or aliases. Public contracts differ — deprecation windows,
  because userspace exists (ST-03).
- **CH-04** No silent scope growth. Anything beyond the stated ask needs
  explicit justification in the moment; otherwise it becomes a parked ticket,
  not a drive-by.
- **CH-05** Done means done: no stubs, placeholders, TODO-implementations;
  changed surfaces verified on the real interface; affected docs and changelog
  touched in the same change.
- **CH-06** One concern per commit; history reads as narrative. Never mix
  formatting with semantics.

## RS — Research & knowledge

- **RS-01** Research before building. Unfamiliar API, library, or error:
  web-research first (exa is the default provider), never code from memory.
- **RS-02** Source over memory, primary over secondary. Verify library
  behavior against its actual source and types when correctness matters.
  Hallucinated APIs are a standard failure mode, not an edge case.
- **RS-03** Dependency ladder: stdlib > small maintained dep > own code.
  Adopting a dependency adopts its maintenance, security, and transitive
  weight; vet license, activity, and supply chain before adoption.
- **RS-04** Research ends in an artifact. Timebox it; conclude with a
  decision — chosen option, rejected options, reasons. ADR if durable,
  ticket or comment if not.
- **RS-05** Knowledge vault: retrieve compiled notes before inferring, then
  read the source anyway. Write durable decisions back; leave raw sessions
  raw. (Codified in `global/AGENTS.md`.)

## CR — Craft

- **CR-01** Fast, strict stacks by default: Go or Rust for new services,
  CLIs, and tools. Strictness converts runtime surprises into compile errors.
  A project's own stack rules override this; never rewrite a working codebase
  to match fashion.
- **CR-02** Agent-friendly tools: structured output (`--json`), deterministic
  flags, machine-readable errors, scriptable, composable, no TUI-only
  behavior in pipelines. Choose and build tools to this spec.
- **CR-03** Sharpest instrument: LSP over text search for symbols; AST
  rewrite over sed for codemods; dedicated readers over cat. Shell runs one
  binary or a short fact pipeline, never surgery.
- **CR-04** Errors are data. Fail loud at boundaries; handle where action is
  possible; never swallow. Panic or assert only on invariant violation.
  Messages name operation, input, and expected state.
- **CR-05** Determinism by default: pinned dependencies, locked toolchains,
  seeded randomness. Same input produces the same artifact.
- **CR-06** Measure before optimizing. Algorithmic wins before micro-opt.
  Still avoid avoidable allocation, copying, and compute early (Carmack).
  Budgets beat vibes.

## TE — Testing & verification

- **TE-01** Tests defend behavior, not plumbing. Spec observable contracts at
  boundaries: CLI output, API responses, UI flows, persisted state.
  Implementation-coupled tests get rewritten or deleted.
- **TE-02** Mixed portfolio weighted toward integration: unit + integration +
  e2e; property and fuzz for parsers and core logic; torture and chaos for
  infrastructure; Gherkin where non-programmers read acceptance criteria.
- **TE-03** Suites are fast: units in seconds, full CI in minutes. Feedback
  delay changes developer behavior more than coverage numbers do.
- **TE-04** Flaky is broken. Quarantine with an owner immediately; fix or
  delete within days. Never normalize retries, sleeps, or wait-and-hope.
- **TE-05** Red means stop. Failing checks block merge; linters, formatters,
  and type-checkers run strict in CI with zero tolerated warnings.
- **TE-06** Real interface over mock. Prove changed behavior by running the
  actual surface: drive the browser, launch the TUI, hit the endpoint. An
  evidence packet accompanies every observable change (`evidence-packet`).
  Pull requests attach reviewer-open artifacts; local paths and hashes are not
  delivered evidence.
- **TE-07** Local mirrors production: compose/k8s reproduces production
  topology, config lives in code, drift is a bug with an owner. Manual QA on
  the running app is part of done — no test suite substitutes hands-on the
  real thing.
- **TE-08** Review depth scales with change class. Prose-only changes get
  relevant static review. Routine executable changes get one bounded
  exact-head review. Auth, secrets, persisted-state semantics, migrations,
  concurrency, harness, and release paths get explicit exhaustive review.

## OP — Delivery & operations

- **OP-01** Every release versioned, changelogged, and annotated through
  `misty-step/landmark`: conventional commits in; semantic version, technical
  changelog, synthesized user notes, machine-readable evidence out. Adopt per
  repo via its fleet playbook.
- **OP-02** Small frequent releases from trunk. Incomplete-but-deployable
  work hides behind flags, never branches.
- **OP-03** Production verification gate: a deployment is done only after the
  expected artifact passes health, smoke, manual QA on affected production
  surfaces, and applicable Sentry, log, metric, or trace inspection. A timed
  soak does not substitute for observed product behavior.
- **OP-04** Rollback rehearsed or nonexistent. A rollback that has never been
  exercised does not exist. Migrations are forward-compatible or paired with
  a tested reverse plan.
- **OP-05** Health is measured, SLO-shaped. Any service must answer "is it
  healthy?" from metrics, logs, and traces without SSH archaeology.
- **OP-06** Incidents stop feature work. Stabilize, then blameless
  postmortem with tracked actions. An alert paging twice without being
  actionable gets fixed or deleted; an alert catching real defects gets
  tuned and kept — never deleted for firing.
- **OP-07** Operations are idempotent and replayable. Scripts tolerate
  reruns; manual steps become code; snowflakes get codified or destroyed.

## OR — Agent orchestration

- **OR-01** Subagents for genuine independence. Fan out self-contained
  slices concurrently; never serialize independent work, never invent padding
  work to fill a wave.
- **OR-02** Contracts before fan-out. Interfaces, schemas, and file ownership
  are decided up front and stated in every brief; siblings coordinate through
  messaging before touching shared files; one named owner per shared mutation.
- **OR-03** Orchestrator verifies. A subagent finishing is an exit, not an
  acceptance; claims are checked against the artifact before integration.
- **OR-04** Scout-then-edit. Unknown territory gets delegated read-only
  recon; edits stay with one owner who holds the design.
- **OR-05** Ledger routing: Powder for all Misty Step work (skill scoped to
  `~/Development/misty-step/`); Habitat only inside R90. Work enters through
  takeable jobs; proof attaches at completion.
- **OR-06** Escalation shape: human-owned tradeoffs get asked with concrete
  options and a recommendation; reversible calls get made autonomously and
  reported.
- **OR-07** Per-token providers are spent deliberately, never ambiently.
  Standing and automatic surfaces — watchdog advisors, CI summaries, and
  routine subagents — start on flat-rate models. Automatic fallback chains
  exhaust flat-rate provider routes before one explicit terminal per-token
  hop: DeepSeek V4 Flash at max effort for routine text roles, or DeepSeek V4
  Pro at max effort for high-stakes text roles. Activation shows in session
  cost. Multimodal roles never fall back to text-only models; `vision` starts
  on flat-rate Gemini and retains image-capable fallbacks.
- **OR-08** Autonomous work leaves a decision trail. Choices made where the
  brief was silent surface post-hoc in a confidence-ranked, non-blocking
  ledger (`audit-choices`); the audit changes no code, and a needs-user
  verdict stops the run (premise gate). Only non-human-owned two-way-door
  choices proceed provisionally (TH-03).

## TL — Tooling surface

- **TL-01** Herdr coordinates sessions and panes; operator focus is
  preserved — never steal tab, pane, or workspace (`herdr`).
- **TL-03** Exe.dev VMs for isolation-sensitive work: untrusted dependencies,
  kernel-level experiments, parallel environments. Never burn the workstation.
- **TL-04** Iron Forest runs routine issue-to-PR mechanics headlessly
  (Builder/Verifier/Fixer). Interactive sessions handle judgment; the factory
  handles repetition.

## DC — Documentation

- **DC-01** Minimal surface: README (what, how to run), VISION (why),
  ARCHITECTURE when scale demands it, plus ADRs. Nothing else persists.
  Everything else is generated or deleted.
- **DC-02** ADRs are immutable once accepted: supersede, never edit.
  Context, Decision, Consequences.
- **DC-03** Git holds history; docs hold current truth. Comments explain why,
  not what. Hand-written changelogs rot; generated ones do not (OP-01).
- **DC-04** Staleness is a bug. Touching code with stale adjacent docs fixes
  or deletes the docs in the same change.

## SE — Security

- **SE-01** Least privilege everywhere: scoped tokens, short-lived
  credentials, minimal grants, containers without surprises.
- **SE-02** Secrets never appear in code, logs, git, or agent context. Assume
  anything an agent sees can land in transcripts and third-party models.
  Redact before sharing; gate pipelines with secret scans (Iron Forest does).
- **SE-03** Validate at trust boundaries; internal code trusts parsed types.
  Authn/authz, secret handling, and untrusted-input parsing get an
  adversarial pass (`security-review`).
- **SE-04** Blast radius stays bounded: destructive commands need explicit
  approval; production writes are gated; dry-run precedes run.
- **SE-05** Adversarial security judgment runs on open non-frontier models —
  GLM 5.3, Kimi K3, DeepSeek V4 Pro via OpenRouter. Frontier-lab models
  refuse or soften offensive reasoning: exploit chains, attack paths,
  red-team passes. Embodied: the `security-review` council script plus
  `security-reviewer`-agent recon, validation, and adjudication, routed
  via `config.yml` to DeepSeek V4 Pro. Standing closeouts cover correctness
  only (OR-07); security analysis runs on demand. Council remediation output is prose,
  not diffs — repairs stay blocked inside the skill until an approved
  writable agent or patch-producing mechanism exists (candidate 4).

## Ledgers

### Synthesis ledger — canon embodied in harness

| Canon | Harness artifact | Status |
| --- | --- | --- |
| DE-07 | `global/RULES.md` deletion-first order | live |
| TH-04, OR-06 | Lean premise gate in `skills/shape` and `global/AGENTS.md` | live |
| TE-06 | `skills/evidence-packet`; `deliver`, `code-review`, and `release` gates; delivery section of `global/AGENTS.md` | live — PR attachments required 2026-08-24 |
| ST-02, RS-02 | `global/AGENTS.md` findings-cite-primary-records line | live — trialed in iron-forest ops 2026-08-21 |
| TE-08 | Change-class review depth; exact-head bounded default; exhaustive high-risk council | live |
| Synthesis policy (one program per name) | Router skill + domain references rule | extracted from census ADR-0006 — governs new skills |
| ADR-0008 (census) | Testing doctrine one shared home | already embodied — foundation + CONTROLS; no new artifact |
| ADR-0009 (census) | Chief-stays-thin kits; 0001/0002/0003/0005 architecture-specific; 0004 mint broker decommissioned with mint | skipped by operator selection 2026-08-21 |
| OR-06 | `global/AGENTS.md` standing-mandate line (reversible calls made and reported) | live — trialed in iron-forest ops 2026-08-21 |
| CH-02 | `skills/diagnose` red-loop, architecture challenge at fix #3 | live |
| TH-01 | `skills/explore-design` fans ≥6 visual theses; `skills/shape` compares only material alternatives | live |
| DE-01, CH-03 | `global/AGENTS.md` design/delivery lines; `audit-simplifications`, `skills/refactor` | `audit-simplifications` live; `refactor` drafted — trial pending |
| RS-01 | exa routing in `config.yml`; `skills/research` decision protocol | drafted — skill written, untrialed |
| TL-01 | `skills/herdr` | live |
| OR-05 | `skills/capture` conversation-to-ledger extraction; Powder in Misty Step | drafted — capture skill written, trial pending |
| TE-01–TE-05 | `skills/foundation` agentic baseline | unverified coverage |
| OR-08 | Operator-invoked `skills/audit-choices` decision ledger | live |
| OP-01 | Landmark adopted in at least `canary` (full, `@35d002b`), `linejam` (full, `@35d002b` = v0.28.1), `crucible` (synthesis-only, `@v0`) — examples, inventory not audited | partial — fleet rollout incomplete |
| OP-03–OP-05 | `release` exact-head merge, deploy, production QA, observability, rollback, and incident gate | live — first real deploy pending |
| SE-03, SE-05 | Council script plus configured `security-reviewer` chain; security on demand; remediation externally owned | live |
| RS-03 | `skills/audit-simplifications` dependency-ladder lenses | live |
| OR-07 | Flat-rate watchdog; OpenRouter removed from automatic chains; spend confined to on-demand work plus the documented vision exception | live |
| TH-04, DE-01–DE-02, DE-07, OR-03, OR-07 | `skills/torvalds-design-review`; high-effort read-only `torvalds-reviewer` agent | live — explicit CLI trial 2026-08-22 |
| TH-01, TH-04, DE-01–DE-08, TE-01–TE-06, CH-01–CH-06, OP-03–OP-06, OR-01–OR-03 | `shape` → `deliver` → optional `code-review` → `release`; evidence-only `brief` | live for entry gates |
| RS-01–RS-02, OR-01–OR-03, OR-07 | `skills/dispatch` current-access, benchmark, cost, role, and fallback routing program | live — explicit CLI trial 2026-08-22; no config mutation |
| DE-07, TE-06, CH-01 | `skills/polish` one-interaction simpler/faster loop with real-surface proof | drafted — CLI gate trial 2026-08-23 |
| DE-01, DE-03, DE-08 | `foundation` context-budget control: per-atomic-module token budget (default 100k) with repomix gate and enforced boundaries | drafted 2026-08-23 — extracted from Taelin's Bend2 observation; first project install pending |
| ST-02, TH-01–TH-04, DE-07, RS-01–RS-05, TE-06, OP-03–OP-06, SE-01–SE-04 | `skills/audit-observability` whole-system signal audit, context contract, and deletion-first remediation plan | drafted 2026-08-25 — first target-system trial pending |

### Candidate syntheses — canon not yet embodied

| Order | Canon | Proposed vehicle |
| --- | --- | --- |
| 1 | TE-01–TE-05 | `foundation` installs project test baseline: portfolio spec, flaky policy, CI budget |
| 2 | OP-01 | Extend landmark adoption across remaining active repos: `fleet scan` → `plan` → confirmed PRs |
| 3 | OR-02, OR-03 | Port brief-contract and verify-the-artifact semantics into Iron Forest declarations |
| 4 | SE-05 | Prototype a writable approved-model remediation agent or an `audit.mjs` patch mode |

### Deviation ledger — reality beating rules

| Date | ID overridden | Case | Outcome |
| --- | --- | --- | --- |
