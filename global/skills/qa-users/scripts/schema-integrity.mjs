import { validateInputSemantics } from "../references/input-semantic.mjs";
import { validateOutputSemantics } from "../references/output-semantic.mjs";
import { assertRejected } from "./integrity-helpers.mjs";

export function runSchemaIntegrity({ schemaFixtures, validateInputSchema, validateOutputSchema, ajv, fail }) {
  if (!validateInputSchema(schemaFixtures.input)) {
    fail(`golden input schema validation failed: ${ajv.errorsText(validateInputSchema.errors)}`);
  }
  const semanticResult = validateInputSemantics(schemaFixtures.input);
  const outputs = Object.fromEntries(
    Object.entries(schemaFixtures.outputs).map(([name, report]) => [
      name,
      { ...report, execution_overrides: semanticResult.execution_overrides },
    ]),
  );
  for (const [name, report] of Object.entries(outputs)) {
    if (!validateOutputSchema(report)) {
      fail(`golden ${name} output schema validation failed: ${ajv.errorsText(validateOutputSchema.errors)}`);
    }
    try {
      validateOutputSemantics(schemaFixtures.input, report);
    } catch (error) {
      fail(`${name} output semantic validation failed: ${error.message}`);
    }
  }
  assertRejected(
    "invalid output fixture",
    () => {
      if (!validateOutputSchema(schemaFixtures.invalid.dry_run_phase_mismatch)) throw new Error("schema rejected");
    },
    fail,
  );
  return { semanticResult, outputs };
}
