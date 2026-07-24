import { readFile, stat } from "node:fs/promises";
import { z } from "zod";
import type { OperatorConfig } from "./config.js";

const powderCardSchema = z.object({
  id: z.string().min(1),
  status: z.string().min(1),
}).passthrough();
const powderCardResponseSchema = z.union([
  powderCardSchema,
  z.object({ card: powderCardSchema }).transform(({ card }) => card),
]);

export type PowderCard = z.infer<typeof powderCardSchema>;
export type PowderCardReader = () => Promise<PowderCard>;

async function readAuthorization(config: OperatorConfig): Promise<string | undefined> {
  const tokenFile = config.powder?.apiTokenFile;
  if (!tokenFile) return undefined;
  const metadata = await stat(tokenFile);
  if ((metadata.mode & 0o077) !== 0) throw new Error("Powder API token file must have mode 0600");
  const token = (await readFile(tokenFile, "utf8")).trim();
  if (token.length === 0) throw new Error("Powder API token file must not be empty");
  return `Bearer ${token}`;
}

export async function createPowderCardReader(
  config: OperatorConfig,
  fetchImpl: typeof fetch = fetch,
): Promise<PowderCardReader> {
  if (!config.powder) throw new Error("operator config powder section is required");
  const authorization = await readAuthorization(config);
  const baseUrl = config.powder.baseUrl.endsWith("/") ? config.powder.baseUrl : `${config.powder.baseUrl}/`;
  const url = new URL(`api/v1/cards/${encodeURIComponent(config.cardId)}`, baseUrl);

  return async () => {
    const headers = new Headers();
    if (authorization) headers.set("authorization", authorization);
    const response = await fetchImpl(url, {
      headers,
      signal: AbortSignal.timeout(10_000),
    });
    if (!response.ok) throw new Error(`Powder card read failed with HTTP ${response.status}`);
    const card = powderCardResponseSchema.parse(await response.json());
    if (card.id !== config.cardId) throw new Error("Powder returned a different card");
    return card;
  };
}
