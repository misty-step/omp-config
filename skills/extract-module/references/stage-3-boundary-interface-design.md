# Stage 3 — Boundary & Interface Design

The boundary is the smallest surface that hides necessary complexity. Design it
from the post-deletion coupling map, not from today's folder layout.

## Procedure

1. **Name the module.** One sentence: what job the extracted module owns after
   deletion. One sentence: what it explicitly does not own.
2. **Minimal public API contract.** List every symbol that survives on the
   public boundary:
   - functions, classes, types, constants, and factory entry points;
   - intentional re-exports from third-party dependencies (prefer narrow
     re-exports over leaking full dependency types).
   For each symbol: inputs, outputs, errors, side effects, and threading/async
   constraints. Omit anything callers can obtain without importing this module.
3. **Internalize private state.** Everything not on the public contract moves
   behind the boundary:
   - private types, helpers, and internal packages;
   - module-level mutable state and caches;
   - config parsing and env reads (callers pass config in, or the module reads
     only its own prefixed keys);
   - test helpers — in a `testing` or `__tests__` subtree, never on the public
     index.
4. **Leakage resolution.** For each leakage from Stage 1, assign one resolution:
   - **extract** — move into the module's public or internal API;
   - **caller adapts** — caller keeps a local type or mapper;
   - **delete** — remove the coupling (often paired with Stage 2 deletions);
   - **shared kernel** — promote to a tiny shared package both sides depend on
     (last resort; justify why inline duplication is worse).
   No leakage remains **unresolved**.
5. **Third-party dependency matrix.** For each direct third-party dependency
   the candidate uses:
   - package name and version constraint;
   - which public API symbols depend on it;
   - whether the dependency stays **direct**, moves **peer**, or becomes
     **dev-only** after extraction;
   - license and security posture if the module will ship externally.
   Use the [Dependency matrix template](artifacts.md#dependency-matrix).
6. **Circular import breaks.** For each cycle from Stage 1, record the chosen
   break: invert dependency, introduce a narrow port type, move shared types to
   kernel, or delete an edge via Stage 2 deletions.
7. **Invariants and failure behavior.** State what the module guarantees,
   what it does not guarantee, and how errors propagate across the boundary.

## Completion criterion

The public API contract lists every exported symbol with typed inputs,
outputs, errors, and side effects — and nothing else. Every private type and
state holder is assigned an internal path with no public re-export. Every
Stage 1 leakage has a resolution with no **unresolved** entries. The
third-party dependency matrix is complete for every direct dependency. Every
import cycle has a named break strategy. Module scope (owns / does not own) is
explicit.
