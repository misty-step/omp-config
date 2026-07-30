import { createFindingFingerprint } from "../references/finding-fingerprint.mjs";
import { assertAccepted } from "./integrity-helpers.mjs";

export function runFingerprintFixtures({ readJson, fail }) {
  const fixtures = readJson("references/finding-fingerprint-fixtures.json");
  if (fixtures.schema_version !== "qa-users.finding-fingerprint-fixtures.v1") {
    fail("finding fingerprint fixture contract version drifted");
  }
  for (const fixture of fixtures.cases ?? []) {
    assertAccepted(`fingerprint fixture ${fixture.name}`, () => {
      const fingerprint = createFindingFingerprint(fixture.finding);
      if (!new RegExp(fixture.expected_pattern).test(fingerprint)) throw new Error("fingerprint format drifted");
      if (fixture.equivalent && createFindingFingerprint(fixture.equivalent) !== fingerprint) {
        throw new Error("fingerprint normalization drifted");
      }
    }, fail);
  }
}
