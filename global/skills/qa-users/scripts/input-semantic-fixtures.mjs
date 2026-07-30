import { validateInputSemantics } from "../references/input-semantic.mjs";
import { assertAccepted, assertRejected, deepEqual } from "./integrity-helpers.mjs";

function materializeInput(baseInput, fixtureInput) {
  return {
    ...baseInput,
    ...fixtureInput,
    execution_overrides: {
      ...baseInput.execution_overrides,
      ...fixtureInput.execution_overrides,
    },
  };
}

export function runInputSemanticFixtures({ readJson, baseInput, fail }) {
  const fixtures = readJson("references/input-semantic-fixtures.json");
  if (fixtures.schema_version !== "qa-users.input-semantic-fixtures.v1") {
    fail("input semantic fixture contract version drifted");
  }
  for (const fixture of fixtures.valid ?? []) {
    const input = materializeInput(baseInput, fixture.input ?? fixture);
    assertAccepted(`valid input semantic fixture ${fixture.name}`, () => {
      const result = validateInputSemantics(input);
      if (fixture.effective_entrypoint_ids && !deepEqual(result.effective_entrypoint_ids, fixture.effective_entrypoint_ids)) {
        throw new Error("effective entrypoint fixture drifted");
      }
      if (fixture.issue_threshold && !deepEqual(result.issue_threshold, fixture.issue_threshold)) {
        throw new Error("issue threshold fixture drifted");
      }
      if (fixture.issue_threshold_rule && result.issue_threshold_rule !== fixture.issue_threshold_rule) {
        throw new Error("issue threshold rule fixture drifted");
      }
    }, fail);
  }
  for (const fixture of fixtures.invalid ?? []) {
    const input = materializeInput(baseInput, fixture.input);
    assertRejected(`invalid input semantic fixture ${fixture.name}`, () => {
      try {
        validateInputSemantics(input);
      } catch {
        throw new Error("rejected");
      }
    }, fail);
  }
}
