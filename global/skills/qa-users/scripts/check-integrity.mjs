import Ajv from "ajv/dist/2020.js";
import { existsSync, readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { runFingerprintFixtures } from "./fingerprint-fixtures.mjs";
import { runInputSemanticFixtures } from "./input-semantic-fixtures.mjs";
import { runOutputSemanticFixtures } from "./output-semantic-fixtures.mjs";
import { runResolverFixtures } from "./resolver-fixtures.mjs";
import { runSchemaIntegrity } from "./schema-integrity.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");

function fail(message) {
  console.error(`qa-users integrity: FAIL ${message}`);
  process.exitCode = 1;
}

function requireFile(relativePath) {
  const path = join(root, relativePath);
  if (!existsSync(path) || !statSync(path).isFile()) fail(`missing file ${relativePath}`);
  return path;
}

function readJson(relativePath) {
  const path = requireFile(relativePath);
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    throw new Error(`qa-users integrity: FAIL invalid JSON ${relativePath}: ${reason}`, { cause: error });
  }
}

for (const relativePath of [
  "SKILL.md",
  "references/lifecycle.md",
  "references/safety.md",
  "references/tracker.md",
  "references/input-semantic.mjs",
  "references/input-semantic-fixtures.json",
  "references/semantic-utils.mjs",
  "references/output-semantic.mjs",
  "references/output-semantic-fixtures.json",
  "references/finding-fingerprint.mjs",
  "references/finding-fingerprint-fixtures.json",
  "references/execution-resolver.mjs",
  "references/execution-validation.mjs",
  "references/execution-resolver-fixtures.json",
  "references/threshold.mjs",
  "references/execution-overrides.md",
  "references/schema-fixtures.json",
  "references/omp.md",
  "scripts/integrity-helpers.mjs",
  "scripts/schema-integrity.mjs",
  "scripts/input-semantic-fixtures.mjs",
  "scripts/resolver-fixtures.mjs",
  "scripts/output-semantic-fixtures.mjs",
  "scripts/fingerprint-fixtures.mjs",
]) requireFile(relativePath);

const schemaFiles = new Map([
  ["input", readJson("references/input.schema.json")],
  ["persona", readJson("references/persona.schema.json")],
  ["tracker", readJson("references/tracker.schema.json")],
  ["execution", readJson("references/execution.schema.json")],
  ["output", readJson("references/output.schema.json")],
]);
const ajv = new Ajv({ allErrors: true, strict: true });
for (const schema of schemaFiles.values()) ajv.addSchema(schema);
const validateInputSchema = ajv.getSchema(schemaFiles.get("input").$id);
const validateOutputSchema = ajv.getSchema(schemaFiles.get("output").$id);
const schemaFixtures = readJson("references/schema-fixtures.json");

const { semanticResult } = runSchemaIntegrity({
  schemaFixtures,
  validateInputSchema,
  validateOutputSchema,
  ajv,
  fail,
});
runInputSemanticFixtures({ readJson, baseInput: schemaFixtures.input, fail });
runResolverFixtures({ readJson, baseInput: schemaFixtures.input, fail });
runOutputSemanticFixtures({ readJson, fail });
runFingerprintFixtures({ readJson, fail });

if (!semanticResult.execution_overrides?.provenance) fail("semantic result omitted execution override provenance");
if (process.exitCode) process.exit();
console.log("qa-users integrity: PASS");
