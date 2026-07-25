import { mkdir, rm } from "node:fs/promises";
import { resolve } from "node:path";

export async function startRecipeTask(options: { cwd: string; signal: AbortSignal }) {
  const runtimeRoot = resolve(options.cwd, ".adapter-runtime");
  await mkdir(runtimeRoot, { mode: 0o700 });
  const completion = Promise.withResolvers<{ text: string }>();
  const abort = (): void => completion.reject(options.signal.reason ?? new Error("cancelled"));
  options.signal.addEventListener("abort", abort, { once: true });
  return {
    wait: () => completion.promise,
    async stop(): Promise<void> {
      options.signal.removeEventListener("abort", abort);
      await rm(runtimeRoot, { recursive: true, force: true });
    },
  };
}
