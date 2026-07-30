// Input is assumed to have passed validateInputSemantics; this checks output persona IDs only.
import { collectDuplicateIds } from "./semantic-utils.mjs";
export function validateOutputSemantics(input, output) {
  const expectedIds = Array.isArray(input?.personas) ? input.personas.map((persona) => persona?.id) : [];
  const actualReports = Array.isArray(output?.personas) ? output.personas : [];
  const actualIds = actualReports.map((persona) => persona?.persona_id);
  const errors = [];

  collectDuplicateIds(actualIds, "output persona", errors);

  const expectedSet = new Set(expectedIds);
  const actualSet = new Set(actualIds);
  for (const id of expectedSet) {
    if (!actualSet.has(id)) errors.push(`missing output persona_id ${String(id)}`);
  }
  for (const id of actualSet) {
    if (!expectedSet.has(id)) errors.push(`unexpected output persona_id ${String(id)}`);
  }

  if (errors.length > 0) {
    throw new Error(`invalid qa-users output semantics: ${errors.join("; ")}`);
  }
  return { valid: true, persona_ids: expectedIds };
}
