# /dispatch null-case eval

## Claim

Given a mixed-risk work item, `/dispatch` produces a focused composition that
selects the correct role, model/provider/reasoning level, hidden skills, MCPs,
tools, verifier, and lane contract. The chief does not execute specialist work.
A bare prompt should lose on at least two of three fixtures.

## Arms

- A: same-model chief with `/dispatch` visible and invoked.
- B: same-model chief with only the task and repository context.
- Grade blind. Remove role and skill names only when they reveal the arm rather
  than the decision quality.

## Fixtures

1. Medium-risk API implementation with an accepted contract, Powder card, and
   a new error path. Correct route: `builder` plus `deliver` and `ci`;
   Powder MCP; independent `qa` verifier.
2. High-risk production latency incident with Canary evidence and an unknown
   recent deploy. Correct route: `cassandra` plus `factory-apps`,
   `estate-infrastructure`, and `mint`; Canary MCP; reproduce before repair.
3. Meaningful structural diff that needs Cursor Thermo-Nuclear review and a
   release decision. Correct route: `reviewer` plus `code-review`,
   `peer-harnesses`, and `ci`; cross-family Cerberus and Cursor
   lanes; Scully verifies live claims.

## Objective checks

Each output must:

- contain the six manifest fields in the documented order;
- choose the expected primary role;
- name a real preferred model/provider and supported reasoning level;
- assign specialist skills to the lane, not the chief;
- name only MCPs and tools required by the fixture;
- add the required independent verifier;
- state outcome, authority, scope, oracle, output, dependencies, and non-goals;
- keep final integration and judgment with the chief.

A nonexistent role, skill, model, provider, or MCP fails the fixture. A generic
`task` worker fails when a declared role fits.

## Rubric

Score each dimension from 1 to 5:

1. role and authority fit;
2. model/provider/reasoning fit;
3. primitive focus and absence of unrelated load;
4. verification independence;
5. executable lane contract;
6. chief-versus-specialist boundary.

## Decision

Keep only when A wins at least two of three fixtures, no objective check fails,
and the grader can select B. Adapt on a routing miss. Cut when current frontier
models match the composition without the skill.

## Cadence

Run all fixtures after model palette, provider policy, agent frontmatter,
primitive routes, or OMP skill-loading mechanics change. Also run after a major
model release.
