import { describe, expect, it } from "vitest";
import { readOperatorConfig } from "../src/config.js";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve } from "node:path";

const recipePaths = {
  implement: "/recipes/implement",
  adversarial_review: "/recipes/review",
  remediate: "/recipes/remediate",
  live_verify: "/recipes/verify",
  terminal_evidence: "/recipes/evidence",
};

async function withConfigFile(content: unknown, exercise: (path: string) => Promise<void>): Promise<void> {
  const dir = await mkdtemp(resolve(tmpdir(), "hatchet-config-test-"));
  const path = resolve(dir, "operator.json");
  try {
    await writeFile(path, JSON.stringify(content), "utf8");
    await exercise(path);
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
}

describe("operator config schema", () => {
  it("accepts legacy single-card config without an explicit powder.mode", async () => {
    await withConfigFile(
      {
        version: 1,
        cardId: "card-1",
        repository: "omp/repo",
        recipePaths,
        cwd: "/repo",
        task: "task",
        powder: { baseUrl: "https://powder.example.test", readyStatus: "ready" },
      },
      async (path) => {
        const config = await readOperatorConfig(path);
        expect(config.powder?.mode).toBe("single");
        expect(config.cardId).toBe("card-1");
      },
    );
  });

  it("rejects single mode when cardId is missing", async () => {
    await withConfigFile(
      {
        version: 1,
        repository: "omp/repo",
        recipePaths,
        cwd: "/repo",
        task: "task",
        powder: { baseUrl: "https://powder.example.test", mode: "single" },
      },
      async (path) => {
        await expect(readOperatorConfig(path)).rejects.toThrow();
      },
    );
  });

  it("rejects single mode when repository is missing", async () => {
    await withConfigFile(
      {
        version: 1,
        cardId: "card-1",
        recipePaths,
        cwd: "/repo",
        task: "task",
        powder: { baseUrl: "https://powder.example.test", mode: "single" },
      },
      async (path) => {
        await expect(readOperatorConfig(path)).rejects.toThrow();
      },
    );
  });

  it("accepts ready-queue mode without cardId or repository", async () => {
    await withConfigFile(
      {
        version: 1,
        recipePaths,
        cwd: "/repo",
        task: "task",
        powder: {
          baseUrl: "https://powder.example.test",
          readyStatus: "ready",
          mode: "ready-queue",
          repositoryAllowlist: ["omp/repo-a", "omp/repo-b"],
        },
      },
      async (path) => {
        const config = await readOperatorConfig(path);
        expect(config.cardId).toBeUndefined();
        expect(config.powder?.mode).toBe("ready-queue");
        expect(config.powder?.repositoryAllowlist).toEqual(["omp/repo-a", "omp/repo-b"]);
      },
    );
  });

  it("rejects an empty repositoryAllowlist", async () => {
    await withConfigFile(
      {
        version: 1,
        recipePaths,
        cwd: "/repo",
        task: "task",
        powder: {
          baseUrl: "https://powder.example.test",
          mode: "ready-queue",
          repositoryAllowlist: [],
        },
      },
      async (path) => {
        await expect(readOperatorConfig(path)).rejects.toThrow();
      },
    );
  });

  it("rejects an unknown powder.mode value", async () => {
    await withConfigFile(
      {
        version: 1,
        cardId: "card-1",
        repository: "omp/repo",
        recipePaths,
        cwd: "/repo",
        task: "task",
        powder: { baseUrl: "https://powder.example.test", mode: "everything" },
      },
      async (path) => {
        await expect(readOperatorConfig(path)).rejects.toThrow();
      },
    );
  });
});
