---
name: estate-infrastructure
description: |
  Use when Misty Step infrastructure work needs current Estate standards,
  inventory or plan readback, a bounded restart or release request, or an
  exact-plan mutation. Trigger: /estate-infrastructure, /estate.
argument-hint: "[observe-plan|bounded-reversible|exact-plan-mutation]"
---

# /estate-infrastructure

Estate is Misty Step's infrastructure intent and sole mutation authority.
Roster projects how an agent finds that authority; it does not copy provider
policy or turn an agent declaration into approval.

## Read the binding source

Read the live Estate revision selected by the workspace or control plane:

1. `VISION.md` for ownership and consequence boundaries.
2. `standards/000-governance.toml`, `standards/vendor-inventory.toml`, and the
   applicable file under `standards/vendors/` for current defaults.
3. Any matching, unexpired `exceptions/` declaration and relevant `decisions/`.
4. `docs/schemas/authorization-v1.md` before requesting an infrastructure
   action.

The canonical repository paths begin at
`https://github.com/misty-step/estate/tree/master/`. Current vendor choices
stay there; do not restate them as durable Roster policy or infer them from an
agent or role name.

If a standard's `review_date` has passed, an exception is expired, or required
evidence is recorded as a gap, report that exact condition and do not use it to
select a vendor or justify a mutation. Keep work read-only unless a separately
valid Estate authorization covers that exact action. Refresh the Estate
evidence or obtain an Estate-declared exception; neither a remembered
preference nor a Roster declaration fills the gap.

## Requested action classes

- `observe-plan`: provider reads, inventory, reconciliation, forecasting, drift
  inspection, and exact plan generation. It grants no mutation.
- `bounded-reversible`: requests only `restart` or `deploy_release`. Standing
  authorization is possible only when Estate verifies the exact resources,
  low-risk reversibility, cost and blast-radius bounds, expiry, artifact, and
  runtime-key proof, and the live Estate schema permits standing execution for
  that payload. A non-disposable payload requires one-shot authorization under
  the current schema.
- `exact-plan-mutation`: requests `create`, `update`, `replace`, or `delete`, or
  any higher-risk `restart` or `deploy_release`. It requires one-shot Estate
  authorization bound to the exact artifact and runtime proof.

The matching public pack is declaration vocabulary for the requested scope.
Pack inclusion, a role name, Powder state, conversational approval, and a
generic Roster authority-provider result without the verified Estate artifact
and runtime proof are not runtime identity or Estate approval. An executor acts
only on an Estate-approved typed artifact; it never derives a provider command
or credential from this skill. Bind standing capabilities only to a durable
declared role; an ad-hoc role may prove this projection but is not a stable
standing-capability identity.

## Evidence

Keep literal credentials, provider snapshots, state, plans, and raw logs out of
Git and the bundle. Return the Estate revision, standards and exceptions read,
provider readback clock, exact plan digest, authorization basis, and redacted
receipt references appropriate to the operation. Never claim provider action,
operator presence, rollback, or recovery without its live evidence.
