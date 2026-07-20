# /harness-engineering convert

Convert between OMP agent definitions (`global/agents/<name>.md`) and skills.

## Agent to Skill

1. Read the agent's system prompt and its `tools`/`autoloadSkills` envelope.
2. Strip agent-only fields (`model`, `thinkingLevel`, `tools`, `spawns`,
   `readSummarize`, `prewalk`).
3. Transform description from "who this agent is" to "when to invoke".
4. Restructure as `SKILL.md` with progressive disclosure.
5. Move detailed instructions to `references/`.

## Skill to Agent

1. Read the skill's `SKILL.md`.
2. Add agent frontmatter: `name`, `description`, explicit `model` binding(s),
   `thinkingLevel`, `tools`, and `spawns` (`bin/check` fails the gate on any
   agent missing `model`, `thinkingLevel`, or `tools`).
3. Rewrite description as persona ("You are...").
4. Keep instructions focused — agents get full context at startup; name
   `autoloadSkills` instead of pasting skill content inline.
