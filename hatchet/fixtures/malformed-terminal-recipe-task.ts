import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

// Simulates a recipe agent whose first attempt returns a terminal object that
// fails runnerTerminalSchema validation (missing headSha) and whose second
// attempt returns a conforming terminal. Attempt count is persisted to a file
// because each Hatchet retry spawns a fresh `bun` process with no shared
// in-memory state.
export async function startRecipeTask(options: { cwd: string; task: string; signal: AbortSignal }) {
  const counterPath = resolve(options.cwd, ".malformed-terminal-attempts");
  await mkdir(options.cwd, { recursive: true, mode: 0o700 });
  let attempt = 1;
  try {
    attempt = Number(await readFile(counterPath, "utf8")) + 1;
  } catch {
    attempt = 1;
  }
  await writeFile(counterPath, String(attempt), "utf8");

  const text = attempt < 2
    ? JSON.stringify({ version: 1, outcome: "completed", artifactRefs: [] })
    : JSON.stringify({ version: 1, outcome: "completed", headSha: "a".repeat(40), artifactRefs: [] });

  return {
    async wait() { return { text }; },
    async stop() {},
  };
}
