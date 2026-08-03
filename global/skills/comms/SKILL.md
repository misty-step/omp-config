---
name: comms
description: |
  Route communication by audience and surface. Use when writing, auditing, or
  revising operator chat, vault notes, code comments, agent-to-agent messages,
  prompts, findings, or work-ledger text. Trigger: /comms.
argument-hint: "[surface|critic]"
hide: true
---

# /comms

Use this skill as the canonical communication router. Identify the surface first.
Load only the references named by that route. Preserve every required fact,
condition, number, scope limit, safety requirement, and uncertainty statement.

## Route

| Surface | Default register | Load |
|---|---|---|
| Operator chat | Action-first shape with precise sentence rules | `references/i-have-adhd.md`, `references/ste.md` |
| Vault notes | Durable, searchable, precise prose | `references/ste.md`; load `i-have-adhd.md` for operational checklists |
| Code comments | Concise technical prose that states the reason or invariant | `references/ste.md` |
| Agent-to-agent | Action-first handoff with state, scope, evidence, and next action | `references/i-have-adhd.md`, `references/ste.md` |

For an unlisted surface, select the closest route and state the choice when it
changes the register. Keep voice subordinate to reader, purpose, and output
contract.

## Register model

- Sentence register: use `references/ste.md` for precise words and sentences.
- Shape register: use `references/i-have-adhd.md` for visible action and state.
- Voice register: choose voice only when the artifact and audience need it.
- Inbound register: clarify operator prompts without changing their intent.


## Apply

1. Identify the audience and surface.
2. Load the sentence and shape references required by the route.
3. Write the answer, result, or required action first.
4. Check that the final line states the result or one required next action.

State why, an invariant, or a constraint in code comments. Do not restate code.
Keep vault notes durable. Remove chat-only closers from durable notes.

## Critic route

Load `references/anti-slop.md` only for a dedicated critic subagent. Agents
follow negative instructions poorly. This reference is a critic checklist that
hunts violations in finished text. It is not a normal drafting register.

## Contract

Verbatim text, code, commands, paths, identifiers, citations, mathematics,
schemas, and required machine-readable fields keep their required form.
A user, system, harness, or output contract overrides a style preference.
