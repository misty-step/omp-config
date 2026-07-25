import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

// Simulates a recipe agent whose first attempt calls the typed terminal tool
// with schema-invalid arguments (missing headSha) and whose second attempt
// calls it with conforming arguments. Attempt count is persisted to a file
// because each Hatchet retry spawns a fresh `bun` process with no shared
// in-memory state.
export async function startRecipeTask(options: {
  cwd: string;
  task: string;
  signal: AbortSignal;
  hostTools: Array<{
    execute(
      params: Record<string, unknown>,
      context: { signal: AbortSignal; sendUpdate(update: string): void },
    ): Promise<string>;
  }>;
}) {
  const counterPath = resolve(options.cwd, ".malformed-terminal-attempts");
  await mkdir(options.cwd, { recursive: true, mode: 0o700 });
  let attempt = 1;
  try {
    attempt = Number(await readFile(counterPath, "utf8")) + 1;
  } catch {
    attempt = 1;
  }
  await writeFile(counterPath, String(attempt), "utf8");

  const terminal = attempt < 2
    ? { version: 1, outcome: "completed", artifactRefs: [] }
    : { version: 1, outcome: "completed", headSha: "a".repeat(40), artifactRefs: [] };

  return {
    async wait() {
      await options.hostTools[0]!.execute(terminal, { signal: options.signal, sendUpdate() {} });
      return { text: "ignored" };
    },
    async stop() {},
  };
}
