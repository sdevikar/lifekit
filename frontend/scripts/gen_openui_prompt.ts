import { writeFileSync } from "node:fs";
import { library } from "../src/lib/openui";

const prompt = library.prompt();
const out = `# Auto-generated from frontend/src/lib/openui.tsx. Do not edit by hand.\nOPENUI_SYSTEM_PROMPT = ${JSON.stringify(prompt)}\n`;
writeFileSync("../lifekit/serve/openui_prompt.py", out);
console.log("written", prompt.length, "chars");
