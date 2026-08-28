# Misty Step operating philosophy

This document describes how we choose, build, and care for software. It is a
philosophy, not a procedure, checklist, or authority. Reality outranks it.
When experience contradicts a principle, we examine the evidence and improve
the principle.

## Reality outranks doctrine

Observed behavior is the ground truth. Claims earn confidence through direct
evidence, primary sources, and reproducible results. We name inference as
inference and uncertainty as uncertainty.

Principles are tools for judgment, not substitutes for it. A justified
deviation is information. Repeated deviations expose a weak principle or a
changed world; they do not justify permanent exception machinery.

Taste matters. We value clear thinking, technical honesty, and the discipline
to discard a favored idea when the system disproves it.

## Purpose before mechanism

We begin with the outcome: who benefits, what changes for them, what must
remain true, and what would prove success. A precise solution to the wrong
problem is still wrong.

Requirements need an accountable owner or binding evidence. We challenge
unsupported requirements before optimizing them. We distinguish product intent
from implementation habit and preserve deliberate non-goals.

Material alternatives deserve comparison. Deletion, the current interface, and
the smallest boring design are always candidates. Exploration ends with a
decision, rejected alternatives, and the evidence that would change the choice.

Reversible choices move quickly. Irreversible choices receive slower treatment,
clear ownership, and explicit acceptance of their consequences.

## Simplicity is a system property

The simplest complete system wins. Complexity must pay rent in capability,
safety, or enduring reduction of other complexity. Local elegance that moves
burden into callers, operations, or future maintenance is not simplicity.

We challenge, delete, simplify, accelerate, and only then automate. We prefer a
small number of deep concepts to a large vocabulary of shallow abstractions.
We design for replacement and deletion rather than speculative flexibility.

Boring technology is the default because familiarity compounds. Innovation is
a deliberate experiment placed behind a boundary where failure and replacement
are cheap.

## Data, ownership, and boundaries

Data structures, relationships, lifecycles, and invariants come before control
flow. Every datum has one owner and one explicit path. The model should make
illegal states unrepresentable where the language permits it.

Good modules hide necessary complexity behind small, stable interfaces. Policy
lives with the state it governs. Special cases stay local instead of leaking
through the system.

Boundaries define trust, compatibility, and failure. We validate untrusted
input at the edge and rely on parsed meaning inside. Public contracts respect
their users; internal contracts change cleanly with every caller migrated.

## Small changes, complete outcomes

We prefer the smallest change that fully accomplishes the outcome. Small never
means partial. A coherent change includes affected callers, obsolete-path
removal, proof, and the documentation needed to preserve current truth.

We fix causes rather than suppress symptoms. Repeated failed fixes are evidence
that the model or architecture deserves re-examination.

We leave no scaffolding disguised as delivery: no inert placeholders, fake
fallbacks, abandoned compatibility paths, or promises that the next change will
finish this one. History should explain the evolution of the system without
mixing unrelated concerns.

## Proof closes the loop

Source outranks memory. Primary evidence outranks summaries. Research ends in a
decision or an explicit gap, not a pile of links.

Changed behavior is proved at the real interface. Tests defend observable
contracts, boundaries, invariants, and failure paths rather than implementation
choreography. A failing required check stops the change.

We measure before optimizing and compare like with like. Fast feedback changes
behavior; flaky feedback destroys trust. Completion is a claim that carries
evidence.

## Operations are part of the product

A system includes its deployment, configuration, recovery, observability, and
operator work. A feature that cannot be shipped, understood, or recovered is
not complete.

Production verification observes the product behavior that matters. Health is
expressed through useful signals and service objectives, not archaeological
access to machines. Alerts must lead to action.

Rollback exists only when it can be executed. Operations are idempotent and
replayable. Incidents suspend feature work until the system is stable and the
learning is captured without blame.

## Trust and blast radius

Least privilege is the default. Secrets stay out of source, logs, transcripts,
and unnecessary contexts. Destructive power is narrow, visible, and gated by
the person accountable for its consequences.

Dependencies extend the trust boundary. Their license, maintenance, security,
transitive weight, and exit path are part of the adoption decision.

Safety comes from explicit ownership, constrained authority, and recoverable
actions—not from assuming every participant or component will behave correctly.

## Automation serves judgment

Automation handles stable, necessary, measured repetition. It does not make an
unclear process correct or turn an unsettled decision into policy.

Tools should be deterministic, composable, inspectable, and honest about
failure. Structured interfaces reduce ambiguity for both people and machines.

Delegation begins with a contract: outcome, boundaries, ownership, and proof.
Independent review supplies evidence and challenge, not authority. Human-owned
tradeoffs remain human-owned; mechanical and reversible choices belong close
to the work.

## Stewardship over time

We optimize for the system six months from now, not only the patch in front of
us. The codebase should become easier to understand, operate, and change after
each completed piece of work.

Documentation holds current truth; history holds history. Durable decisions
record context, choice, and consequences. Stale explanation is repaired or
deleted when encountered.

We leave systems with fewer accidental concepts, clearer ownership, stronger
evidence, and a cheaper path to the next change.
