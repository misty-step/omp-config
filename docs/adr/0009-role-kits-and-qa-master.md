# ADR 0009: Role kits, sculptor, and QA master

- Status: Accepted
- Date: 2026-08-06

## Context

Specialized skills are valuable when scoped to domain agents, not when they load on every chief session. The `ponytail` agent name hid a broader structure-critic job. Persona QA discovery lived on the OMP root while the coordinator was task-only and blind to the product.

## Decision

1. Keep five broad executives: `architect`, `builder`, `designer`, `researcher`, `verifier`.
2. Rename the structure critic to `sculptor`. Autoload kit `prune` (Ponytail ladder + deep-module vocabulary + non-repair output).
3. Rename persona QA to `qa-master` → `qa-persona`.
4. Give `qa-master` read tools plus browser limited to smoke and reproduction. It explores, mints personas with knowledge and blind_spots, freezes input, dispatches leaves, and synthesizes. The chief owns tracker and PR writes.
5. Autoload one primary kit per agent: designer → `design`; verifier → `verify`; sculptor → `prune`; qa-master → `qa-users`; qa-persona → `qa-persona`.
6. Keep specialty skills hand-only. Load branches from the kit or brief, not from chief model-invocation.

## Consequences

Chief stays thin. Domain agents carry method kits. Persona generation is brief generation against one leaf agent type, not runtime agent-file creation. Sealed launch still unions composition skills onto the root until the compiler injects per-agent.

## Reversal condition

Revert names and tool split only if OMP gains first-class per-spawn skill bundles and dynamic agent declarations that remove the need for fixed role kits.
