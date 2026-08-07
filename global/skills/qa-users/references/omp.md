# OMP composition

## Roles

- **Chief:** dispatches `qa-master`, receives the evidence packet, owns tracker query/create/read-back, PR comments, and work-ledger writes.
- **qa-master:** `global/agents/qa-master.md`. Explores the product, mints personas, freezes `input.v1`, dispatches one `qa-persona` per persona, synthesizes evidence. Tools: read, grep, glob, lsp, browser (smoke/repro only), task. No edit/write/tracker authority.
- **qa-persona:** `global/agents/qa-persona.md`. Browser only. Receives one persona brief and one named real browser entrypoint. Returns runtime evidence, strengths, friction, and exact user steps.

## Depth

`chief → qa-master → qa-persona` (one leaf per persona).

No executive may dispatch persona QA. `verifier` never owns this route.

## Environment

Use only predeclared `real: true` entrypoints whose environment is `local`, `dev`, or `staging`. Unsupported kinds are blocked. Production targets are rejected before dispatch.

## Browser split

- Master browser: entrypoint smoke and reproduction confirmation only. No full persona mission on the master.
- Persona browser: full user mission for the frozen brief only.

## Handoff

`fix-and-pr` requires separate explicit authorization and a read-back issue ID. It runs only after chief filing and read-back, with `inside_user_session: false`.
