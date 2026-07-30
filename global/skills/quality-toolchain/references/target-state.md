# Toolchain target-state rubric

Set one target per applicable surface in phase 2. Use
`global/references/quality-gates.md` for tiering (hard-block / ratchet /
report) and diff-scoped enforcement. A brownfield repo adopts strict targets
on changed code plus shrink-only ratchets on the legacy baseline.

## Lint

- One strict base ruleset per language, committed; warnings are errors on
  changed code.
- Project-specific rules: one mechanical rule per mistake this repo has
  actually made — custom ESLint rule, `ast-grep` pattern, Clippy
  `disallowed_methods`. Each rule cites the correction or incident it encodes.
- An inline disable requires a reason on the same line; the total disable
  count is a ratchet.
- Agent-shortcut checks are mechanical: growth of `as any` / `@ts-ignore` /
  `# type: ignore`, swallowed errors, `todo!()`-style stubs, dead scaffolding.

## Types

- Strictest viable checker mode (`tsc --strict`, `mypy --strict`, or the
  language equivalent). Relaxations are listed individually with reasons,
  never wholesale.
- Suppression markers are a ratchet; new code adds none.
- Typecheck runs in the fast gate.

## Build

- One repo-owned build command per artifact, reproducible given the lockfile.
- Dependencies are locked and resolved against the registry before install.
- Compiler warnings are errors where the language supports it.
- The build, or the cheapest whole-program compile check, runs no later than
  the full gate.

## Formatting

- One formatter per language; check mode in the fast gate; no style debate in
  review.

## Hooks

- Pre-commit runs in seconds: format check, changed-path lint, cheap secret
  scan over content and the commit message.
- Pre-push runs the fast gate: typecheck, focused or changed tests, remaining
  fast checks.
- A repo-owned setup command installs the hooks and the root docs name it. A
  fresh clone that skips it still hits the same contract in CI.
- Prove hooks live: verification includes one seeded bad commit or push
  attempt that the hook blocks.

## Observability

- Every gate has a name, one command, a tier (fast / full / scheduled), and a
  report path under `.evidence/` or the CI artifact store.
- Gate duration is recorded; a fast-gate budget breach is a finding.
- The assessment lists every gate. A check that exists but appears in no gate
  tier is a finding: folklore scripts are not gates.
