#!/usr/bin/env node
import { createHmac } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const target = process.argv[2] ?? "http://127.0.0.1:8099/webhook/powder";
const configPath = resolve(process.env.HATCHET_OPERATOR_CONFIG ?? resolve(root, "local/operator-wildcard.json"));
const secretPath = resolve(process.env.HATCHET_WEBHOOK_SECRET_FILE ?? resolve(root, "local/powder-webhook-secret"));
const config = JSON.parse(await readFile(configPath, "utf8"));
const probeCardId = "hatchet-rollout-probe-unconfigured";
if (probeCardId === config.cardId) throw new Error("probe sentinel must not be the configured card");
const metadata = await stat(secretPath);
if ((metadata.mode & 0o077) !== 0) throw new Error("webhook secret file must have mode 0600");
const secret = Buffer.from((await readFile(secretPath, "utf8")).trim(), "utf8");
if (secret.length < 32) throw new Error("webhook secret must contain at least 32 bytes");

const body = JSON.stringify({
  schema_version: "powder.card_event.v1",
  event_id: "evt-hatchet-rollout-probe",
  event_type: "moved-to-ready",
  occurred_at: Math.floor(Date.now() / 1000),
  actor: "hatchet-rollout-probe",
  card: {
    id: probeCardId,
    title: "Hatchet rollout probe",
    body: "",
    status: "ready",
    priority: "P1",
    created_at: 0,
    updated_at: 0,
  },
  change: {
    previous_status: "backlog",
    status: "ready",
  },
});
const signature = `sha256=${createHmac("sha256", secret).update(body).digest("hex")}`;
const response = await fetch(target, {
  method: "POST",
  headers: {
    "content-type": "application/json",
    "x-signature-256": signature,
  },
  body,
  signal: AbortSignal.timeout(15_000),
});
const responseBody = await response.json();
if (
  response.status !== 202
  || responseBody?.triggered !== false
  || responseBody?.reason !== "card_not_configured"
) {
  throw new Error("signed webhook probe did not take the non-triggering other-card path");
}
process.stdout.write(`${JSON.stringify({ httpStatus: response.status, response: responseBody })}\n`);
