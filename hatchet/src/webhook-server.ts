import { readFile, stat } from "node:fs/promises";
import { readOperatorConfig } from "./config.js";
import { createPowderCardReader } from "./powder-client.js";
import { createPowderWebhookServer } from "./powder-webhook.js";

const secretPath = process.env.HATCHET_WEBHOOK_SECRET_FILE;
if (!secretPath) throw new Error("HATCHET_WEBHOOK_SECRET_FILE is required");
const secretMetadata = await stat(secretPath);
if ((secretMetadata.mode & 0o077) !== 0) throw new Error("webhook secret file must have mode 0600");
const secret = Buffer.from((await readFile(secretPath, "utf8")).trim(), "utf8");
if (secret.length < 32) throw new Error("webhook secret must contain at least 32 bytes");

const operatorConfig = await readOperatorConfig();
const readPowderCard = await createPowderCardReader(operatorConfig);
const server = createPowderWebhookServer({
  config: operatorConfig,
  secret,
  readPowderCard,
});
const port = Number.parseInt(process.env.HATCHET_WEBHOOK_PORT ?? "8099", 10);
if (!Number.isSafeInteger(port) || port < 1 || port > 65_535) {
  throw new Error("HATCHET_WEBHOOK_PORT must be an integer from 1 through 65535");
}
server.listen(port, "127.0.0.1", () => {
  process.stdout.write(`Webhook server ready on 127.0.0.1:${port}\n`);
});
