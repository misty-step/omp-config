---
disable-model-invocation: true
name: bdd-pipeline
description: |
  Opt-in product methodology: theme or story to acceptance specs, then
  implement and verify. Use only when the operator or repo chooses BDD-style
  delivery. Not the default OMP workflow. Trigger: /bdd-pipeline, "gherkin
  pipeline", "acceptance-first delivery".
argument-hint: "[theme|story|acceptance|implement|verify]"
---

# /bdd-pipeline

Optional pipeline for product repos that want acceptance-first delivery.
Do not use for harness engineering, research, or ops by default.

## Agents

Use existing broad agents only:

| Stage | Agent | Oracle |
|---|---|---|
| Shape theme / story | chief or `architect` | written story + non-goals |
| Acceptance spec | `builder` or chief | runnable acceptance (Gherkin, fixed script, or checklist with commands) |
| Implement | `builder` | code + unit tests meeting acceptance |
| Verify | `verifier` | acceptance commands pass on real entrypoint |
| Structure pass | `sculptor` when substantive | deletion/deepen findings |

No `gherkin-author`, `qa-author`, `cleaner`, or `hardener` native agents.

## Stages

1. **Theme / story** — one user-visible outcome, scope, and non-goals.
2. **Acceptance** — examples that fail before the change and pass after. Prefer executable commands over prose-only Gherkin when the repo has no cucumber runner.
3. **Implement** — smallest change that satisfies acceptance.
4. **Verify** — fresh verifier runs acceptance and named gates.
5. **Stop** — ship only with evidence; optional sculptor on large diffs.

## Rules

1. Opt-in per request or repo. Never imply this is global dispatch law.
2. Keep acceptance artifacts in the product repo (`features/`, `tests/acceptance/`, or documented commands).
3. Verifier does not implement fixes.
4. If the process itself changes (new mandatory stage), apply
   `global/references/process-adversarial-testing.md`.

## Non-goals

- Iron Forest daemon FSM (product delivery machine lives there)
- Replacing outcome-based `/dispatch` for all work
