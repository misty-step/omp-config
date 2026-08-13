---
name: foundation
description: Explore a project's intent and current reality, agree on the smallest coherent foundation for its next stage, then implement and prove the locked plan.
disable-model-invocation: true
argument-hint: "[repo-path]"
---

# Foundation

Help one project become easier to build, use, verify, deliver, and operate at
its credible next stage. Foundation is a design conversation followed by a
locked implementation, not a universal compliance checklist.

The workflow is:

```text
Orient → Explore → Frame → Recommend → Discuss → Lock → Execute → Prove
```

Do not mutate the project before the operator explicitly locks scope and
acceptance. Repository inspection, safe read-only commands, and reversible
runtime observation are allowed during exploration. Installation, generated
files, issue creation, configuration changes, and repository edits are not.

## Stance

- Start from the project's purpose, users, stage, distribution, constraints, and
  ambition. Absence is not automatically a gap.
- Enable the next credible stage. Avoid both present-only local optimization and
  speculative construction of the imagined end state.
- Recommend one coherent package. State what it deliberately omits and the
  evidence or trigger that would justify adding each deferred capability.
- Prefer existing project and organizational conventions when they remain
  current and fit the project. Named tools are replaceable preferences, not
  doctrine.
- Inspect current repository guidance, organization guidance, installed tools,
  and live integrations before recommending a work tracker, release system,
  credential route, deployment target, or observability product.
- Do not preserve retired machinery because an old project, archived prompt, or
  stale document names it.
- Ask the operator about intent and tradeoffs, never facts available from the
  repository or tools.

## 1. Orient and explore

Default to the current repository unless the invocation names another target.
Keep one repository or coherent project boundary per run.

Inspect before interviewing. Establish observed facts and unresolved questions
across all four domains:

### Product and users

- Purpose, users, primary jobs, project stage, and success criteria.
- Public, private, internal, experimental, library, service, CLI, web, or mixed
  distribution.
- Current product truth: README, vision, screenshots, demos, documentation,
  user feedback, and deployed surfaces where applicable.

### Architecture and interfaces

- Domain core, ownership boundaries, data model, dependencies, and technology
  constraints.
- Existing API, CLI, UI, library, skill, MCP, SDK, event, or automation faces.
- Which faces serve real users or integrations. Do not presume every project
  needs every face.
- State ownership, failure boundaries, security boundaries, and likely next
  architectural pressure.

### Quality and verification

- Fast and full gates, CI, behavioral tests, live probes, and release checks.
- Important risks not defended by the current verification system.
- Security, accessibility, performance, compatibility, and supply-chain needs
  only to the degree the product and risk justify them.
- Prefer observable-contract coverage and real-boundary proof over coverage
  percentages or checklist volume.

### Delivery and operations

- Zero-to-use onboarding, configuration, deployment, release, rollback, and
  runtime diagnosis.
- Observability, backup/restore, data lifecycle, and incident needs where state,
  users, or production operation make them consequential.
- Durable work tracking and organizational conventions. Misty Step projects may
  prefer GitHub Issues; R90 projects may use Habitat; inspect current authority
  instead of treating either as universal.
- Existing integrations and installed tools are evidence, not obligations.

Use safe probes where they reduce uncertainty. Do not claim a runtime, command,
integration, or public surface works from declaration alone.

## 2. Frame the project

Before asking questions, present a compact evidence-backed profile:

```markdown
## Project profile
- Purpose and users:
- Current stage and distribution:
- Existing strengths:
- Next-stage pressure:
- Constraints and settled decisions:
- Observed foundation risks:
- Uncertainties requiring operator judgment:
```

Label hypotheses as hypotheses. Cite the paths, commands, URLs, or runtime
observations supporting consequential claims.

Then ask a small batch of questions whose answers materially change the
recommendation. Focus on ambition, intended users, acceptable operating burden,
compatibility, timing, and tradeoffs. Offer concrete options with a recommended
default when the tradeoff is understood. Do not conduct a questionnaire for its
own sake.

Continue inspection after an answer only when it resolves a real branch. Keep
the dialogue compact; another round is justified only by a consequential new
uncertainty.

## 3. Recommend one foundation package

Synthesize one opinionated package rather than a catalog of practices or generic
lean/standard/ambitious tiers.

```markdown
## Recommended foundation
### Outcome
<What credible next stage this enables.>

### Build now
- <coherent capability, rationale, and observable result>

### Preserve
- <existing strengths or settled choices that should not be churned>

### Deliberately omit
- <capability not justified now, why, and the trigger for reconsidering it>

### Material alternatives
- <only alternatives with meaningfully different costs or product consequences>

### Proposed slices
1. <coherent implementation slice>

### Proof
- <observable scenario or invariant for each outcome>

### Non-goals
- <explicit boundaries>
```

Recommendations must connect evidence to a project outcome. “Best practice,”
“every project needs this,” and tool availability are not sufficient reasons.
State maintenance and operating cost. Prefer the smallest package whose pieces
reinforce each other; do not recommend disconnected cleanup under the
Foundation label.

Public proof, marketing, documentation, API, CLI, UI, skill, MCP, SDK, release
automation, observability, work tracking, and deployment infrastructure are all
conditional. Recommend each only when the project profile gives it a job.

## 4. Discuss and lock

Invite direct revision. Resolve disagreements and update the recommendation in
conversation. Do not create a mandatory plan file, issue, ADR, or work ledger
entry merely to record the discussion.

Execution requires an explicit operator lock covering:

```markdown
## Foundation lock
- Target outcome:
- Accepted scope:
- Non-goals:
- Implementation slices:
- Observable acceptance and proof:
```

File-level mechanics may remain implementation judgment unless an interface,
migration, destructive action, compatibility promise, or architectural seam
needs an explicit decision. A request to audit, explore, discuss, recommend, or
plan is not an execution lock. Silence is not approval.

If the operator changes the goal, revise the recommendation and lock before
editing. If the operator locks only part of the package, execute only that part.

## 5. Execute the locked plan

After an explicit lock:

1. Translate the accepted slices into tracked work.
2. Implement the simplest coherent design that satisfies the locked outcome.
3. Preserve existing conventions and migrate every affected caller or surface.
4. Verify each significant slice on its real boundary before continuing.
5. Keep changes inside the accepted scope and non-goals.

Do not silently add attractive cleanup, a named organizational tool, another
interface, or future-stage infrastructure.

When execution uncovers consequential work outside the lock, finish any safe,
independent work already accepted, then return with:

- the new evidence;
- why it changes or blocks the locked design;
- one recommended amendment;
- the scope and proof delta.

Discuss and explicitly relock before expanding. Mechanical necessities already
implied by the accepted outcome do not require ceremony; product, architecture,
operating-cost, compatibility, and destructive changes do.

## 6. Prove and close

Proof must match the accepted outcomes:

- Run repository gates that defend changed contracts.
- Exercise real CLI, API, UI, library, service, deployment, or onboarding paths
  affected by the work.
- Use a real browser for rendered surfaces and real runtime/readback for
  operational claims.
- Distinguish declarations, deterministic gates, live observations, and fresh
  judgment. Never substitute a weaker class for the promised proof.

Close with:

```markdown
## Foundation result
- Locked outcome:
- Implemented slices:
- Proof observed:
- Preserved decisions:
- Residual risks:
- Reconsider when:
```

Do not turn every residual into an issue automatically. Report it as a future
decision unless the locked scope explicitly includes durable tracking.
