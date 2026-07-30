---
disable-model-invocation: true
name: estate-infrastructure
description: |
  Use when infrastructure work needs Estate standards, inventory or plan readback, a bounded restart or release request, or an exact-plan mutation.
  Trigger: /estate-infrastructure, /estate.
argument-hint: "[observe-plan|bounded-reversible|exact-plan-mutation]"
---

# /estate-infrastructure

Estate defines Misty Step's infrastructure intent and holds sole mutation authority.
The projected agent home shows where an agent finds that authority. It does not
copy provider policy or turn an agent declaration into approval.

## Read the binding source

Read the live Estate revision that the workspace or control plane selects:

1. Read `VISION.md` to learn ownership and consequence boundaries.
2. Read `standards/000-governance.toml`, `standards/vendor-inventory.toml`, and the
   applicable file under `standards/vendors/` for current defaults.
3. Read any matching, unexpired `exceptions/` declaration and relevant `decisions/`.
4. Read `docs/schemas/authorization-v1.md` before you request an infrastructure
   action.

Canonical repository paths start at
`https://github.com/misty-step/estate/tree/master/`. Keep current vendor choices
there. Do not restate them as durable local policy or infer them from an agent or
role name.

When a standard's `review_date` has passed, an exception is expired, or required
evidence has a gap, report that exact condition. Do not use the condition to
select a vendor or justify a mutation. Keep work read-only unless a separate
valid Estate authorization covers that exact action. Refresh Estate evidence or
obtain an Estate-declared exception. A remembered preference or an agent-home
declaration cannot fill the gap.

## Requested action classes

- `observe-plan`: Use for provider reads, inventory, reconciliation, forecasting,
  drift inspection, and exact plan generation. It grants no mutation.
- `bounded-reversible`: Request only `restart` or `deploy_release`. Estate can
  grant standing authorization only after it verifies the exact resources,
  low-risk reversibility, cost and blast-radius bounds, and expiry. Estate must
  also verify the artifact and runtime-key proof. The live Estate schema must
  permit standing execution for that payload. A non-disposable payload requires
  one-shot authorization under the current schema.
- `exact-plan-mutation`: Request `create`, `update`, `replace`, or `delete`, or
  any higher-risk `restart` or `deploy_release`. It requires one-shot Estate
  authorization bound to the exact artifact and runtime proof.

The matching public pack gives declaration vocabulary for the requested scope.
Pack inclusion, a role name, Powder state, conversational approval, and a generic
agent-home authority-provider result do not establish approval. None establishes
runtime identity or Estate approval without the verified Estate artifact and
runtime proof. An executor acts only on an Estate-approved typed artifact. It
never derives a provider command or credential from this skill. Bind standing
capabilities only to a durable declared role. An ad-hoc role may prove this
projection, but it is not a stable standing-capability identity.

## Evidence

Keep literal credentials, provider snapshots, state, plans, and raw logs out of
Git and the bundle. Return the Estate revision, standards and exceptions read,
provider readback clock, exact plan digest, and authorization basis. Return
redacted receipt references that fit the operation. Never claim provider action,
operator presence, rollback, or recovery without live evidence.
