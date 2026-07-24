import { triggerConfiguredWorkflow } from "../src/trigger-service.js";
import { readOperatorConfig } from "../src/config.js";

const config = await readOperatorConfig();
const result = await triggerConfiguredWorkflow(config, "manual");
process.stdout.write(`RUN=${JSON.stringify(result)}\n`);
