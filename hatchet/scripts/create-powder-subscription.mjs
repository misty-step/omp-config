#!/usr/bin/env node
import { mkdir, open, readFile, rm, stat } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const webhookUrl = process.argv[2];
if (!webhookUrl) {
  process.stderr.write("usage: create-powder-subscription.mjs <tailnet-webhook-url>\n");
  process.exit(2);
}
const parsedWebhookUrl = new URL(webhookUrl);
if (parsedWebhookUrl.protocol !== "https:") throw new Error("webhook URL must use HTTPS");
if (
  !parsedWebhookUrl.hostname.endsWith(".ts.net")
  || parsedWebhookUrl.pathname !== "/webhook/powder"
  || parsedWebhookUrl.search !== ""
  || parsedWebhookUrl.hash !== ""
  || parsedWebhookUrl.username !== ""
  || parsedWebhookUrl.password !== ""
) {
  throw new Error("webhook URL must be the exact tailnet HTTPS /webhook/powder route");
}

const configPath = resolve(process.env.HATCHET_OPERATOR_CONFIG ?? resolve(root, "local/operator-wildcard.json"));
const secretPath = resolve(process.env.HATCHET_WEBHOOK_SECRET_FILE ?? resolve(root, "local/powder-webhook-secret"));
const config = JSON.parse(await readFile(configPath, "utf8"));
if (!config.powder?.baseUrl || !config.powder?.apiTokenFile) {
  throw new Error("operator config must provide powder.baseUrl and powder.apiTokenFile");
}

const tokenMetadata = await stat(config.powder.apiTokenFile);
if ((tokenMetadata.mode & 0o077) !== 0) throw new Error("Powder API token file must have mode 0600");
const tokenPlaceholder = (await readFile(config.powder.apiTokenFile, "utf8")).trim();
if (!/^__mint\.[a-z0-9_-]+\.[a-z0-9_-]+__$/i.test(tokenPlaceholder)) {
  throw new Error("Powder API token file must contain a Mint placeholder, never credential bytes");
}

const baseUrl = config.powder.baseUrl.endsWith("/") ? config.powder.baseUrl : `${config.powder.baseUrl}/`;
const endpoint = new URL("api/v1/events/subscriptions", baseUrl);
await mkdir(dirname(secretPath), { recursive: true, mode: 0o700 });
const secretHandle = await open(secretPath, "wx", 0o600);
let created;
try {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      authorization: `Bearer ${tokenPlaceholder}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      url: parsedWebhookUrl.href,
      event_filter: ["moved-to-ready"],
    }),
    signal: AbortSignal.timeout(15_000),
  });
  if (!response.ok) throw new Error(`Powder subscription creation failed with HTTP ${response.status}`);

  created = await response.json();
  if (
    typeof created?.signing_secret !== "string"
    || created.signing_secret.length < 32
    || typeof created?.subscription?.id !== "string"
    || created.subscription.url !== parsedWebhookUrl.href
    || !Array.isArray(created.subscription.event_filter)
    || created.subscription.event_filter.length !== 1
    || created.subscription.event_filter[0] !== "moved-to-ready"
  ) {
    throw new Error("Powder returned an invalid subscription response");
  }

  await secretHandle.writeFile(`${created.signing_secret}\n`, "utf8");
  await secretHandle.sync();
  await secretHandle.close();
  const secretMetadata = await stat(secretPath);
  if ((secretMetadata.mode & 0o077) !== 0) throw new Error("captured webhook secret file is not mode 0600");
} catch (error) {
  await secretHandle.close().catch(() => undefined);
  await rm(secretPath, { force: true });
  const subscriptionId = created?.subscription?.id;
  if (typeof subscriptionId === "string") {
    const disableEndpoint = new URL(
      `api/v1/events/subscriptions/${encodeURIComponent(subscriptionId)}/disable`,
      baseUrl,
    );
    const disabled = await fetch(disableEndpoint, {
      method: "POST",
      headers: { authorization: `Bearer ${tokenPlaceholder}` },
      signal: AbortSignal.timeout(15_000),
    });
    if (!disabled.ok) {
      throw new Error(
        `subscription ${subscriptionId} could not be disabled after local secret persistence failed`,
        { cause: error },
      );
    }
  }
  throw error;
}
process.stdout.write(`${JSON.stringify({ subscription: created.subscription })}\n`);
