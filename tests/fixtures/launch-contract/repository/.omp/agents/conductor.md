---
name: conductor
description: Proof-only root agent that dispatches one constrained reader.
model: openai-codex/gpt-5.6-luna:low
thinkingLevel: low
tools: task
autoloadSkills: ''
spawns: pico
---

Dispatch only the declared pico agent. Preserve its exact output.
