# Executable Oracles

An oracle is a check that decides whether a task succeeds.
Checkbox oracles can become unreliable. Executable oracles enforce the result.

## The Problem

Prose oracles require interpretation:
- "Auth should work" — what does "work" mean?
- "Response time should be fast" — how fast?
- "Tests should pass" — which tests?

These statements become matters of opinion.
The builder can claim success while the critic disagrees, and the team has no
objective result to check.

## The Fix: Oracles as Commands

Make every oracle a command that returns pass/fail:

```bash
# Bad: "The login endpoint should return 200 with valid credentials"
# Good:
curl -sf -X POST localhost:3000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","pass":"test123"}' \
  | jq -e '.token != null'

# Bad: "All auth tests should pass"
# Good:
pytest tests/auth/ -x -q

# Bad: "Response time should be reasonable"
# Good:
ab -n 100 -c 10 http://localhost:3000/api/health | grep -q 'Time per request.*[0-9]\.' \
  && echo "p99 < 1s" || exit 1

# Bad: "No regressions"
# Good:
npm test -- --bail 2>&1 | tail -1 | grep -q 'passed'
```

## Template

Write the Oracle section of a context packet:

```markdown
## Oracle (Definition of Done)

Commands that must all exit 0:
- `pytest tests/auth/ -x -q` — existing auth tests pass
- `curl -sf localhost:3000/api/users/me -H "Authorization: Bearer $TOKEN" | jq -e '.id'` — new endpoint works
- `npm run typecheck` — no type errors introduced
- `git diff --stat | wc -l | awk '$1 < 20'` — diff stays reviewable

Observable outcomes (verified by a human or `verifier`):
- Login page renders the new OAuth button
- Clicking it redirects to provider, then back with session
```

Split into two categories:
1. **Automated** — commands that CI or a Stop check can run
2. **Observable** — outcomes that require visual or interactive verification

Automated oracles are the primary gate.
Observable outcomes cover layout, UX flow, and visual correctness that scripts
cannot verify.

## When You Can't Write an Oracle

If you cannot write an executable oracle, the goal is not clear enough.
Review the specification again. Common causes:
- Goal is too vague ("improve performance")
- Success depends on subjective judgment with no proxy metric
- The feature needs test infrastructure that does not exist yet

For the third case, build the test infrastructure first.
