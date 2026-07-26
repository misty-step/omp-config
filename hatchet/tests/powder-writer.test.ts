import { describe, expect, it } from "vitest";
import { createPowderWriter } from "../src/powder-writer.js";
import type { OperatorConfig } from "../src/config.js";

const config = {
  version: 1,
  repository: "omp-config",
  recipePaths: {},
  cwd: "/tmp",
  task: "t",
  powder: { baseUrl: "https://powder.example.test", readyStatus: "ready", mode: "ready-queue" },
} as unknown as OperatorConfig;

type Call = { url: string; method: string | undefined; headers: Headers; body: unknown };

// `noUncheckedIndexedAccess` is on: assert the call happened rather than
// asserting it away with `!`, so a writer that sends nothing fails loudly.
function at(calls: Call[], index: number): Call {
  const call = calls[index];
  if (!call) throw new Error(`expected a request at index ${index}, got ${calls.length}`);
  return call;
}

// Mirrors the server: claim is the one keyless mutation (claim_card,
// powder-server/src/main.rs:1636), while release, status, and work-log all call
// `required_idempotency_key` and 400 without it (:1662, :1755, :1972). A fake
// that answered 200 to everything would pass while the client shipped a request
// Powder rejects - which is exactly how a missing key survived review here.
// The real claim receipt is a Claim (powder-core/src/model.rs:987-995). An
// invented shape here would let the client discard the lease id that
// `release` requires - which is exactly what happened.
const claimReceipt = { principal: "p", agent: "hatchet", run_id: "lease-1", acquired_at: 1, expires_at: 2 };

function recorder(status = 200, payload: unknown = claimReceipt) {
  const calls: Call[] = [];
  const fetchImpl = (async (url: URL | string, options: RequestInit = {}) => {
    const headers = new Headers(options.headers);
    calls.push({
      url: String(url),
      method: options.method,
      headers,
      body: options.body ? JSON.parse(String(options.body)) : undefined,
    });
    const keyless = String(url).endsWith("/claim");
    if (!keyless && !headers.get("idempotency-key")) {
      return new Response(JSON.stringify({ error: "missing Idempotency-Key header" }), { status: 400 });
    }
    return new Response(JSON.stringify(payload), { status });
  }) as unknown as typeof fetch;
  return { calls, fetchImpl };
}

