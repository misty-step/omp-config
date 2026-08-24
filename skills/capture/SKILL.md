---
name: capture
description: Extract and commit this conversation's durable findings, decisions, and debt to the project's backlog of record.
disable-model-invocation: true
argument-hint: "[optional project or scope]"
---

# Capture

Commit the durable findings, decisions, defects, and technical debt of this
conversation to the authoritative backlog of record. Preserve what was learned,
why it matters, and how future work can prove it complete.

## 1. Establish the boundary

Use the active conversation and project. Use the invocation argument only to
name the project or narrow the subject. Read project policy to identify the
backlog of record and its interface. When policy names Powder (such as in
Misty Step repositories), read `skill://powder` before writing.

If no authoritative backlog is configured, report that missing prerequisite.
Do not substitute a local file, issue tracker, or memory store.

Completion criterion: One conversation boundary, one project, and one
backlog of record are explicit.

## 2. Distill the findings

Identify each durable finding that warrants future work or changes existing
work:

- an observed defect, unmet need, or architecture debt;
- an operator decision that constrains future delivery;
- a material risk, dependency, or unresolved choice;
- a concrete follow-up task that remains incomplete.

For each finding, preserve its evidence, consequence, desired outcome, known
constraints, and observable proof. Keep an operator-owned choice open unless
the conversation settles it. Exclude completed work, transient process detail,
and unsupported speculation.

Completion criterion: Every substantive finding is marked for creation,
reconciliation with an existing item, or omission with a stated reason.

## 3. Reconcile the record

Read the relevant backlog before writing. Search by subject, outcome, and
repository. Amend the item that already owns the outcome. Create a new item only
when no existing item owns it. Split findings only when they have independently
completable outcomes or different owners.

Preserve priority, status, ownership, and scope unless this conversation
explicitly changes them. Record a dependency only when evidence establishes
it.

Completion criterion: Each retained finding has exactly one owning backlog
item, with no duplicate work introduced.

## 4. Commit the findings

Write the smallest complete record. Give each item an outcome-led title and a
specification that carries:

- the finding and its evidence;
- the desired outcome and boundary;
- material constraints, dependencies, and open choices;
- the observable completion criterion and required proof;
- the originating conversation reference when one is available.

Set repository and blocker metadata when the evidence supports them. Preserve
exact quotations only when their wording governs the work. The backlog is an
institutional record, not a transcript archive.

Completion criterion: Every created or amended item can be understood and
completed without recovering this conversation, except for choices explicitly
left to the operator.

## 5. Verify and account

Re-read every changed item from the backlog interface. Confirm that the stored
record preserves the finding, evidence, boundary, open choices, and proof.
Report each item identifier with `created` or `amended`. List omitted findings
and their reasons.

Completion criterion: Every substantive finding is accounted for, every
changed item is verified from the backlog of record, and no unresolved write
failure remains.
