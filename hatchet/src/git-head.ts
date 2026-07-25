import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { shaSchema } from "./contracts.js";
import { DeterministicInputError } from "./errors.js";

const execFileAsync = promisify(execFile);

export async function currentHeadSha(cwd: string): Promise<string> {
  try {
    const { stdout } = await execFileAsync("git", ["-C", cwd, "rev-parse", "HEAD"], {
      encoding: "utf8",
      maxBuffer: 4096,
    });
    return shaSchema.parse(stdout.trim()).toLowerCase();
  } catch {
    throw new DeterministicInputError(`cannot resolve current git HEAD in ${cwd}`);
  }
}

export async function requireCurrentHead(cwd: string, expected: string, edge: string): Promise<void> {
  const actual = await currentHeadSha(cwd);
  if (actual !== expected.toLowerCase()) {
    throw new DeterministicInputError(`${edge} rejected stale head: expected ${expected}, current ${actual}`);
  }
}