describe("powder writer", () => {
  it("claims a card as the declared worker, not as the credential", async () => {
    // Powder refuses to infer the semantic worker from the authenticated
    // principal, so the agent label must travel in the body every time.
    const { calls, fetchImpl } = recorder();
    const writer = await createPowderWriter(config, fetchImpl);

    await writer.claim("card-1", 900);

    expect(calls).toHaveLength(1);
    expect(at(calls, 0).url).toBe("https://powder.example.test/api/v1/cards/card-1/claim");
    expect(at(calls, 0).method).toBe("POST");
    expect(at(calls, 0).body).toEqual({ agent: "hatchet", ttl_seconds: 900 });
  });

  it("returns the lease Powder minted, because release cannot be called without it", async () => {
    // Powder generates the claim's run_id server-side; it is not the Hatchet run
    // id and cannot be reconstructed. A claim that returned void made release
    // uncallable, and no fake caught it because none returned a real receipt.
    const { calls, fetchImpl } = recorder();
    const writer = await createPowderWriter(config, fetchImpl);

    const lease = await writer.claim("card-1");
    await writer.release("card-1", lease.runId);

    expect(lease.runId).toBe("lease-1");
    expect(at(calls, 1).body).toEqual({ run_id: "lease-1" });
  });

  it("omits the ttl rather than sending a null the server must interpret", async () => {
    const { calls, fetchImpl } = recorder();
    const writer = await createPowderWriter(config, fetchImpl);

    await writer.claim("card-1");

    expect(at(calls, 0).body).toEqual({ agent: "hatchet" });
  });

  it("derives the idempotency key from the transition so a retry is one event", async () => {
    // The header is what makes a retried board write collapse instead of
    // appending a second entry. A random nonce would defeat it entirely, so
    // the same transition must produce the same key twice.
    const { calls, fetchImpl } = recorder(200, {});
    const writer = await createPowderWriter(config, fetchImpl);

    await writer.setStatus("card-1", "awaiting_input", "run-7");
    await writer.setStatus("card-1", "awaiting_input", "run-7");

    expect(at(calls, 0).headers.get("idempotency-key")).toBe("card-1:awaiting_input:run-7");
    expect(at(calls, 1).headers.get("idempotency-key")).toBe(at(calls, 0).headers.get("idempotency-key"));
    expect(at(calls, 0).body).toEqual({ status: "awaiting_input" });
  });

  it("gives a different run a different key for the same status", async () => {
    const { calls, fetchImpl } = recorder(200, {});
    const writer = await createPowderWriter(config, fetchImpl);

    await writer.setStatus("card-1", "awaiting_input", "run-7");
    await writer.setStatus("card-1", "awaiting_input", "run-8");

    expect(at(calls, 0).headers.get("idempotency-key")).not.toBe(at(calls, 1).headers.get("idempotency-key"));
  });

  it("sends the work-log agent matching the claim holder", async () => {
    // Powder rejects a work-log whose agent is not the current claim holder,
    // so this label and the claim label are the same string by construction.
    const { calls, fetchImpl } = recorder(200, {});
    const writer = await createPowderWriter(config, fetchImpl);

    await writer.appendWorkLog("card-1", { body: "implement completed", runId: "run-7", model: "gpt-5.6" });

    expect(at(calls, 0).url).toBe("https://powder.example.test/api/v1/cards/card-1/work-log");
    expect(at(calls, 0).body).toEqual({
      agent: "hatchet",
      body: "implement completed",
      run_id: "run-7",
      model: "gpt-5.6",
    });
  });

  it("keys the release so Powder does not reject it", async () => {
    // release_claim calls required_idempotency_key (main.rs:1662) exactly like
    // status and work-log. Only claim is keyless. Shipping this without a key
    // meant every release 400ed, and a fake that always answered 200 hid it.
    const { calls, fetchImpl } = recorder(200, {});
    const writer = await createPowderWriter(config, fetchImpl);

    await writer.release("card-1", "run-7");

    expect(at(calls, 0).url).toBe("https://powder.example.test/api/v1/cards/card-1/release");
    expect(at(calls, 0).headers.get("idempotency-key")).toBe("card-1:release:run-7");
    expect(at(calls, 0).body).toEqual({ run_id: "run-7" });
  });

  it("surfaces a rejected write instead of reporting a board update that never happened", async () => {
    // Callers choose whether a board failure is fatal. They cannot choose well
    // if the writer hides it.
    const { fetchImpl } = recorder(409, {});
    const writer = await createPowderWriter(config, fetchImpl);

    await expect(writer.setStatus("card-1", "done", "run-7")).rejects.toThrow(/HTTP 409/);
  });

  it("joins a base url that has no trailing slash without eating the path", async () => {
    const { calls, fetchImpl } = recorder();
    const writer = await createPowderWriter(
      { ...config, powder: { ...config.powder!, baseUrl: "https://powder.example.test/api-root" } } as OperatorConfig,
      fetchImpl,
    );

    await writer.claim("card-1");

    expect(at(calls, 0).url).toBe("https://powder.example.test/api-root/api/v1/cards/card-1/claim");
  });

  it("escapes a card id that would otherwise change the route", async () => {
    const { calls, fetchImpl } = recorder();
    const writer = await createPowderWriter(config, fetchImpl);

    await writer.claim("a/../b");

    expect(at(calls, 0).url).toBe("https://powder.example.test/api/v1/cards/a%2F..%2Fb/claim");
  });
});
