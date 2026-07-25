import { execFile } from "node:child_process";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  checkStatusSchema,
  prRefSchema,
  type CheckStatus,
  type PrRef,
} from "./contracts.js";

export type ExecResult = {
  stdout: string;
  stderr: string;
  exitCode: number;
};

export type Exec = (
  file: string,
  args: string[],
  options: { cwd: string },
) => Promise<ExecResult>;

export type PrContextComment = {
  author: string;
  body: string;
};

export type PrContext = {
  comments: PrContextComment[];
};

export type GithubClient = {
  ensureBranch(cwd: string, base: string, branch: string): Promise<void>;
  publishBranch(cwd: string, branch: string): Promise<void>;
  ensurePullRequest(
    cwd: string,
    options: { branch: string; base: string; title: string; body: string },
  ): Promise<PrRef>;
  postComment(cwd: string, pr: number, body: string): Promise<void>;
  readPrContext(cwd: string, pr: number): Promise<PrContext>;
  readChecks(cwd: string, pr: number, expectedHeadSha: string): Promise<CheckStatus>;
  mergePullRequest(cwd: string, pr: number): Promise<void>;
};

export const defaultExec: Exec = (file, args, options) => {
  const { promise, resolve } = Promise.withResolvers<ExecResult>();
  execFile(file, args, {
    cwd: options.cwd,
    encoding: "utf8",
    maxBuffer: 16 * 1024 * 1024,
  }, (error, stdout, stderr) => {
    const exitCode = error
      ? (typeof error.code === "number" ? error.code : 1)
      : 0;
    const capturedStderr = String(stderr ?? "") || (error instanceof Error ? error.message : "");
    resolve({
      stdout: String(stdout ?? ""),
      stderr: capturedStderr,
      exitCode,
    });
  });
  return promise;
};

function commandText(file: string, args: string[]): string {
  return [file, ...args].join(" ");
}

function commandError(file: string, args: string[], result: ExecResult): Error {
  const stderr = result.stderr.trim();
  const detail = stderr.length > 0 ? `: ${stderr}` : "";
  return new Error(`${commandText(file, args)} exited with code ${result.exitCode}${detail}`);
}

async function run(exec: Exec, file: string, args: string[], cwd: string): Promise<string> {
  const result = await exec(file, args, { cwd });
  if (result.exitCode !== 0) throw commandError(file, args, result);
  return result.stdout;
}

function parseJson(stdout: string, command: string): unknown {
  try {
    return JSON.parse(stdout);
  } catch (error) {
    throw new Error(`${command} returned invalid JSON: ${error instanceof Error ? error.message : String(error)}`);
  }
}

function asRecord(value: unknown, context: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`${context} returned an unexpected object`);
  }
  return value as Record<string, unknown>;
}

function parsePullRequest(value: unknown, context: string): PrRef {
  const record = asRecord(value, context);
  return prRefSchema.parse({
    number: record.number,
    url: record.url,
    branch: record.headRefName,
    base: record.baseRefName,
  });
}

