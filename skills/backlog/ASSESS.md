# Assess the backlog

Reality first. The board is a claim about work; primary records decide what is
true.

## Scope

Read the argument, project policy, repository identity, and board instructions.
For Misty Step, run `powder skill`; treat the relevant verb's `--help` output as
command truth. Use the exact repository value stored by the board. If it is
unknown, inspect the unfiltered list and derive it rather than guessing.

Record the target, exact board scope, snapshot time, and exclusions. Make no
board or product changes.

Done when every later count and claim has one explicit scope.

## Inventory

Read the full in-scope list without a state filter, then read every item through
`powder show`. Follow direct blockers and cited proofs, pull requests, commits,
or decisions far enough to understand the item. Read an out-of-scope item only
when an in-scope relation depends on it.

Classify each item once, in this precedence: completed, abandoned, waiting,
held, draft, blocked, takeable. A draft has no executable spec. Derive blocked
state from the actual direct blockers. Powder list order is creation order, not
priority.

For each item, record:

- ID, title, intended outcome, and repository;
- current state, holder or question, direct blockers, and freshness dates;
- proof or primary evidence;
- the theme and user or operator outcome it serves;
- contradictions, overlap, or evidence gaps.

Done when all in-scope items are accounted for and every relation resolves or is
named as a gap.

## Check reality

Test material board claims against their owning records: current source and
product documents, merged and open changes, accepted decisions, and the real
product surface when a capability or delivery claim depends on runtime state.
Use current readback, not recollection or a status summary. Inspect only enough
of the codebase to decide the board claim.

Classify carefully:

- **stale** means current evidence contradicts the item or its premise no longer
  holds; age alone is only a review signal;
- **duplicate** means two items own the same outcome, not merely the same area;
- **missing** means an evidenced necessary outcome has no board owner;
- **delivered** requires the proof expected by the item, not an implementation
  claim alone;
- **unknown** names the exact unavailable evidence or unsettled human choice.

Done when every stale, duplicate, missing, and delivered judgment cites a
primary record or remains explicitly unknown.

## Synthesize

Return a dated snapshot with these sections:

1. **Scope and evidence** — board query, repository identity, source revision or
   runtime identity when used, and gaps.
2. **State** — counts and item IDs by state; totals must reconcile.
3. **Themes** — each coherent product or system outcome, the items serving it,
   and what remains unfinished.
4. **Flow** — takeable work, active work, waits, blocker chains, drafts, and
   stranded items. Do not infer rank from list order.
5. **Reality gaps** — delivered-but-open, obsolete, duplicate, unsupported,
   missing, or unverifiable work.
6. **Board account** — what the board says the product is becoming, what it says
   matters now, and which material choices the board cannot settle.

Keep facts, inferences, and operator choices distinct. Cite item IDs beside every
board claim and primary records beside every reality claim.

Done when the state totals reconcile, every in-scope item appears in the
account, and the summary can be checked without this session.