import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, rename, rm, stat, writeFile } from "node:fs/promises";
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

const lockOwnerSchema = z.object({
  pid: z.number().int().positive(),
  createdAt: z.string().datetime(),
  token: z.string().uuid(),
}).strict();
type LockOwner = z.infer<typeof lockOwnerSchema>;

export type IdempotencyLockOptions = {
  staleAfterMs?: number;
  waitTimeoutMs?: number;
  retryDelayMs?: number;
  isProcessAlive?: (pid: number) => boolean;
};

const DEFAULT_STALE_AFTER_MS = 15 * 60_000;
const DEFAULT_WAIT_TIMEOUT_MS = 30_000;
const DEFAULT_RETRY_DELAY_MS = 50;

function positiveInteger(value: number | undefined, fallback: number, name: string): number {
  const resolved = value ?? fallback;
  if (!Number.isSafeInteger(resolved) || resolved < 1) {
    throw new Error(`${name} must be a positive integer`);
  }
  return resolved;
}

function localProcessIsAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return (error as NodeJS.ErrnoException).code !== "ESRCH";
  }
}

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

async function readLockOwner(lockPath: string): Promise<LockOwner | undefined> {
  try {
    const parsed = lockOwnerSchema.safeParse(
      JSON.parse(await readFile(resolve(lockPath, "owner.json"), "utf8")),
    );
    return parsed.success ? parsed.data : undefined;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined;
    if (error instanceof SyntaxError) return undefined;
    throw error;
  }
}

async function inspectLock(
  lockPath: string,
  staleAfterMs: number,
  isProcessAlive: (pid: number) => boolean,
): Promise<"active" | "gone" | "stale"> {
  const owner = await readLockOwner(lockPath);
  if (owner) {
    // A valid, live local PID always wins, even after the age threshold. The
    // threshold only recovers abandoned locks whose owner cannot be proven
    // alive (for example, SIGKILL before owner.json was fully written).
    return isProcessAlive(owner.pid) ? "active" : "stale";
  }
  try {
    const metadata = await stat(lockPath);
    return Date.now() - metadata.mtimeMs >= staleAfterMs ? "stale" : "active";
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return "gone";
    throw error;
  }
}

async function quarantineStaleLock(lockPath: string): Promise<boolean> {
  const quarantinePath = `${lockPath}.quarantine-${randomUUID()}`;
  try {
    await rename(lockPath, quarantinePath);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return false;
    throw error;
  }
  await rm(quarantinePath, { recursive: true });
  return true;
}

async function acquireLock(lockPath: string, owner: LockOwner): Promise<void> {
  await mkdir(lockPath, { mode: 0o700 });
  try {
    await writeFile(resolve(lockPath, "owner.json"), `${JSON.stringify(owner)}\n`, {
      encoding: "utf8",
      mode: 0o600,
      flag: "wx",
    });
  } catch (error) {
    await rm(lockPath, { recursive: true, force: true });
    throw error;
  }
}

async function releaseOwnedLock(lockPath: string, token: string): Promise<void> {
  const owner = await readLockOwner(lockPath);
  if (!owner || owner.token !== token) return;

  const releasePath = `${lockPath}.release-${token}`;
  try {
    await rename(lockPath, releasePath);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return;
    throw error;
  }
  const movedOwner = await readLockOwner(releasePath);
  if (!movedOwner || movedOwner.token !== token) {
    throw new Error("idempotency lock ownership changed during release");
  }
  await rm(releasePath, { recursive: true });
}

export async function withIdempotentTrigger(
  idempotencyKey: string,
  buildInput: () => Promise<PrWorkflowInput>,
  validateExisting: (input: PrWorkflowInput) => void,
  createRun: (input: PrWorkflowInput) => Promise<string>,
  lockOptions: IdempotencyLockOptions = {},
): Promise<{ mapping: TriggerMapping; duplicate: boolean }> {
  await mkdir(idempotencyRoot, { recursive: true, mode: 0o700 });
  const stem = keyHash(idempotencyKey);
  const mappingPath = resolve(idempotencyRoot, `${stem}.json`);
  const lockPath = resolve(idempotencyRoot, `${stem}.lock`);
  const staleAfterMs = positiveInteger(
    lockOptions.staleAfterMs,
    DEFAULT_STALE_AFTER_MS,
    "staleAfterMs",
  );
  const waitTimeoutMs = positiveInteger(
    lockOptions.waitTimeoutMs,
    DEFAULT_WAIT_TIMEOUT_MS,
    "waitTimeoutMs",
  );
  const retryDelayMs = positiveInteger(
    lockOptions.retryDelayMs,
    DEFAULT_RETRY_DELAY_MS,
    "retryDelayMs",
  );
  const isProcessAlive = lockOptions.isProcessAlive ?? localProcessIsAlive;
  const deadline = Date.now() + waitTimeoutMs;
  const owner: LockOwner = {
    pid: process.pid,
    createdAt: new Date().toISOString(),
    token: randomUUID(),
  };

  for (;;) {
    const existing = await readMapping(mappingPath);
    if (existing) {
      return { mapping: acceptExisting(existing, validateExisting), duplicate: true };
    }
    try {
      await acquireLock(lockPath, owner);
      break;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "EEXIST") throw error;
      const state = await inspectLock(lockPath, staleAfterMs, isProcessAlive);
      if (state === "gone") continue;
      if (state === "stale") {
        await quarantineStaleLock(lockPath);
        continue;
      }
      const remainingMs = deadline - Date.now();
      if (remainingMs <= 0) {
        throw new Error(`timed out waiting for active idempotency lock after ${waitTimeoutMs}ms`);
      }
      await delay(Math.min(retryDelayMs, remainingMs));
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
    await writeFile(temporary, `${JSON.stringify(mapping)}\n`, {
      encoding: "utf8",
      mode: 0o600,
      flag: "wx",
    });
    await rename(temporary, mappingPath);
    return { mapping, duplicate: false };
  } finally {
    await releaseOwnedLock(lockPath, owner.token);
  }
}
