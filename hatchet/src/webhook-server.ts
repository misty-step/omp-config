import { createHmac, timingSafeEqual } from "node:crypto";
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { z } from "zod";
import { readOperatorConfig } from "./config.js";
import { triggerConfiguredWorkflow } from "./trigger-service.js";

const webhookPayloadSchema = z.object({
  event: z.literal("card.ready"),
  cardId: z.string().min(1),
  headSha: z.string().regex(/^[0-9a-f]{40}$/i),
  idempotencyKey: z.string().min(1).optional(),
});

const secretPath = process.env.HATCHET_WEBHOOK_SECRET_FILE;
if (!secretPath) throw new Error("HATCHET_WEBHOOK_SECRET_FILE is required");
const secretMetadata = await stat(secretPath);
if ((secretMetadata.mode & 0o077) !== 0) throw new Error("webhook secret file must have mode 0600");
const secret = Buffer.from((await readFile(secretPath, "utf8")).trim(), "utf8");
if (secret.length < 32) throw new Error("webhook secret must contain at least 32 bytes");
const operatorConfig = await readOperatorConfig();

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

function signatureMatches(header: string | undefined, body: Buffer): boolean {
  if (!header?.startsWith("sha256=")) return false;
  const suppliedHex = header.slice("sha256=".length);
  if (!/^[0-9a-f]{64}$/i.test(suppliedHex)) return false;
  const expected = createHmac("sha256", secret).update(body).digest();
  return timingSafeEqual(expected, Buffer.from(suppliedHex, "hex"));
}

const server = createServer(async (request, response) => {
  try {
    if (request.method === "GET" && request.url === "/health") {
      send(response, 200, { ok: true });
      return;
    }
    if (request.method !== "POST" || request.url !== "/webhook/powder") {
      send(response, 404, { error: "not_found" });
      return;
    }
    const body = await readBody(request);
    const signature = Array.isArray(request.headers["x-hatchet-canary-signature"])
      ? undefined
      : request.headers["x-hatchet-canary-signature"];
    if (!signatureMatches(signature, body)) {
      send(response, 401, { error: "unauthorized" });
      return;
    }
    const payload = webhookPayloadSchema.parse(JSON.parse(body.toString("utf8")));
    if (payload.cardId !== operatorConfig.cardId) {
      send(response, 403, { error: "card_not_configured" });
      return;
    }
    const result = await triggerConfiguredWorkflow(operatorConfig, "webhook", payload.headSha, payload.idempotencyKey);
    send(response, 202, result);
  } catch (error) {
    const status = error instanceof z.ZodError || error instanceof SyntaxError ? 400 : 500;
    send(response, status, { error: status === 400 ? "invalid_request" : "internal_error" });
  }
});

const port = Number.parseInt(process.env.HATCHET_WEBHOOK_PORT ?? "8099", 10);
server.listen(port, "127.0.0.1", () => process.stdout.write(`Webhook server ready on 127.0.0.1:${port}\n`));
