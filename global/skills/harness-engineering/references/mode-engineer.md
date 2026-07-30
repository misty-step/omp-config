# /harness-engineering engineer

Design harness improvements for hooks, enforcement, context, and codification.

## Codification hierarchy

When encoding knowledge, target the highest-leverage mechanism:

```
Type system > Lint rule > Hook > Test > CI > Skill > AGENTS.md > Memory
```

## The Design Test (Norman Principle)

For every harness component, apply the Norman test:

1. **Can an agent make this error?** — The harness permits it. Add prevention.
2. **Does the harness make this error likely?** — The harness induces it. Fix it
   urgently.
3. **After an error, does the response fix the system?** — If not, you teach
   burner mappings. Redesign the harness.

Prevention hierarchy: Type system > Hook > Lint > Test > Skill > Prose.
Treat prose as the burner label. Hooks are the redesigned stove.

## Local CI

For omp-config itself, run the Python-owned local gate:

```sh
bin/check
bin/check --installed   # also verifies the ~/.omp/agent projection
```

When adding gate coverage, keep deterministic config-contract checks inside
`bin/check`.
Put semantic quality in evals and fresh critics.
Do not make Dagger, Docker, GitHub Actions YAML, or provider CLIs the default
inner-loop gate for omp-config.

## Consumer repo gate velocity

When engineering CI defaults for other repos, encode a two-tier loop:

- **Inner loop:** Run fast deterministic checks in local hooks.
  Agents must tolerate these checks during amend/push cycles.
- **Outer loop:** Keep full Dagger/Docker/browser/network/live-readiness gates
  required before merge, main deploy, or an explicit ship command.

Slow pre-push gates are a harness defect when CI repeats the same expensive
proof.
Split `check-fast` from `ship-check`, add stale-PR concurrency cancellation,
or give Dagger a persistent/cloud engine cache.
Do not path-skip the only required workflow.
Skipped required GitHub checks can leave a PR pending.

## Verification systems

When a harness change affects agent behavior, runtime behavior, generated
artifacts, or operator trust, load
`../../../shared/references/verification-system-first.md`.
Name the driver, grader, evidence packet, and cadence before you edit.
A new primitive without a gate, eval, benchmark, QA path, smoke path, or probe
is unfinished.

## Hooks are the highest-leverage investment

Hooks run on every tool use.
`AGENTS.md` is read once.
A hook that blocks `rm -rf` is infinitely more reliable than an `AGENTS.md`
line that says "don't delete files."
Invest in hooks over prose.

Keep harness-native hooks in the owning harness or consumer repository.
omp-config composes session primitives (skills, agents, config, MCP).
It does not install or manage per-repo hook surfaces.

## AGENTS.md is a map, not a manual

Keep AGENTS.md under 100 lines.
Point it to deeper sources of truth (skills, references, docs/) instead of
putting all instructions inline.
A monolithic AGENTS.md becomes a graveyard of stale rules.

## Stress-test assumptions

Every harness component encodes an assumption about model limitations.
When a new model drops, ask whether this skill is still needed and whether this
hook still catches real problems.
Strip what is not load-bearing.

## Thin harness default

Default to a thin harness:

- define agents, tools, prompts, and boundaries
- launch them
- capture raw artifacts
- optionally synthesize with another agent

Do not default to semantic workflow engines, regex recovery of agent structure,
or heavy handoff machinery.
Reasoning about the repo or recovering meaning from free-form agent prose is a
strong smell.

## Workflow layering

When multiple skills touch the same delivery lane, enforce strict layering:

- **Leaf skills own one domain and run standalone.** Examples:
  `/ci`, `/research`.
- **Composer skills orchestrate leaves around one bounded objective.**
  Example: `/deliver`.
- **Outer-loop / event workflows are Mode B**, but no active event plane is
  available. Keep them out of new skills until a future product is explicitly
  named. See `../../shared/references/loop-readiness.md`.
- **Aliases are vocabulary, not new domains.**
  Do not add a skill when a trigger alias on an existing one covers the request.

Redundancy test:
- If a composer explains a leaf skill's internal method in detail, that is
  drift.
  The composer should invoke or reference the leaf.
  Add only the boundary judgment it owns.
- If two skills can both claim authority for the same concern, the boundary is
  wrong.
  Pick one owner and make the other compose it.
