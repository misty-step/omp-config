import { validateInputSemantics } from "../references/input-semantic.mjs";
import { assertRejectsWithExactMessage, assertRejectsWithMessage } from "./integrity-helpers.mjs";

function materializeInput(baseInput, fixture) {
  const input = {
    ...baseInput,
    ...(fixture.input_without_entrypoints
      ? { entrypoints: undefined }
      : fixture.declared_entrypoint_ids
        ? { entrypoints: fixture.declared_entrypoint_ids.map((id) => ({ id })) }
        : {}),
  };
  if (fixture.input_without_field) {
    input[fixture.field] = undefined;
    if (fixture.field === "issue_threshold") {
      input.execution_overrides = { ...baseInput.execution_overrides, issue_threshold: undefined };
    }
  }
  return input;
}

function materializeValue(fixture) {
  if (fixture.value_kind === "NaN") return Number.NaN;
  if (fixture.value_kind === "Infinity") return Number.POSITIVE_INFINITY;
  if (fixture.value_kind === "-Infinity") return Number.NEGATIVE_INFINITY;
  if (fixture.value && typeof fixture.value === "object") {
    return {
      ...fixture.value,
      ...(fixture.value.minimum_confidence_kind === "Infinity"
        ? { minimum_confidence: Number.POSITIVE_INFINITY }
        : {}),
    };
  }
  return fixture.value;
}

export function runResolverFixtures({ readJson, baseInput, fail }) {
  const fixtures = readJson("references/execution-resolver-fixtures.json");
  if (fixtures.schema_version !== "qa-users.execution-resolver-fixtures.v1") {
    fail("execution resolver fixture contract version drifted");
  }
  for (const fixture of fixtures.cases ?? []) {
    const input = materializeInput(baseInput, fixture);
    const options = fixture.source === "cli"
      ? { cli: { entrypoints: fixture.entrypoints } }
      : { harnessDefaults: { entrypoints: fixture.entrypoints } };
    assertRejectsWithMessage(
      `resolver fixture ${fixture.name}`,
      () => validateInputSemantics(input, options),
      fixture.error_fragment,
      fail,
    );
  }
  for (const fixture of fixtures.invalid_cases ?? []) {
    const input = materializeInput(baseInput, fixture);
    const override = { [fixture.field]: materializeValue(fixture) };
    const options = fixture.source === "cli" ? { cli: override } : { harnessDefaults: override };
    assertRejectsWithExactMessage(
      `resolver fixture ${fixture.name}`,
      () => validateInputSemantics(input, options),
      fixture.error,
      fail,
    );
  }
}
