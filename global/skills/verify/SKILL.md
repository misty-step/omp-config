---
disable-model-invocation: true
name: verify
description: Verifier kit router. Select live proof, gate, or review-lens branches without repairing findings.
argument-hint: "[live|ci|tests|security|vision|review] [claim]"
---

# /verify

Kit router for **verifier**. Stay read-only. Return evidence. Never repair.

## Choose one primary branch

| Brief signal | Load | Oracle |
|---|---|---|
| Live behavior, browser, CLI, API path | `skill://verify-live` | PASS/WARN/FAIL/SKIP on the named entrypoint |
| Repository gate, CI contract | `skill://ci` | exact gate command and observed result |
| Tests defend the changed contract | `skill://review-tests` | ranked test-defense findings |
| Security defects in the diff | `skill://review-security` | ranked security findings with triggers |
| Intent vs written vision/ADR | `skill://review-vision` | intent findings only; taste is not a finding |
| Frozen committed-range protocol | `skill://code-review` | receipt protocol; you submit a lens result, you do not own the gate |

If the brief names multiple angles, run them in order and keep findings separated by angle.

## Shared rules

1. Read the acceptance contract and name the cheapest credible falsifier first.
2. Exercise or inspect only the claimed surface.
3. Preserve evidence paths, commands, and residual risk.
4. Do not edit, write, weaken gates, or file fixes.
5. Do not run persona QA. That route is chief → `qa-master` → `qa-persona`.
6. Point at `global/references/verification-system-first.md` when proof design is disputed.
7. Point at `global/references/testing-principles.md` when test quality is disputed.

## Completion

Return the branch verdicts, exact evidence, and any unverified paths.
Subagent confidence is not evidence.
