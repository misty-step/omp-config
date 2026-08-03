# Architecture

Load this reference after `/quality` selects `architecture`. It supplies the source-structure oracle and branch-specific routes.

## Boundary

Judge structure, interfaces, and test defense from source. Keep the inventory source-only. Do not drive a browser or infer runtime behavior from source. Route runtime claims to `skill://verify-live` or select the `product` branch.

Dispatch read-only lanes through `skill://dispatch`. Name the native role, scope, oracle, evidence contract, and non-goals in every brief.

## Source inventory

Use a read-only `researcher` to inventory:

- public APIs, routes, CLIs, jobs, extension points, and schemas;
- every module, interface, and caller;
- tests, quality gates, ADRs, and project rules.

Name every reachable entrypoint with its file path. Record absent surfaces and unknowns with an explicit reason. Do not infer an entrypoint or contract.

## Accepted target state

Freeze accepted, measurable target clauses in `.evidence/quality/architecture/target-state.md` before structural judgment. Keep the machine target in the architecture assessment `targets[]`; render the Markdown record from that data. Treat the accepted target as the only oracle.

Apply these target lenses to each named module and interface:

- **Strategic design:** judge future modification cost. Name tactical structure that accreted without a chosen owner. Name each load-bearing abstraction and why it earns its maintenance cost.
- **Deep modules:** state the interface a caller must learn and the complexity it hides. Flag shallow modules, pass-through layers, and generic `Manager`, `Util`, or `Helper` modules. Apply the deletion test: deletion that removes complexity exposes a pass-through; deletion that spreads complexity across callers shows an abstraction that earns its keep.
- **Complexity ownership:** assign each hard problem to one module. Flag configuration, caveats, ordering rules, error handling, and change amplification repeated across callers.
- **Information hiding:** keep each data structure, algorithm, storage format, and dependency decision inside one module. Name temporal decomposition when execution order leaks instead of knowledge.
- **Public contracts:** state inputs, outputs, invariants, and error behavior for every public interface.

## Audit methods

Dispatch one fresh, non-mutating verifier per selected lens. Use the Ousterhout (`ousterhout`) and `delete-first` lenses from `global/references/lenses.md`. Use `skill://review-tests` for observable-contract test defense; apply its checks instead of restating them here.

Require every lane to return a finding or an explicit clean pass. Each finding names file and line evidence, the violated target clause, severity, and a correction shape. Source evidence is required for every structural claim.

Prefer deletion over wrappers when deletion passes the target and keeps the contract intact. Send coupled decomposition questions to an `architect` before implementation. Keep structural remediation slices independent when their interfaces do not couple.

## Independent proof

A fresh, non-mutating verifier re-runs the originating lens after remediation. The remediating lane never verifies its own change. Use `skill://review-tests` for changed contract defenses and `skill://verify-live` for any runtime claim. Preserve every strength recorded in the assessment; a lost strength is a regression, not closure.

## Evidence location

Store architecture evidence under `.evidence/quality/architecture/`. Keep `target-state.md`, `assessment.json`, and the rendered `assessment.md` there. Link each inventory fact, target clause, finding, remediation result, independent proof, preserved strength, and blocker to evidence in that directory.
