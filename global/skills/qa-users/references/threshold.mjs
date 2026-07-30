const STRICTER_SEVERITY = Object.freeze({
  info: "low",
  low: "medium",
  medium: "high",
  high: "critical",
  critical: "critical",
});
const STRICTER_CONFIDENCE_INCREMENT = 0.1;

export function resolveIssueThreshold(inputThreshold, mode = "configured") {
  if (!inputThreshold || typeof inputThreshold !== "object") {
    throw new Error("issue_threshold input is required for deterministic resolution");
  }
  const minimumSeverity = inputThreshold.minimum_severity;
  const minimumConfidence = inputThreshold.minimum_confidence;
  if (
    !Object.hasOwn(STRICTER_SEVERITY, minimumSeverity) ||
    typeof minimumConfidence !== "number" ||
    !Number.isFinite(minimumConfidence) ||
    minimumConfidence < 0 ||
    minimumConfidence > 1
  ) {
    throw new Error("issue_threshold minimum_confidence must be finite and between 0 and 1");
  }
  if (mode === "configured") {
    return {
      threshold: { minimum_severity: minimumSeverity, minimum_confidence: minimumConfidence },
      rule: "configured",
    };
  }
  if (mode === "stricter") {
    return {
      threshold: {
        minimum_severity: STRICTER_SEVERITY[minimumSeverity],
        minimum_confidence: Math.min(1, Number((minimumConfidence + STRICTER_CONFIDENCE_INCREMENT).toFixed(6))),
      },
      rule: "stricter.v1",
    };
  }
  throw new Error(`issue_threshold override must be configured or stricter, got ${String(mode)}`);
}
