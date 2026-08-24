# Repair and Verification Loop

Shared loop contract consumed by `/deliver` and `/code-review`.

## 1. Security Remediation Policy

Security-review findings remain under `/security-review` model policy. Record
accepted guidance and suspend autonomous repair. Do not design or apply a
security repair until an approved writable mechanism or external repair exists.
Re-audit an external repair before resuming this loop.

## 2. Repair Discipline

1. **In-Scope Blockers and Takes:** Repair all supported in-scope Blockers and
   in-scope Takes autonomously. Delete first. Fix the source directly. Migrate
   every caller across the repository. Remove obsolete paths, shims, and tests.
2. **Out-of-Scope Blockers:** Route out-of-scope Blockers to the operator with
   exact evidence and a suggested owner.
3. **Narrow Re-Verification:** Run the narrowest real scenario and applicable
   contract tests immediately after each repair.

## 3. Council Convergence

Rerun the same council groups over the repaired boundary. Continue iterating
until:

- zero in-scope Blockers and in-scope Takes remain;
- all contract tests and product-surface QA checks are green;
- evidence matches the final behavior;
- the same finding does not recur after a coherent repair.

Stop and escalate to the operator only when:

- a repair changes accepted intent or scope;
- a hard-to-reverse architectural tradeoff arises;
- the same supported defect recurs after an attempted fix.

Completion criterion: The loop is green, an explicit decision blocks it, or an
accepted security finding has one named external remediation blocker.
