# Repo-Local Skill Generation

Use this when a domain agent is being stood up to work in a specific repo.
Use it for a resident lane or an orchestrator-dispatched subagent.
Use it when the global catalog is too broad or is not installed there.
Do not sync the whole catalog.
Read the repo's real facts and write one or two skills that could not exist
elsewhere.
Name the repo's actual commands, not a genre of command.

Exemplar: a resident lane wrote `.agents/skills/canary-qa/SKILL.md` by hand.
This QA skill uses Canary's own `bin/validate`, HTTP routes, CLI, and webhook
rehearsal script.
It has no invented process and no generic "run the tests" prose.
This skill proves the pattern works.
The first pass skipped two things:
a provenance header and an eval stub.
The header tells future readers that generation, not hand authorship, created
the skill.
The eval stub routes the falsifiable claim through `/skill-eval`.

## Boundary: this is not `/tailor` again

The predecessor Harness Kit tried whole-repo harness generation twice.
It retired the approach both times.
The audit found roughly 60% ceremony; agent judgment was simpler and better.
Do not rebuild that machinery.
Do not add a manifest schema, automatic-rollback A/B harness, skill-cap
pre-commit hook, or planner/critic dialectic loop without fresh measured
evidence.
This pattern generates **one to three focused skills**, not a harness.
Do not add a manifest, killswitch, lint hook, or state machine.
A lead agent reads a repo, decides what is worth generating, writes it, and
proves it once with a cold-agent smoke.
If a repo needs more than a handful of bespoke skills, declare a focused OMP
agent.
Give it a curated `autoloadSkills` list instead of hand-generating a pile.
Declared agents subset the existing skill catalog.
This pattern authors net-new repo-specific content that has no catalog
equivalent.

## Read the repo before writing anything

Read sources in this order.
Later sources correct earlier sources when they disagree:

1. `AGENTS.md` — the repo's own stated contract:
   gate command, base branch, red lines, and known-debt map.
2. `.github/workflows/*.yml` (or equivalent CI config) — what actually runs on
   a PR.
   It may differ from what `AGENTS.md` claims.
   A repo with no CI workflow has a fact worth naming in the generated skill.
   Do not smooth it over.
3. `bin/`, `scripts/`, root manifests (`Cargo.toml`, `package.json`) — the real
   invocable commands.
   Copy them verbatim.
   Never paraphrase them.
4. `docs/*.md` runbooks — deploy, DR, migration, and onboarding docs that
   encode procedures too specific to derive from code alone.
5. Root `SKILL.md`, if the repo ships one — this is almost always the
   **product** skill for agents that use the thing this repo builds.
   Do not confuse it with a skill for agents building the repo.
   Do not duplicate its content.
6. The registry-routed work board — open debt and priority context that shape
   which domain is worth encoding now versus later.

## Pick a domain with a drivable oracle

Rank candidate domains by whether a cold agent can run a real action and observe
pass/fail, not by topic importance:

- **Verification/QA** is almost always the strongest first domain.
  Every repo has a shape and a real command to exercise it.
  Shape taxonomy: browser app, API/service, CLI, library, MCP, hybrid.
- **Deploy/release runbooks** are the second-strongest.
  Use a real deploy command and a real rollback/DR path.
  These paths usually appear in `docs/*.md`.
  Collect them into agent-executable form.
- Skip domains without a falsifiable check.
  "Architecture", "conventions", and "style" have no oracle a cold agent can
  run.
  A generated skill in one of these domains is prose without a falsifier.
  If the repo needs this material, put it in `AGENTS.md`, not a generated
  skill.

Generating more than two or three skills in one pass means you are building a
bundle, not authoring bespoke content.
Stop and reconsider role-scoped bundles.

## Name and place the file

