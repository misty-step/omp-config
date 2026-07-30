import Ajv from "ajv/dist/2020.js";
import { readFileSync } from "node:fs";

const executionSchema = JSON.parse(readFileSync(new URL("./execution.schema.json", import.meta.url), "utf8"));
const ajv = new Ajv({ allErrors: true, strict: true });
ajv.addSchema(executionSchema, "execution.v1.json");
const validate = ajv.compile({ $ref: "execution.v1.json#/$defs/output_overrides" });

export function assertValidExecutionOverrides(values, provenance) {
  const document = { ...values, provenance };
  if (validate(document)) return;
  const details = (validate.errors ?? []).map((error) => {
    const field = error.instancePath.split("/")[1] ?? "execution_overrides";
    const source = provenance?.[field]?.source;
    return `${field}${source ? ` from ${source}` : ""} ${error.message}`;
  });
  throw new Error(`invalid execution overrides: ${details.join("; ")}`);
}
