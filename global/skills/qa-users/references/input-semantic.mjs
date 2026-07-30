import { collectDuplicateIds } from "./semantic-utils.mjs";
import { resolveExecutionOverrides } from "./execution-resolver.mjs";

const ALLOWED_ENVIRONMENTS = new Set(["local", "dev", "staging"]);

export function validateInputSemantics(input, { cli = {}, harnessDefaults = {} } = {}) {
  const errors = [];
  const personas = Array.isArray(input?.personas) ? input.personas : [];
  const entrypoints = Array.isArray(input?.entrypoints) ? input.entrypoints : [];
  const personaIds = personas.map((persona) => persona?.id);
  const entrypointIds = entrypoints.map((entrypoint) => entrypoint?.id);

  collectDuplicateIds(personaIds, "persona", errors);
  collectDuplicateIds(entrypointIds, "entrypoint", errors);
  for (const entrypoint of entrypoints) {
    if (!ALLOWED_ENVIRONMENTS.has(entrypoint?.environment)) {
      errors.push(`entrypoint ${String(entrypoint?.id)} environment must be local, dev, or staging`);
    }
  }

  let executionOverrides;
  try {
    executionOverrides = resolveExecutionOverrides(input, { cli, harnessDefaults });
  } catch (error) {
    errors.push(error.message);
  }

  if (errors.length > 0) {
    throw new Error(`invalid qa-users input semantics: ${errors.join("; ")}`);
  }
  return {
    valid: true,
    effective_entrypoint_ids: executionOverrides.entrypoints,
    issue_threshold: executionOverrides.issue_threshold,
    issue_threshold_rule: executionOverrides.provenance.issue_threshold.rule,
    execution_overrides: executionOverrides,
  };
}
