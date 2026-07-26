import { readOperatorConfig } from "../config.js";
import { triggerConfiguredWorkflow } from "../trigger-service.js";

const args = process.argv.slice(2);
const valueAfter = (flag: string): string | undefined => {
  const index = args.indexOf(flag);
  return index === -1 ? undefined : args[index + 1];
};

const config = await readOperatorConfig(valueAfter("--config"));
const result = await triggerConfiguredWorkflow({
  config,
  source: "manual",
  ...(valueAfter("--head") ? { headSha: valueAfter("--head")! } : {}),
});
process.stdout.write(`${JSON.stringify(result)}\n`);
