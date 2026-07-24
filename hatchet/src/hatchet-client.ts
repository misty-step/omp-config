import { HatchetClient as Hatchet } from "@hatchet-dev/typescript-sdk/v1/index.js";
import { clientEndpoint, readWorkerToken } from "./config.js";

export async function createHatchetClient(): Promise<Hatchet> {
  const token = await readWorkerToken();
  return new Hatchet({
    token,
    host_port: clientEndpoint.hostPort,
    api_url: clientEndpoint.apiUrl,
    tls_config: { tls_strategy: "none" },
    log_level: "WARN",
  });
}
