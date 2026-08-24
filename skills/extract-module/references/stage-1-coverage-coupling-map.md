# Stage 1 — Coverage & Coupling Map

Map the territory before drawing a boundary. The coupling map is the evidence
base every later stage inherits.

## Procedure

1. **Frame the candidate.** State the extraction candidate: directory paths,
   owning concepts, and explicit non-goals for this investigation.
2. **Discover subsystems.** Walk inward from the candidate and outward to
   callers. List:
   - files and modules inside the candidate boundary (as it exists today);
   - direct and transitive callers outside the candidate;
   - sibling modules that share types, config, or runtime state with the
     candidate.
3. **Measure fan-in and fan-out per exported symbol.** For each public export
   (function, class, type, constant, re-export):
   - **Fan-in** — count and list distinct caller modules via `lsp references`.
     Group by package/directory.
   - **Fan-out** — count and list distinct dependencies the candidate imports
     from outside itself. Trace through re-exports and barrel files.
   Record hot symbols: high fan-in exports and high fan-out imports.
4. **Structural coupling scan.** Use `ast-grep` (read `skill://ast-grep`) to
   find patterns that text search misses:
   - deep imports past the intended boundary (`../../internal/...`);
   - type assertions and casts that couple to foreign shapes;
   - shared mutable singletons or module-level state accessed across
     boundaries;
   - duplicate type definitions mirroring foreign modules.
5. **Circular imports.** Enumerate every import cycle that touches the
   candidate. For each cycle, record participating modules and the dependency
   edge that would break the cycle with least blast radius.
6. **Leakages.** Name every coupling that is not a plain import:
   - leaked types (DTOs, error types, config structs) defined in the candidate
     but consumed by callers, or vice versa;
   - shared test fixtures, golden files, or snapshot directories;
   - environment variables, feature flags, and config keys both sides read;
   - implicit contracts (error string matching, log format, metric names);
   - build-time coupling (shared `tsconfig` paths, codegen, protobuf packages).
7. **Assemble the coupling map.** Use the
   [Coupling map template](artifacts.md#coupling-map) in `artifacts.md`.

Rank findings: extraction blockers first (cycles, hard runtime coupling), then
high fan-in symbols that constrain the public API, then leakages.

## Completion criterion

The coupling map template is complete. Every exported symbol in the candidate
has fan-in and fan-out counts with cited caller/dependency paths. Every import
cycle touching the candidate is listed with a proposed break edge. Every
leakage is classified with file evidence. Subsystems inside and outside the
candidate are enumerated with paths. Non-goals for this investigation are
explicit.
