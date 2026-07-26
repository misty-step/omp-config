import { createHmac, timingSafeEqual } from "node:crypto";
import { createServer, type IncomingMessage, type Server, type ServerResponse } from "node:http";
import { z } from "zod";
import type { OperatorConfig } from "./config.js";
import type { PowderCardReader } from "./powder-client.js";
import { triggerConfiguredWorkflow, type TriggerRequest, type TriggerResult } from "./trigger-service.js";

export const powderWebhookPayloadSchema = z.object({
  schema_version: z.literal("powder.card_event.v1"),
  event_id: z.string().min(1),
  event_type: z.literal("moved-to-ready"),
  occurred_at: z.number().int(),
  actor: z.string().min(1),
  principal: z.string().min(1).optional(),
  role: z.string().min(1).optional(),
  audit_event_id: z.string().min(1).optional(),
  card: z.object({
    id: z.string().min(1),
    status: z.literal("ready"),
  }).passthrough(),
  change: z.object({
    previous_status: z.string().min(1),
    status: z.literal("ready"),
  }).passthrough(),
}).passthrough();

export type PowderWebhookPayload = z.infer<typeof powderWebhookPayloadSchema>;
type TriggerWorkflow = (request: TriggerRequest) => Promise<TriggerResult>;

export type PowderWebhookDependencies = {
  config: OperatorConfig;
  secret: Buffer;
  readPowderCard: PowderCardReader;
  triggerWorkflow?: TriggerWorkflow;
};

function send(response: ServerResponse, status: number, body: object): void {
  response.writeHead(status, { "content-type": "application/json" });
  response.end(`${JSON.stringify(body)}\n`);
}

function readBody(request: IncomingMessage): Promise<Buffer> {
  return new Promise<Buffer>((resolve, reject) => {
    const chunks: Buffer[] = [];
    let length = 0;
    request.on("data", (chunk: Buffer) => {
      length += chunk.length;
      if (length > 64 * 1024) {
        reject(new Error("request body too large"));
        request.destroy();
        return;
      }
      chunks.push(chunk);
    });
    request.once("end", () => resolve(Buffer.concat(chunks)));
    request.once("error", reject);
  });
}

export function powderSignature(secret: Buffer, body: Buffer): string {
  return `sha256=${createHmac("sha256", secret).update(body).digest("hex")}`;
}

export function powderSignatureMatches(secret: Buffer, header: string | undefined, body: Buffer): boolean {
  if (!header?.startsWith("sha256=")) return false;
  const suppliedHex = header.slice("sha256=".length);
  if (!/^[0-9a-f]{64}$/i.test(suppliedHex)) return false;
  const expected = createHmac("sha256", secret).update(body).digest();
  return timingSafeEqual(expected, Buffer.from(suppliedHex, "hex"));
}

export function createPowderWebhookServer(dependencies: PowderWebhookDependencies): Server {
  const triggerWorkflow = dependencies.triggerWorkflow ?? triggerConfiguredWorkflow;
  return createServer(async (request, response) => {
    try {
      if (request.method === "GET" && request.url === "/health") {
        send(response, 200, { ok: true, service: "hatchet-powder-webhook" });
        return;
      }
      if (request.method !== "POST" || request.url !== "/webhook/powder") {
        send(response, 404, { error: "not_found" });
        return;
      }

      const body = await readBody(request);
      const signature = Array.isArray(request.headers["x-signature-256"])
        ? undefined
        : request.headers["x-signature-256"];
      if (!powderSignatureMatches(dependencies.secret, signature, body)) {
        send(response, 401, { error: "unauthorized" });
        return;
      }

      const payload = powderWebhookPayloadSchema.parse(JSON.parse(body.toString("utf8")));
      if (payload.card.id !== dependencies.config.cardId) {
        send(response, 202, {
          accepted: true,
          triggered: false,
          reason: "card_not_configured",
          cardId: payload.card.id,
          eventId: payload.event_id,
        });
        return;
      }

      const currentCard = await dependencies.readPowderCard();
      if (currentCard.status !== dependencies.config.powder?.readyStatus) {
        send(response, 202, {
          accepted: true,
          triggered: false,
          reason: "card_not_ready",
          cardId: currentCard.id,
          status: currentCard.status,
          eventId: payload.event_id,
        });
        return;
      }
        // Powder events do not carry repository HEAD, so the trigger snapshots
        // it. Admission belongs to the engine and is keyed on the card alone.
        const result = await triggerWorkflow({ config: dependencies.config, source: "webhook" });
      send(response, 202, {
        accepted: true,
        triggered: !result.duplicate,
        eventId: payload.event_id,
        ...result,
      });
    } catch (error) {
      const status = error instanceof z.ZodError || error instanceof SyntaxError ? 400 : 500;
      send(response, status, { error: status === 400 ? "invalid_request" : "internal_error" });
    }
  });
}
