import { constants as fsConstants } from "node:fs";
import { access, readFile, stat } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import { recipePathsSchema } from "./contracts.js";

const sourceRoot = resolve(fileURLToPath(new URL("..", import.meta.url)));
export const hatchetRoot = resolve(process.env.HATCHET_ROOT ?? sourceRoot);
export const localRoot = resolve(process.env.HATCHET_LOCAL_ROOT ?? resolve(hatchetRoot, "local"));
export const tokenPath = resolve(localRoot, "hatchet-config", "authdisabled-token");
export const executionRoot = resolve(localRoot, "executions");
export const idempotencyRoot = resolve(localRoot, "idempotency");

const operatorConfigSchema = z.object({
  version: z.literal(1),
  cardId: z.string().min(1),
  repository: z.string().min(1),
  recipePaths: recipePathsSchema,
  cwd: z.string().min(1),
  task: z.string().min(1),
  powder: z.object({
    baseUrl: z.string().url(),
    apiTokenFile: z.string().min(1).optional(),
    readyStatus: z.string().min(1).default("ready"),
  }).strict().optional(),
}).strict();
export type OperatorConfig = z.infer<typeof operatorConfigSchema>;

export async function readWorkerToken(): Promise<string> {
  await access(tokenPath, fsConstants.R_OK);
  const metadata = await stat(tokenPath);
  if ((metadata.mode & 0o077) !== 0) {
    throw new Error(`refusing permissive token file mode at ${tokenPath}; expected 0600`);
  }
  const token = (await readFile(tokenPath, "utf8")).trim();
  if (token.length === 0) {
    throw new Error(`empty Hatchet token file at ${tokenPath}`);
  }
  return token;
}

export async function readOperatorConfig(path = process.env.HATCHET_OPERATOR_CONFIG ?? resolve(localRoot, "operator.json")): Promise<OperatorConfig> {
  const parsed: unknown = JSON.parse(await readFile(resolve(path), "utf8"));
  return operatorConfigSchema.parse(parsed);
}

export const clientEndpoint = Object.freeze({
  hostPort: process.env.HATCHET_CLIENT_HOST_PORT ?? "127.0.0.1:7077",
  apiUrl: process.env.HATCHET_CLIENT_API_URL ?? "http://127.0.0.1:8888",
});
