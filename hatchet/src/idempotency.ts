import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { z } from "zod";
import { idempotencyRoot } from "./config.js";
import { prWorkflowInputSchema, type PrWorkflowInput } from "./contracts.js";
import { DeterministicInputError } from "./errors.js";

const legacyMappingSchema = z.object({
  version: z.literal(1),
  fingerprint: z.string().regex(/^[0-9a-f]{64}$/),
  runId: z.string().min(1),
  createdAt: z.string().datetime(),
});

const mappingSchema = z.object({
  version: z.literal(2),
  fingerprint: z.string().regex(/^[0-9a-f]{64}$/),
  runId: z.string().min(1),
  createdAt: z.string().datetime(),
  input: prWorkflowInputSchema,
});

const storedMappingSchema = z.union([legacyMappingSchema, mappingSchema]);
export type TriggerMapping = z.infer<typeof mappingSchema>;
type StoredMapping = z.infer<typeof storedMappingSchema>;

function keyHash(key: string): string {
  return createHash("sha256").update(key).digest("hex");
}

function triggerFingerprint(input: PrWorkflowInput): string {
  return createHash("sha256").update(JSON.stringify(input)).digest("hex");
}

async function readMapping(path: string): Promise<StoredMapping | undefined> {
  try {
    return storedMappingSchema.parse(JSON.parse(await readFile(path, "utf8")));
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined;
    throw error;
  }
}

function acceptExisting(
  mapping: StoredMapping,
  validateExisting: (input: PrWorkflowInput) => void,
): TriggerMapping {
  if (mapping.version === 1) {
    throw new DeterministicInputError(
      "idempotency key belongs to a legacy single-recipe trigger; use a new key",
    );
  }
  if (mapping.fingerprint !== triggerFingerprint(mapping.input)) {
    throw new DeterministicInputError("stored idempotency mapping fingerprint is invalid");
  }
  validateExisting(mapping.input);
  return mapping;
}

export async function withIdempotentTrigger(
  idempotencyKey: string,
  buildInput: () => Promise<PrWorkflowInput>,
  validateExisting: (input: PrWorkflowInput) => void,
  createRun: (input: PrWorkflowInput) => Promise<string>,
): Promise<{ mapping: TriggerMapping; duplicate: boolean }> {
  await mkdir(idempotencyRoot, { recursive: true, mode: 0o700 });
  const stem = keyHash(idempotencyKey);
  const mappingPath = resolve(idempotencyRoot, `${stem}.json`);
  const lockPath = resolve(idempotencyRoot, `${stem}.lock`);

  for (;;) {
    const existing = await readMapping(mappingPath);
    if (existing) {
      return { mapping: acceptExisting(existing, validateExisting), duplicate: true };
    }
    try {
      await mkdir(lockPath);
      break;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "EEXIST") throw error;
      await delay(50);
    }
  }

  try {
    const existing = await readMapping(mappingPath);
    if (existing) {
      return { mapping: acceptExisting(existing, validateExisting), duplicate: true };
    }

    const input = await buildInput();
    if (input.idempotencyKey !== idempotencyKey) {
      throw new DeterministicInputError("trigger builder changed the idempotency key");
    }
    const mapping: TriggerMapping = {
      version: 2,
      fingerprint: triggerFingerprint(input),
      runId: await createRun(input),
      createdAt: new Date().toISOString(),
      input,
    };
    const temporary = `${mappingPath}.${randomUUID()}.tmp`;
    await writeFile(temporary, `${JSON.stringify(mapping)}\n`, { encoding: "utf8", mode: 0o600, flag: "wx" });
    await rename(temporary, mappingPath);
    return { mapping, duplicate: false };
  } finally {
    await rm(lockPath, { recursive: true, force: true });
  }
}
