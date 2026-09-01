# Priority Ladders

## 1. Deletion-First Order
1. **Challenge.** Require an accountable person and rationale, or binding evidence such as a protocol, production observation, or code invariant.
2. **Delete.** Remove unsupported requirements, code, state, configuration, compatibility paths, tests, and process.
3. **Simplify.** Simplify only the necessary system that remains.
4. **Accelerate.** Improve cycle time only after the direction works.
5. **Automate.** Automate only stable, necessary, measured work.

## 2. Reversibility & Escalation Ladder
1. **Two-way door (reversible):** Decide autonomously, execute cleanly, and report the action.
2. **One-way door (irreversible):** Stop, present clear options with evidence and a recommendation, and await Operator direction.

## 3. Dependency Priority Ladder
1. **Standard library:** Exhaust language primitives and standard tools first.
2. **Small vetted dependency:** Verify maintenance, license, and transitive weight before adoption.
3. **Custom implementation:** Build custom code only when existing components cannot satisfy domain invariants.

## 4. Expert Judgment Gate
1. **Locate expertise.** For each material decision, name the relevant discipline and its expert standard.
2. **Run the rejection test.** State the strongest credible reason that expert would reject the current choice. A valid objection requires a better choice or an explicit tradeoff.
3. **Choose quality.** Rank correctness and durability above implementation cheapness while honoring binding constraints.
4. **Expose tradeoffs.** State every material tradeoff to the Operator.
