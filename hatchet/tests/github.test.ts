import { readFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";
import { createGithubClient, type Exec, type ExecResult } from "../src/github.js";

const cwd = "/fixture/repository";
const headSha = "a".repeat(40);

type Call = {
  file: string;
  args: string[];
  cwd: string;
};

type Responder = (call: Call) => Promise<ExecResult> | ExecResult;

function fakeExec(responder: Responder) {
  const calls: Call[] = [];
  const exec: Exec = async (file, args, options) => {
    const call = { file, args: [...args], cwd: options.cwd };
    calls.push(call);
    return responder(call);
  };
  return { calls, exec };
}

function ok(stdout = ""): ExecResult {
  return { stdout, stderr: "", exitCode: 0 };
}

function rollupExec(rollup: unknown[], reportedHeadSha = headSha) {
  return fakeExec((call) => {
    if (call.file === "gh" && call.args[0] === "pr" && call.args[1] === "view") {
      return ok(JSON.stringify({ headRefOid: reportedHeadSha, statusCheckRollup: rollup }));
    }
    return ok();
  });
}

describe("GithubClient", () => {
  it("checks out an existing branch without resetting its commits", async () => {
    const fake = fakeExec((call) => {
      if (call.file === "git" && call.args[0] === "show-ref") return ok();
      return ok();
    });

    await createGithubClient(fake.exec).ensureBranch(cwd, "master", "card/branch");

    expect(fake.calls.map((call) => call.args)).toEqual([
      ["fetch", "origin"],
      ["show-ref", "--verify", "--quiet", "refs/heads/card/branch"],
      ["checkout", "card/branch"],
    ]);
    expect(fake.calls.some((call) => call.args.includes("reset") || call.args.includes("--force"))).toBe(false);
  });

  it("creates a missing branch from origin/base after fetching", async () => {
    const fake = fakeExec((call) => {
      if (call.file === "git" && call.args[0] === "show-ref") {
        return { stdout: "", stderr: "", exitCode: 1 };
      }
      return ok();
    });

    await createGithubClient(fake.exec).ensureBranch(cwd, "master", "card/branch");

    expect(fake.calls.map((call) => call.args)).toEqual([
      ["fetch", "origin"],
      ["show-ref", "--verify", "--quiet", "refs/heads/card/branch"],
      ["checkout", "-b", "card/branch", "origin/master"],
    ]);
  });

  it("reuses an existing open pull request without creating another", async () => {
    const existing = {
      number: 17,
      url: "https://github.com/example/project/pull/17",
      headRefName: "card/branch",
      baseRefName: "master",
    };
    const fake = fakeExec((call) => {
      if (call.file === "gh" && call.args[1] === "list") return ok(JSON.stringify([existing]));
      throw new Error(`unexpected command: ${call.file} ${call.args.join(" ")}`);
    });

    const result = await createGithubClient(fake.exec).ensurePullRequest(cwd, {
      branch: "card/branch",
      base: "master",
      title: "Implement card",
      body: "Description",
    });

    expect(result).toEqual({
      number: 17,
      url: existing.url,
      branch: "card/branch",
      base: "master",
    });
    expect(fake.calls.some((call) => call.file === "gh" && call.args[1] === "create")).toBe(false);
  });

  it("creates a pull request when the open-PR lookup is empty", async () => {
    const fake = fakeExec((call) => {
      if (call.file === "gh" && call.args[1] === "list") return ok("[]");
      if (call.file === "gh" && call.args[1] === "create") {
        return ok("https://github.com/example/project/pull/18\n");
      }
      throw new Error(`unexpected command: ${call.file} ${call.args.join(" ")}`);
    });

    const result = await createGithubClient(fake.exec).ensurePullRequest(cwd, {
      branch: "card/branch",
      base: "master",
      title: "Implement card",
      body: "Description",
    });

    expect(result).toEqual({
      number: 18,
      url: "https://github.com/example/project/pull/18",
      branch: "card/branch",
      base: "master",
    });
    expect(fake.calls[1]?.args).toEqual([
      "pr",
      "create",
      "--head",
      "card/branch",
      "--base",
      "master",
      "--title",
      "Implement card",
      "--body",
      "Description",
    ]);
  });

  it("maps a fully successful rollup to green", async () => {
    const fake = rollupExec([
      { name: "build", status: "COMPLETED", conclusion: "SUCCESS" },
      { context: "lint", state: "SUCCESS" },
      { name: "docs", status: "COMPLETED", conclusion: "NEUTRAL" },
      { name: "optional", status: "COMPLETED", conclusion: "SKIPPED" },
    ]);

    await expect(createGithubClient(fake.exec).readChecks(cwd, 17, headSha)).resolves.toEqual({
      conclusion: "green",
      headSha,
      failing: [],
    });
  });

  it("maps queued or expected checks to pending", async () => {
    const fake = rollupExec([
      { name: "build", status: "QUEUED", conclusion: null },
      { context: "lint", state: "EXPECTED" },
    ]);

    await expect(createGithubClient(fake.exec).readChecks(cwd, 17, headSha)).resolves.toEqual({
      conclusion: "pending",
      headSha,
      failing: [],
    });
  });

  it("maps every failing check to red and names each one", async () => {
    const fake = rollupExec([
      { name: "build", status: "COMPLETED", conclusion: "FAILURE", output: { summary: "unit tests failed" } },
      { context: "deploy", state: "ERROR", description: "deployment failed" },
      { name: "cancelled", status: "COMPLETED", conclusion: "CANCELLED" },
    ]);

    await expect(createGithubClient(fake.exec).readChecks(cwd, 17, headSha)).resolves.toEqual({
      conclusion: "red",
      headSha,
      failing: [
        { name: "build", summary: "unit tests failed" },
        { name: "deploy", summary: "deployment failed" },
        { name: "cancelled", summary: "" },
      ],
    });
  });

  it("maps an empty or absent rollup to none rather than green", async () => {
    const empty = rollupExec([]);
    await expect(createGithubClient(empty.exec).readChecks(cwd, 17, headSha)).resolves.toEqual({
      conclusion: "none",
      headSha,
      failing: [],
    });

    const absentClient = createGithubClient(fakeExec((call) => {
      if (call.file === "gh" && call.args[1] === "view") return ok(JSON.stringify({ headRefOid: headSha }));
      return ok();
    }).exec);
    await expect(absentClient.readChecks(cwd, 17, headSha)).resolves.toEqual({
      conclusion: "none",
      headSha,
      failing: [],
    });
  });

  it("rejects a stale rollup instead of returning a result for the wrong commit", async () => {
    const fake = rollupExec([{ name: "build", status: "COMPLETED", conclusion: "SUCCESS" }], "b".repeat(40));

    await expect(createGithubClient(fake.exec).readChecks(cwd, 17, headSha)).rejects.toThrow(/stale/iu);
  });

  it("preserves newlines, backticks, and quotes in a comment body", async () => {
    const body = "first line\n`inline code` and \"quoted\"\nlast line";
    let observedBody = "";
    const fake = fakeExec(async (call) => {
      if (call.file === "gh" && call.args[1] === "comment") {
        const bodyFlag = call.args.indexOf("--body-file");
        const bodyPath = call.args[bodyFlag + 1];
        if (!bodyPath) throw new Error("missing body file");
        observedBody = await readFile(bodyPath, "utf8");
      }
      return ok();
    });

    await createGithubClient(fake.exec).postComment(cwd, 17, body);

    expect(observedBody).toBe(body);
    expect(fake.calls[0]?.args).toEqual(["pr", "comment", "17", "--body-file", expect.any(String)]);
  });

  it("surfaces a non-zero command exit with the captured stderr", async () => {
    const fake = fakeExec((call) => {
      if (call.file === "git" && call.args[0] === "push") {
        return { stdout: "", stderr: "fatal: permission denied", exitCode: 1 };
      }
      return ok();
    });

    await expect(createGithubClient(fake.exec).publishBranch(cwd, "card/branch"))
      .rejects.toThrow(/git push.*fatal: permission denied/iu);
  });
});
