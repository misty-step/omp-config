# Review Council

The multi-model, multi-angle Council of Subagents contract.

## 1. Master Reviewer and Council Architecture

The top-level agent acts as the **Master Reviewer**, orchestrating an
exhaustive council of independent subagents with diverse provider and model
specializations to prevent single-family blind spots.

```text
               ┌───────────────────────────────────────────────┐
               │         Master Reviewer (Orchestrator)        │
               └───────┬──────────────┬──────────────┬─────────┘
                       │              │              │
        ┌──────────────┴───┐   ┌──────┴─────────┐   ┌┴────────────────┐
        │ Structure Scout  │   │ Behavior Scout │   │Practicality Sc. │
        │ (Torvalds/Oust.) │   │  (Uncle Bob)   │   │(Carmack/Thermo) │
        │ GPT-5.6 Sol Max  │   │ Claude Fable 5 │   │    Grok 4.6     │
        └──────────────────┘   └────────────────┘   └─────────────────┘
```

## 2. Select & Model-Diverse Roster

A trivial change is local, changes no public interface or state, and touches no
error, security, persistence, or concurrency path. Use one scout with
`thermo.md` and `torvalds.md`.

For all other changes, dispatch the full three-group council across distinct
model families:

| Group | Target Lens References | Model Role & Focus | Job |
|---|---|---|---|
| **structure** | `torvalds.md`, `ousterhout.md`, `hickey.md`, `taelin.md` | Primary Reasoning (`@slow` / GPT-5.6 Sol) | Data ownership, invalid states, module depth, decomplection |
| **behavior** | `uncle-bob.md`, `kcd.md` | Cross-Provider Reasoning (Claude Fable / Opus) | Correctness, contracts, boundary tests, error recovery |
| **practicality** | `carmack.md`, `thermo.md`, `ponytail.md` | High-Throughput Critic (Grok 4.6 / Gemini Flash) | Inspectability, hot paths, YAGNI, code growth |

Auth, secrets, untrusted input, privilege, cryptography, and material trust
boundary changes require an adversarial pass via `/security-review` (routed
to DeepSeek V4 Pro via `security-reviewer`). Stop and ask the operator to
invoke `/security-review`; resume only from its triaged findings.
Completion criterion: The group set is fixed, and each group has an assigned
model role and lens references.

## 3. Run

Launch read-only scouts in parallel using the `task` subagent tool. Give each
scout:

- accepted intent, user value, and scope;
- complete diff and surrounding codebase context;
- test execution results and product-surface QA observations;
- inspected evidence artifacts;
- only its assigned lens references and specific evaluation rubric.

Each scout independently returns zero to five structured findings:

```yaml
- symbol: "exact file, function, or interface"
  mechanism: "trigger condition and failing mechanism"
  evidence: "observed behavior, test failure, or structural smell"
  repair: "smallest coherent, behavior-preserving repair"
  severity: "block | should | note"
  scope: "in | out"
```

Completion criterion: Every dispatched council scout returns grounded,
evidence-backed findings.

## 4. Classify & Adjudicate

The Master Reviewer collects, dedupes, and adjudicates all scout findings.

1. **Blockers:** Any supported correctness, security, data integrity, or
   contract violation is a non-negotiable **Blocker**. Taste never suppresses a
   Blocker.
2. **Takes:** A non-blocking finding is a **Take** only when its repair:
   - eliminates an invalid representable state or dual ownership;
   - deletes incidental machinery or decomplects concerns;
   - creates a smaller, more stable module interface;
   - makes failure visible and recoverable.
3. **Drops:** Style, naming preferences, speculative flexibility, and unrelated
   cleanup are classified as **Drop** unless they cause a concrete defect.

Completion criterion: Every finding is classified as Blocker, Take, or Drop
with an explicit rationale.
