import { assertValidExecutionOverrides } from "./execution-validation.mjs";
import { resolveIssueThreshold } from "./threshold.mjs";

const OVERRIDE_DESCRIPTORS = Object.freeze([
  { outputField: "harness", readInput: (input) => readInputField(input, "harness") },
  { outputField: "provider", readInput: (input) => readInputField(input, "provider") },
  { outputField: "model", readInput: (input) => readInputField(input, "model") },
  { outputField: "reasoning", readInput: (input) => readInputField(input, "reasoning") },
  { outputField: "concurrency", readInput: (input) => readInputField(input, "concurrency") },
  { outputField: "session_length_seconds", readInput: (input) => readInputField(input, "session_length_seconds") },
  { outputField: "seed", readInput: (input) => readInputField(input, "seed") },
  {
    outputField: "entrypoints",
    readInput: (input) => {
      const override = readOverride(input, "entrypoints");
      if (override !== undefined) return override;
      return Array.isArray(input?.entrypoints) ? input.entrypoints.map((entrypoint) => entrypoint?.id) : undefined;
    },
    normalize: normalizeEntrypoints,
  },
  { outputField: "issue_threshold", readInput: (input) => readInputField(input, "issue_threshold"), normalize: normalizeThreshold },
  { outputField: "maximum_creates", readInput: (input) => readInputField(input, "maximum_creates") },
  {
    outputField: "selected_tracker",
    readInput: (input) => {
      const override = readOverride(input, "tracker");
      return override !== undefined ? override : input?.tracker?.selected;
    },
    normalize: normalizeTracker,
  },
]);


export function resolveExecutionOverrides(input, { cli = {}, harnessDefaults = {} } = {}) {
  const normalizedInput = Object.fromEntries(
    OVERRIDE_DESCRIPTORS.map(({ outputField, readInput }) => [outputField, readInput(input)]),
  );
  const values = {};
  const provenance = {};

  for (const descriptor of OVERRIDE_DESCRIPTORS) {
    const selected = selectSource(descriptor.outputField, normalizedInput, cli, harnessDefaults);
    const normalized = descriptor.normalize
      ? descriptor.normalize(selected.value, { input, source: selected.source })
      : selected.value;
    const provenanceEntry = { source: selected.source };
    values[descriptor.outputField] = normalized;
    if (descriptor.outputField === "issue_threshold") {
      values[descriptor.outputField] = normalized.threshold;
      provenanceEntry.rule = normalized.rule;
    }
    provenance[descriptor.outputField] = provenanceEntry;
  }

  validateEntrypointAssignments(input, values.entrypoints, provenance.entrypoints.source);
  assertValidExecutionOverrides(values, provenance);
  return { ...values, provenance };
}

function selectSource(outputField, normalizedInput, cli, harnessDefaults) {
  const sources = [
    ["cli", readOutputField(cli, outputField)],
    ["input", normalizedInput[outputField]],
    ["harness-default", readOutputField(harnessDefaults, outputField)],
  ];
  const selected = sources.find(([, value]) => value !== undefined);
  if (!selected) throw new Error(`no execution override value for ${outputField}`);
  return { source: selected[0], value: selected[1] };
}

function readOutputField(source, outputField) {
  if (!source || typeof source !== "object" || !Object.hasOwn(source, outputField)) return undefined;
  return source[outputField];
}

function readInputField(input, field) {
  const override = readOverride(input, field);
  return override !== undefined ? override : input?.[field];
}

function readOverride(input, field) {
  const overrides = input?.execution_overrides;
  return overrides && typeof overrides === "object" && Object.hasOwn(overrides, field)
    ? overrides[field]
    : undefined;
}

function normalizeEntrypoints(value, { source }) {
  if (!Array.isArray(value) || value.length === 0 || !value.every((id) => typeof id === "string" && id.length > 0)) {
    throw new Error(`execution override entrypoints from ${source} must be a nonempty array of nonempty strings`);
  }
  return value;
}

function normalizeThreshold(value, { input, source }) {
  try {
    if (value && typeof value === "object") return resolveIssueThreshold(value, "configured");
    return resolveIssueThreshold(input?.issue_threshold, value ?? "configured");
  } catch (error) {
    throw new Error(`invalid issue_threshold from ${source}: ${error.message}`);
  }
}

function normalizeTracker(value) {
  if (typeof value !== "string" || value.length === 0) throw new Error("selected tracker must be a nonempty string");
  return value;
}

function validateEntrypointAssignments(input, resolvedEntrypoints, source) {
  const declaredEntrypoints = Array.isArray(input?.entrypoints) ? input.entrypoints.map((entrypoint) => entrypoint?.id) : [];
  const declaredSet = new Set(declaredEntrypoints);
  const resolvedSet = new Set(resolvedEntrypoints);
  if (resolvedSet.size !== resolvedEntrypoints.length) {
    throw new Error(`resolved entrypoint IDs from ${source} must be unique`);
  }
  for (const id of resolvedEntrypoints) {
    if (!declaredSet.has(id)) throw new Error(`resolved entrypoint ID ${id} from ${source} is not declared in input`);
  }
  for (const persona of input?.personas ?? []) {
    for (const id of persona?.entrypoint_ids ?? []) {
      if (!resolvedSet.has(id)) {
        throw new Error(`resolved entrypoint set from ${source} omits persona ${String(persona?.id)} entrypoint ${id}`);
      }
    }
  }
}