function parseCreatedPullRequest(stdout: string, options: { branch: string; base: string }): PrRef {
  const text = stdout.trim();
  if (text.length === 0) throw new Error("gh pr create returned no pull request URL");

  try {
    const parsed = JSON.parse(text);
    if (typeof parsed === "object" && parsed !== null && !Array.isArray(parsed)) {
      return parsePullRequest(parsed, "gh pr create");
    }
  } catch {
    // `gh pr create` normally prints only the URL, so parse that form below.
  }

  const url = text.split(/\s+/u).find((candidate) => /^https:\/\/[^\s]+\/pull\/\d+(?:$|[?#])/u.test(candidate));
  if (!url) throw new Error(`gh pr create returned no pull request URL: ${text}`);
  const match = url.match(/\/pull\/(\d+)(?:$|[?#])/u);
  if (!match) throw new Error(`gh pr create returned an invalid pull request URL: ${url}`);
  const number = Number(match[1]);
  return prRefSchema.parse({ number, url, branch: options.branch, base: options.base });
}

function commentAuthor(value: unknown): string {
  if (typeof value === "string") return value;
  if (typeof value !== "object" || value === null || Array.isArray(value)) return "";
  const record = value as Record<string, unknown>;
  if (typeof record.login === "string") return record.login;
  if (typeof record.name === "string") return record.name;
  return "";
}

function parseCommentContext(stdout: string): PrContext {
  const payload = asRecord(parseJson(stdout, "gh pr view"), "gh pr view");
  const rawComments = payload.comments;
  if (rawComments === undefined || rawComments === null) return { comments: [] };
  if (!Array.isArray(rawComments)) throw new Error("gh pr view returned an invalid comments array");

  const comments = rawComments.map((value) => {
    const record = asRecord(value, "gh pr view comments");
    return {
      author: commentAuthor(record.author),
      body: typeof record.body === "string" ? record.body : "",
      createdAt: typeof record.createdAt === "string" ? Date.parse(record.createdAt) : Number.NaN,
    };
  });

  // GitHub normally returns comments oldest-first. When timestamps are present,
  // sort explicitly so the public context contract remains newest-last.
  if (comments.length > 1 && comments.every((comment) => Number.isFinite(comment.createdAt))) {
    comments.sort((left, right) => left.createdAt - right.createdAt);
  }
  return {
    comments: comments.map(({ author, body }) => ({ author, body })),
  };
}

function textField(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function rollupEntries(payload: unknown): Record<string, unknown>[] {
  const record = asRecord(payload, "gh pr view statusCheckRollup");
  const rollup = record.statusCheckRollup;
  if (rollup === undefined || rollup === null) return [];
  if (!Array.isArray(rollup)) throw new Error("gh pr view returned an invalid status check rollup");
  return rollup.map((entry) => asRecord(entry, "gh pr view statusCheckRollup"));
}

function failingRollupEntry(entry: Record<string, unknown>): { name: string; summary: string } | undefined {
  const status = textField(entry.status).toLowerCase();
  const conclusion = textField(entry.conclusion).toLowerCase();
  const state = textField(entry.state).toLowerCase();
  const failingConclusions = new Set([
    "failure",
    "timed_out",
    "cancelled",
    "action_required",
    "error",
    "startup_failure",
    "stale",
  ]);
  const failingStates = new Set(["failure", "error"]);
  const checkRunFailure = failingConclusions.has(conclusion)
    || (status === "completed" && !["success", "neutral", "skipped"].includes(conclusion));
  const statusContextFailure = failingStates.has(state);
  if (!checkRunFailure && !statusContextFailure) return undefined;

  const output = typeof entry.output === "object" && entry.output !== null && !Array.isArray(entry.output)
    ? entry.output as Record<string, unknown>
    : undefined;
  const name = textField(entry.name) || textField(entry.context) || "unnamed check";
  const summary = textField(output?.summary) || textField(output?.title) || textField(entry.description);
  return { name, summary: summary.slice(0, 4_000) };
}

function pendingRollupEntry(entry: Record<string, unknown>): boolean {
  const status = textField(entry.status).toLowerCase();
  const conclusion = textField(entry.conclusion).toLowerCase();
  const state = textField(entry.state).toLowerCase();
  if (failingRollupEntry(entry)) return false;
  if (["success", "neutral", "skipped"].includes(conclusion) || ["success", "neutral", "skipped"].includes(state)) return false;
  return status !== "completed";
}

function resolvedRollupHead(payload: unknown): string {
  const record = asRecord(payload, "gh pr view statusCheckRollup");
  const headRefOid = record.headRefOid;
  if (typeof headRefOid !== "string") throw new Error("gh pr view returned no headRefOid");
  return headRefOid;
}

function assertExpectedHead(actual: string, expected: string): void {
  if (actual.toLowerCase() !== expected.toLowerCase()) {
    throw new Error(`pull request head is stale: expected ${expected}, GitHub reported ${actual}`);
  }
}

export function createGithubClient(exec: Exec = defaultExec): GithubClient {
  return {
    async ensureBranch(cwd, base, branch): Promise<void> {
      await run(exec, "git", ["fetch", "origin"], cwd);
      const probeArgs = ["show-ref", "--verify", "--quiet", `refs/heads/${branch}`];
      const probe = await exec("git", probeArgs, { cwd });
      if (probe.exitCode !== 0 && probe.exitCode !== 1) throw commandError("git", probeArgs, probe);
      if (probe.exitCode === 0) {
        await run(exec, "git", ["checkout", branch], cwd);
      } else {
        await run(exec, "git", ["checkout", "-b", branch, `origin/${base}`], cwd);
      }
    },

    async publishBranch(cwd, branch): Promise<void> {
      // `git push origin <branch>` pushes the REF, wherever HEAD happens to
      // be. If anything moved HEAD after ensureBranch - a human or another
      // agent running `git checkout` in a shared work tree - the stage's
      // commits land on that other branch and this pushes an unchanged ref.
      // The observable symptom is a later "No commits between master and
      // <branch>" from pull request creation, which names neither the real
      // cause nor the branch that swallowed the work. Refuse here instead.
      const head = (await run(exec, "git", ["rev-parse", "--abbrev-ref", "HEAD"], cwd)).trim();
      if (head !== branch) {
        throw new Error(
          `refusing to publish ${branch}: work tree ${cwd} is on ${head}. ` +
            "HEAD moved after this run created its branch, so the run's commits are not on it. " +
            "The work tree must belong to this run alone.",
        );
      }
      await run(exec, "git", ["push", "--set-upstream", "origin", branch], cwd);
    },

    async ensurePullRequest(cwd, options): Promise<PrRef> {
      const listArgs = [
        "pr",
        "list",
        "--head",
        options.branch,
        "--state",
        "open",
        "--json",
        "number,url,headRefName,baseRefName",
      ];
      const listed = parseJson(await run(exec, "gh", listArgs, cwd), "gh pr list");
      if (!Array.isArray(listed)) throw new Error("gh pr list returned an unexpected result");
      const existing = listed[0];
      if (existing !== undefined) return parsePullRequest(existing, "gh pr list");

      const createArgs = [
        "pr",
        "create",
        "--head",
        options.branch,
        "--base",
        options.base,
        "--title",
        options.title,
        "--body",
        options.body,
      ];
      const createdUrl = await run(exec, "gh", createArgs, cwd);
      return parseCreatedPullRequest(createdUrl, options);
    },

    async postComment(cwd, pr, body): Promise<void> {
      const directory = await mkdtemp(join(tmpdir(), "hatchet-gh-comment-"));
      const bodyPath = join(directory, "body.md");
      try {
        await writeFile(bodyPath, body, "utf8");
        await run(exec, "gh", ["pr", "comment", String(pr), "--body-file", bodyPath], cwd);
      } finally {
        await rm(directory, { recursive: true, force: true });
      }
    },

    async readPrContext(cwd, pr): Promise<PrContext> {
      const stdout = await run(exec, "gh", ["pr", "view", String(pr), "--json", "comments"], cwd);
      return parseCommentContext(stdout);
    },

    async readChecks(cwd, pr, expectedHeadSha): Promise<CheckStatus> {
      const stdout = await run(
        exec,
        "gh",
        ["pr", "view", String(pr), "--json", "statusCheckRollup,headRefOid"],
        cwd,
      );
      const payload = parseJson(stdout, "gh pr view");
      const headSha = resolvedRollupHead(payload);
      assertExpectedHead(headSha, expectedHeadSha);
      const entries = rollupEntries(payload);
      const failing = entries
        .map(failingRollupEntry)
        .filter((check): check is { name: string; summary: string } => check !== undefined);
      const conclusion = failing.length > 0
        ? "red"
        : entries.length === 0
          ? "none"
          : entries.some(pendingRollupEntry)
            ? "pending"
            : "green";
      return checkStatusSchema.parse({ conclusion, headSha, failing });
    },

    async mergePullRequest(cwd, pr): Promise<void> {
      // Safety checking belongs to the caller; this method only performs the requested merge.
      await run(exec, "gh", ["pr", "merge", String(pr), "--merge"], cwd);
    },
  };
}
