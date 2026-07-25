export class DeterministicInputError extends Error {
  override readonly name = "DeterministicInputError";
}

export class TransientRunnerError extends Error {
  override readonly name = "TransientRunnerError";
}

export class RunnerCancelledError extends Error {
  override readonly name = "RunnerCancelledError";
}

export class StageTimeoutError extends Error {
  override readonly name = "StageTimeoutError";
}

// Exit code recipe-runner-adapter.ts's main() returns when a stage hits its
// stageTimeoutMs backstop (12h) instead of finishing or genuinely erroring.
// A stage that trips this backstop is wedged, not unlucky: a fresh attempt
// would burn the same 12h again for no better odds. runner.ts's invokeRunner
// maps this exact code to StageTimeoutError (not TransientRunnerError) so
// invokeRunnerWithRetry consumes exactly one attempt instead of retrying a
// process that already proved it cannot converge in the allotted time.
// Distinct from the 64/65/66/78 deterministicExitCodes set: those mean "this
// input will fail identically forever" (sysexits usage/data/config errors);
// this means "this run outlived its time budget," an unrelated failure mode
// that happens to share the same non-retryable handling.
export const stageTimeoutExitCode = 82;
