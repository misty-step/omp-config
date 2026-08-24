# Stage 4 — Extraction Blueprint & Phased Cutover

The blueprint sequences mechanical moves so each phase leaves the repo buildable
and testable. Pick the target phase based on operator intent; still document
all three so later promotion does not restart investigation.

## Procedure

1. **Choose the cutover target.** Record operator intent:
   - **Phase 1 only** — in-tree isolation sufficient;
   - **Phase 2** — independent workspace package inside the monorepo;
   - **Phase 3** — external package or standalone repository.
2. **Phase 1 — In-tree directory isolation.**
   - Target directory path (e.g. `packages/foo/` or `internal/foo/`).
   - `index` / barrel export file: exact public API from Stage 3.
   - Internal subtree layout (`internal/`, `private/`, or language convention).
   - Import path changes: every caller migration listed file-by-file.
   - Build config changes (`tsconfig` paths, `go.mod` replace, Rust crate
     boundaries).
   - Verification: commands that must pass before Phase 1 is declared done.
3. **Phase 2 — Monorepo workspace package.**
   - Package name, workspace manifest entry (`package.json`, `go.work`,
     `Cargo.toml` workspace member).
   - Independent build command and test suite scope.
   - Versioning and publish config (private registry vs npm public).
   - Consumer migration: how in-repo callers import the workspace package.
   - CI job boundaries: package builds and tests in isolation.
4. **Phase 3 — External package / standalone repository.**
   - Repository name, default branch, and release tagging strategy.
   - What moves out vs what stays in the monorepo (consumers, codegen, deploy
     hooks).
   - Release pipeline, changelog ownership, and backward-compatibility policy.
   - Consumer upgrade path and deprecation window for old import paths.
5. **Ordered cutover steps.** Numbered list of atomic commits or PR slices:
   each step names files touched, migration direction, and the verification
   command. No step leaves the repo in a broken intermediate state without an
   explicit **WIP flag** and rollback note.
6. **Risk register.** For each phase: blast radius, rollback procedure, and
   signals that mean stop (test failures, fan-in symbols not yet migrated,
   unresolved cycles).
7. **Assemble the blueprint.** Use the
   [Extraction blueprint template](artifacts.md#extraction-blueprint) in
   `artifacts.md`. Attach completed templates from Stages 1–3.

## Completion criterion

Phase 1 directory layout, public `index` export boundary, and caller migration
list are specified file-by-file. Phase 2 workspace package manifest, isolated
build/test commands, and CI boundaries are specified when Phase 2 or 3 is the
target. Phase 3 repository, release, and consumer upgrade path are specified
when Phase 3 is the target. The ordered cutover steps are numbered with a
verification command per step. The risk register covers every phase through
the chosen target. The assembled artifact includes the coupling map, deletion
ledger, dependency matrix, and extraction blueprint — ready for implementation
without reopening Stages 1–3.
