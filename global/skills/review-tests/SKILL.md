---
disable-model-invocation: true
name: review-tests
description: |
  Test-quality lens for code-critic: given a diff and its acceptance oracle,
  judge whether the tests actually defend the changed contract or just run
  the changed lines. Covers mutation thinking, mock-boundary discipline, and
  weakened-assertion detection — checks with no public precedent. Read-only;
  produces findings only, never edits code or tests.
  Use when a diff adds or modifies tests, or when a green suite needs
  judgment beyond "it passed". Trigger: /review-tests.
---

# /review-tests

Judge test defense, not test presence. A green suite proves nothing by
itself; this lens asks whether the suite would notice if the changed
contract broke.

## Scope

Input: the diff and its acceptance oracle. No author-reasoning trail, no
chat history — judge the artifact as it stands (Shared Operating Spine:
Prove). Read-only. This skill never edits, writes, commits, or mutates
tracker state; it returns findings for the diff's author or the Fixer to
act on.

## Severity

- **blocking** — the suite would not catch the defect the change exists to
  prevent, or a test was weakened to hide a real failure. Must resolve
  before merge.
- **important** — couples tests to implementation, or leaves a real gap
  (missing boundary/transition/error case) that will produce false signals
  or blind spots later, without currently masking an active defect.
- **advisory** — worth naming, does not block: low-value edge case, minor
  setup duplication, a borderline call either way would be defensible.

`No blocking findings` is a valid, expected outcome. State it plainly when
every changed line is defended. Do not invent findings to justify the pass.

## Checks

1. **Kills a plausible bug.** Implement the most plausible wrong version of
   the changed logic — off-by-one, swapped comparison, missing guard — and
   check whether any test goes red. *Example:* `isEligible(age) { return age
   >= 18 }` tested only at `age = 25`. Break it to `age > 18`; every test
   still passes. Blocking — the boundary itself is untested.

2. **Mutation thinking.** For every line the diff touches, mentally apply
   each operator and ask which test dies: flip a boundary (`>=`↔`>`,
   `<`↔`<=`), invert a condition (`if (x)`→`if (!x)`), swap an arithmetic or
   logical operator (`+`↔`-`, `&&`↔`||`), delete or short-circuit an error
   branch (swallow the throw, drop the catch), stub a return with a default
   (`0`, `null`, `[]`, `true`), or drop a loop-bound adjustment (off-by-one
   on `<` vs `<=` in a `for`). If no test in the suite fails for a mutation
   on a changed line, that survivor is a blocking finding: name the exact
   line, the mutation, and which test should have caught it but didn't.
   *Example:* diff adds `if (retries > MAX_RETRIES) throw new
   RetryExhausted()`. Mutate to `>=`, or delete the `throw`: no test fails.
   Blocking.

3. **No internal-structure assertions.** Reject assertions on private
   methods, internal call counts, or implementation-shaped snapshots — they
   couple the test to the code's shape, not its contract, producing false
   greens on real breakage and false reds on safe refactors. *Example:*
   `expect(cache._evict).toHaveBeenCalledTimes(2)` passes even if eviction
   drops the wrong entry, and fails the moment eviction is inlined. Important,
   blocking if it is the only test guarding that contract.

4. **No mock of an internal seam.** A mock of a module or class the same
   repo owns hides the exact integration the change is supposed to prove.
   Legitimate mock surface is external I/O only: network, filesystem, clock,
   third-party SDK. *Example:* testing `OrderService.place` with
   `OrderValidator.validate` mocked out — if `OrderValidator` starts
   accepting negative quantities, this test never notices. Blocking when the
   mocked seam is the contract under test; important otherwise.

5. **Exercises the real entrypoint.** Trace the test from setup to
   assertion and confirm it actually reaches the changed lines — not a
   direct call to an inner helper that bypasses the wiring the diff changed.
   *Example:* diff changes validation inside the `POST /orders` route; the
   test calls `validateOrder()` directly while the route still wires the old
   validator. The route path is unverified. Blocking — theater.

6. **Boundaries, transitions, precedence, real errors.** Enumerate the
   changed function's boundary values, state transitions, precedence between
   competing matches, and thrown/returned error conditions; each needs an
   asserting test, not just the happy path. *Example:* a "highest discount
   wins" stacking rule tested only with one discount applied — no case where
   two discounts compete and the wrong one could silently win. Important,
   blocking if precedence is the point of the change.

7. **Deterministic and isolated.** No wall-clock or unseeded-random
   dependence, no order coupling between tests, no fixture mutated by more
   than one test, safe inside the full suite. *Example:* two tests share a
   module-level array; test A pushes a user, test B asserts its length —
   green alone, red after A runs first, flaky in CI. Blocking; a
   non-deterministic gate is not a gate.

8. **No weakened test.** A loosened matcher (`toBe(42)` →
   `toBeGreaterThan(0)`), a widened tolerance, an added `.skip`/`.only`/
   `xit`, a deleted assertion, or a narrowed input set that quietly drops the
   case the code broke on — each is blocking by default. *Example:* a prior
   exact-value assertion becomes a loose range check with no linked ticket or
   stated contract change in the diff. Treat it as hiding a failure until the
   diff proves otherwise.

## Fix vs. weaken

Hand this to whoever resolves a finding:

- Test fails because of a legitimate, intended behavior change → update the
  expectation, and say so in the diff.
- Test fails because the test is brittle (order-dependent, over-specified,
  coupled to structure) → make the test robust; do not touch its intent.
- Test fails because the code under test is wrong → report it. Never edit
  the code to please a test, and never edit the test to stop it complaining.
- Never weaken a test to make it pass. Loosening an assertion, widening a
  tolerance, adding `skip`/`only`, or narrowing a matcher to dodge a failing
  case is check 8, not a fix.

## Non-goals

- Coverage percentage as a proxy for quality. A 100%-covered suite that
  kills no mutants is weaker than a 60%-covered suite that kills every
  mutant on the changed lines.
- Formatting, import order, and lint violations — the linter's job.
- Test naming and file-organization bikeshedding.
- Demanding a test for pure plumbing with no observable contract: a
  one-line re-export, a type-only change, a config value threaded through
  unchanged.
