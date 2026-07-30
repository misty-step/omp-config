import { validateOutputSemantics } from "../references/output-semantic.mjs";
import { assertAccepted, assertRejected } from "./integrity-helpers.mjs";

export function runOutputSemanticFixtures({ readJson, fail }) {
  const fixtures = readJson("references/output-semantic-fixtures.json");
  if (fixtures.schema_version !== "qa-users.output-semantic-fixtures.v1") {
    fail("output semantic fixture contract version drifted");
  }
  for (const fixture of fixtures.valid ?? []) {
    assertAccepted(`valid output semantic fixture ${fixture.name}`, () => {
      validateOutputSemantics(fixture.input, fixture.output);
    }, fail);
  }
  for (const fixture of fixtures.invalid ?? []) {
    assertRejected(`invalid output semantic fixture ${fixture.name}`, () => {
      try {
        validateOutputSemantics(fixture.input, fixture.output);
      } catch {
        throw new Error("rejected");
      }
    }, fail);
  }
}
