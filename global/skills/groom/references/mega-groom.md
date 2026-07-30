# Mega Groom

Treat strategic `/groom` as an exhaustive project-quality sweep.
Review product, architecture, operations, and agent readiness, not only issue
triage.

## Mission

Cover the full project, then distill the findings.

The output is a detailed plan to make the current project world class.
Cover the codebase, documentation, infrastructure, operations, product, system
design, architecture, value proposition, testing, security, and agent interface.
Make the backlog diff the durable expression of that plan.

Start the plan from a project vision.
If the repo lacks a durable vision artifact, emit one or shape the epic that
will create it.
Otherwise, use the vision as the stable standard for deciding what to include.

## Coverage Map

Account for every surface in each strategic groom.
Mark each surface `complete`, `partial`, `failed`, or `skipped`. Do not omit a
surface.

| Surface | Question |
|---|---|
| Product and value prop | Who is this for, why would they care, what would make it indispensable? |
| Project vision | What durable vision guides brainstorming, backlog moves, deletions, and sequencing? |
| Operator/user experience | Can a new or returning user achieve the core job without friction? |
| Architecture and system design | Are the deep modules deep, the boundaries honest, and the interfaces small? |
| Code quality and simplicity | What can be deleted, flattened, clarified, or made harder to misuse? |
| Runtime reliability | What fails under load, restart, queue pressure, retries, or partial outages? |
| Security and privacy | Where can secrets, tokens, user data, metadata, or logs leak? Where can authority exceed its intended scope? |
| Observability and ops | Can an operator see state, cost, queue pressure, incidents, and recovery actions? |
| Tests and verification | Do gates prove the live behavior that matters, not just units, and do they fail the likely security mistakes before publication? |
| Documentation and onboarding | Can a cold agent or human understand, run, extend, and debug the project? |
| Agent readiness | Are skills, AGENTS, lane cards, receipts, and CLI JSON surfaces primary interfaces? |
| Infrastructure and delivery | Are deploys, rollbacks, backups, hosted checks, and local development predictable? |
| External exemplars | What do adjacent best-in-class systems prove or warn against? |

## Swarm Contract

Default strategic groom launches a swarm, not a single helper.
Use the harness's native subagents when explicitly allowed and available.
Otherwise, use peer CLIs or sprite lanes.
When delegation is unavailable, run the same coverage map locally and label the
run degraded.

Minimum useful swarm for a normal repo:

- Product/value strategist.
- Project-vision editor.
- Operator/user-experience critic.
- Runtime reliability investigator.
- Security/privacy reviewer.
- Architecture/Ousterhout reviewer.
- Simplification/deletion reviewer.
- Test/verification reviewer.
- Docs/onboarding reviewer.
- Ops/infrastructure reviewer.
- Agent-readiness/harness reviewer.
- External exemplar scout.
- Premise challenger.

For small repos, combine lanes only when the same evidence answers both questions.
For important repos, add lanes instead of removing them.

Require each lane to return:

```markdown
**<Lane> Report**
Top Findings
1. <finding> -- Evidence: <file:line, command, URL, artifact>. Impact: high|med|low.
2. ...
World-Class Delta
<What would have to be true for this surface to be excellent?>
Backlog Move
<One epic, ticket, deletion, consolidation, or "no emission" with rationale.>
```

## Evidence Standard

Exhaustive work still needs precision.

- Cite live files, commands, URLs, artifacts, receipts, screenshots, or
  rendered surfaces.
- Label hypotheses as hypotheses.
- Verify each candidate emission against the repo before writing it.
- Prefer epics with children for coherent ambitions.
- Keep deletion and consolidation candidates visible even when you do not apply
  them.
- Never use a backlog count as a veto.

## Output Shape

Include these sections in the final groom report:

1. **Source Matrix**: every surface/lane, status, evidence, and contribution.
2. **Project Vision**: canonical artifact read or proposed; audience,
   job-to-be-done, category, standards, non-goals, bets, and 6-12 month target.
3. **World-Class Target**: the best version of the project in concrete terms.
4. **Gap Map**: what live evidence says is missing or weak by surface.
5. **Verification Map**: missing or weak gates, QA paths, evals, benchmarks,
   probes, repo-local verification skills, and secret/content/metadata leak
   checks. Treat missing commit-message, outbound-range, PR-body, log, and
   generated-artifact scanning as agent-readiness gaps unless the repo has a
   stronger server-side control.
6. **Strategy Themes**: 4-8 themes, each with recommendation first and evidence
   second.
7. **Backlog Diff**: applied ticket edits/emissions and proposed deletions.
8. **Sequence**: now, next, later, and blocked.
9. **Best Next Pickup**: one concrete next issue and why it outranks the rest.
10. **Residual Risk**: skipped surfaces, failed lanes, missing credentials,
   uncertain external facts, and stale evidence.

## Emission Bar

A strategic groom is incomplete when it emits only a tiny issue set, unless the
user explicitly asks for narrow triage.
A healthy mega groom usually produces some mix of:

- A few P0/P1 safety or correctness moves.
- Several strategic epics with ordered children.
- Small ready tickets that remove immediate friction.
- Deletion/consolidation proposals.
- A world-class plan artifact when the repo needs shared direction.

Do not add low-value tickets to pad the output.
Do not stop at the first credible theme.
Keep searching until the coverage map has an honest answer.

## Gotchas

- **Too few tickets.** Three issues can be the top of the list, not the groom.
  If only three survive, show the matrix that rejected every other candidate.
- **Vision without evidence.** A beautiful plan with no file, command, URL, or
  artifact evidence has no support.
- **Vision without effect.** A vision that does not change what gets emitted,
  deleted, sequenced, or rejected does not guide strategy.
- **Repeated prompts.** Many lanes with the same prompt duplicate one lane.
  Compose perspectives for the repo.
- **Unsequenced issues.** Many tickets without sequencing or shared themes are
  storage, not strategy.
- **Local maxima.** Ask what would make the project excellent in its category,
  not merely less broken.
