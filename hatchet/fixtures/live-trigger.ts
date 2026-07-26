import { triggerConfiguredWorkflow } from "../src/trigger-service.js";
import { readOperatorConfig } from "../src/config.js";

const config = await readOperatorConfig();
const result = await triggerConfiguredWorkflow({ config, source: "manual" });
process.stdout.write(`RESULT=${JSON.stringify(result)}\n`);