- Path: `<target-repo>/.agents/skills/<repo>-<domain>/SKILL.md` — for example,
  `canary-qa`, `powder-qa`, `canary-deploy`.
  The repo prefix is load-bearing.
  It prevents the generated skill from shadowing a first-party omp-config skill
  name (`qa`, `deploy`).
  It also makes provenance clear from the directory name.
- Never write into omp-config's own tree.
  `.agents/skills/` in the target repo is the portable root.
  Write there directly.
  No separate per-harness bridge directory syncs from it.
- Copy `templates/repo-local-skill/SKILL.md.tmpl` as the starting shape.
  Keep frontmatter (`name`, `description` with explicit `Use when:`/`Trigger:`
  phrasing, `argument-hint`), the provenance comment block, a surfaces/routes
  table, exact commands, gotchas, and a report contract.
  Use the `canary-qa` exemplar, scaled to what this repo actually has.

## Provenance header

Every generated `SKILL.md` carries an HTML comment immediately after the
frontmatter closing `---`, before the first heading:

```markdown
<!--
Generated via omp-config's repo-local skill generation pattern
(global/skills/harness-engineering/references/repo-local-skill-generation.md).
Source repo: <owner/repo> @ <sha>. Generated: <YYYY-MM-DD>.
Generator ref: omp-config@<sha used to generate this>.
Facts below are repo-derived at generation time, not invented. Re-verify
commands against the live repo before trusting this if it has aged — a
generated skill is a snapshot, not a live view.
-->
```

This is new.
No existing generated repo-local skill in the fleet carries this header.
(`canary-qa` predates this convention and is not retrofitted by this change.)
It stays as committed.
Its lane's work is not overwritten.
Every skill that this pattern generates from now on carries the header.
The header tells future readers that generation, not hand authorship, created
the content.
It also helps readers judge staleness.

## Eval stub — the evals-per-skill floor extended to generated skills

Copy `templates/repo-local-skill/evals/eval-stub.md.tmpl` to
`<target-repo>/.agents/skills/<repo>-<domain>/evals/<repo>-<domain>-eval.md`.
This instrument is smaller than
`global/skills/skill-eval/templates/eval-spec.md` (omp-config's first-party
template).
It has one falsifiable claim and one to two fixtures built around a cold-agent
run.
Do not use a multi-arm A/B judge panel.
The claim is whether a cold agent executes the real command from this skill
alone, not whether it beats raw prompting by how much.
Use objective pass/fail checks and a run log.
Fill the run log with the actual cold-agent smoke transcript reference from
generation, not "PENDING".
Require the smoke before committing the skill (next section).
Real evidence should already exist.

## Validate before committing
1. **Run the flagship command yourself, once**, exactly as written in the
   generated skill, before you commit it.
   A generated skill whose one command 404s or has a mistyped flag is worse
   than no skill.
   It sends a cold agent into a debugging detour instead of saving one.
2. **Cold-agent smoke.** Dispatch a fresh-context agent without session memory
   of this generation work.
   Give it only the generated skill file and normal repo read access.
   Ask it to use the skill for one real, ideally read-only, action.
   Capture the transcript as the eval stub's first run-log entry and as the PR's
   evidence.
   The author driving the generated skill is not evidence under the shared
   no-self-review doctrine.
3. Commit only the new `.agents/skills/<repo>-<domain>/` files.
   Never stage or touch unrelated in-flight changes in the target repo.
   Check `git status` first.
   If another lane has uncommitted work on the checkout, use a worktree instead
   of the shared working tree.

## Anti-goals

- No manifest, A/B eval infrastructure, rollback, or lint-enforced skill cap.
  See the boundary section above.
- Do not shadow a first-party omp-config skill name.
- Do not touch the target repo's root `SKILL.md`, its `AGENTS.md`, or its gate
  contract.
  This pattern adds a skill; it does not rewrite the repo's doctrine.
- Do not regenerate or overwrite an existing hand-authored or previously
  generated skill without a reason in the PR.
  Add content by default.
