import type { AddressInfo } from "node:net";
import type { Server } from "node:http";
import { describe, expect, it } from "vitest";
import type { OperatorConfig } from "../src/config.js";
import {
  createPowderWebhookServer,
  powderSignature,
  type PowderWebhookDependencies,
} from "../src/powder-webhook.js";

const configuredCardId = "omp-config-tools-wildcard-resolution";
const secret = Buffer.alloc(32, 0x2a);
const config: OperatorConfig = {
  version: 1,
  cardId: configuredCardId,
  repository: "misty-step/omp-config",
  recipePaths: {
    implement: "/recipes/implement",
    adversarial_review: "/recipes/review",
    remediate: "/recipes/remediate",
    live_verify: "/recipes/verify",
    terminal_evidence: "/recipes/evidence",
  },
  cwd: "/repo",
  task: "task",
  powder: {
    baseUrl: "https://powder.example.test",
    readyStatus: "ready",
  },
};

function eventBody(cardId = configuredCardId, eventId = "evt-test-delivery"): Buffer {
  return Buffer.from(JSON.stringify({
    schema_version: "powder.card_event.v1",
    event_id: eventId,
    event_type: "moved-to-ready",
    occurred_at: 1_753_315_200,
    actor: "operator",
    card: {
      id: cardId,
      title: "Configured card",
      body: "",
      status: "ready",
      priority: "P1",
      created_at: 1_753_315_100,
      updated_at: 1_753_315_200,
    },
    change: {
      previous_status: "backlog",
      status: "ready",
    },
  }));
}

async function withServer(
  dependencies: PowderWebhookDependencies,
  exercise: (baseUrl: string) => Promise<void>,
): Promise<void> {
  const server: Server = createPowderWebhookServer(dependencies);
  await new Promise<void>((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const { port } = server.address() as AddressInfo;
  try {
    await exercise(`http://127.0.0.1:${port}`);
  } finally {
    await new Promise<void>((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
  }
}

function signedHeaders(body: Buffer): HeadersInit {
  return {
    "content-type": "application/json",
    "x-signature-256": powderSignature(secret, body),
  };
}

const neverTrigger = async (): Promise<never> => {
  throw new Error("workflow must not be triggered");
};

describe("Powder webhook HTTP contract", () => {
  it("serves health without touching Powder or Hatchet", async () => {
    await withServer({
      config,
      secret,
      readPowderCard: async () => { throw new Error("health must not read Powder"); },
      triggerWorkflow: neverTrigger,
    }, async (baseUrl) => {
      const response = await fetch(`${baseUrl}/health`);
      expect(response.status).toBe(200);
      await expect(response.json()).resolves.toEqual({ ok: true, service: "hatchet-powder-webhook" });
    });
  });

  it("returns 401 for unsigned and incorrectly signed bodies", async () => {
    const body = eventBody();
    await withServer({
      config,
      secret,
      readPowderCard: async () => { throw new Error("unauthorized request must not read Powder"); },
      triggerWorkflow: neverTrigger,
    }, async (baseUrl) => {
      const unsigned = await fetch(`${baseUrl}/webhook/powder`, { method: "POST", body: body.toString("utf8") });
      expect(unsigned.status).toBe(401);
      const badSignature = await fetch(`${baseUrl}/webhook/powder`, {
        method: "POST",
        headers: { "x-signature-256": `sha256=${"0".repeat(64)}` },
        body: body.toString("utf8"),
      });
      expect(badSignature.status).toBe(401);
    });
  });

  it("acknowledges and ignores a signed event for another card", async () => {
    const body = eventBody("another-card");
    await withServer({
      config,
      secret,
      readPowderCard: async () => { throw new Error("other card must not read Powder"); },
      triggerWorkflow: neverTrigger,
    }, async (baseUrl) => {
      const response = await fetch(`${baseUrl}/webhook/powder`, {
        method: "POST",
        headers: signedHeaders(body),
        body: body.toString("utf8"),
      });
      expect(response.status).toBe(202);
      await expect(response.json()).resolves.toMatchObject({
        accepted: true,
        triggered: false,
        reason: "card_not_configured",
        cardId: "another-card",
      });
    });
  });

  it("does not trigger a stale event after the configured card has left ready", async () => {
    const body = eventBody();
    await withServer({
      config,
      secret,
      readPowderCard: async () => ({ id: configuredCardId, status: "in_progress" }),
      triggerWorkflow: neverTrigger,
    }, async (baseUrl) => {
      const response = await fetch(`${baseUrl}/webhook/powder`, {
        method: "POST",
        headers: signedHeaders(body),
        body: body.toString("utf8"),
      });
      expect(response.status).toBe(202);
      await expect(response.json()).resolves.toMatchObject({
        accepted: true,
        triggered: false,
        reason: "card_not_ready",
        status: "in_progress",
      });
    });
  });

  it("returns the existing run for a duplicate event and leaves HEAD/key derivation to the shared trigger", async () => {
    const body = eventBody(configuredCardId, "evt-duplicate");
    let admitted = false;
    const triggerCalls: Array<{ head: string | undefined; key: string | undefined }> = [];
    await withServer({
      config,
      secret,
      readPowderCard: async () => ({ id: configuredCardId, status: "ready" }),
      triggerWorkflow: async (_config, _source, head, key) => {
        triggerCalls.push({ head, key });
        const duplicate = admitted;
        admitted = true;
        return {
          runId: "run-existing",
          duplicate,
          idempotencyKey: `${configuredCardId}:${"a".repeat(40)}`,
        };
      },
    }, async (baseUrl) => {
      const first = await fetch(`${baseUrl}/webhook/powder`, {
        method: "POST",
        headers: signedHeaders(body),
        body: body.toString("utf8"),
      });
      const second = await fetch(`${baseUrl}/webhook/powder`, {
        method: "POST",
        headers: signedHeaders(body),
        body: body.toString("utf8"),
      });
      expect(await first.json()).toMatchObject({ runId: "run-existing", duplicate: false, triggered: true });
      expect(await second.json()).toMatchObject({ runId: "run-existing", duplicate: true, triggered: false });
      expect(triggerCalls).toEqual([
        { head: undefined, key: undefined },
        { head: undefined, key: undefined },
      ]);
    });
  });
});
