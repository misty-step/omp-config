export class DeterministicInputError extends Error {
  override readonly name = "DeterministicInputError";
}

export class TransientRunnerError extends Error {
  override readonly name = "TransientRunnerError";
}

export class RunnerCancelledError extends Error {
  override readonly name = "RunnerCancelledError";
}
