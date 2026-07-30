# Execution overrides

`validateInputSemantics(input, { cli, harnessDefaults })` is the single public
resolver entry point. It returns all 11 output fields plus structured
provenance. Precedence is `cli`, then `input`, then `harness-default`; every
field records the winning source. The `cli` and `harnessDefaults` objects use
output-field names only, including `selected_tracker`; the input document
keeps its `tracker` and `execution_overrides.tracker` names.
After precedence and normalization, the complete output is validated against
the `execution.v1` `output_overrides` definition. Bounds and types therefore
apply identically to CLI, input, and harness defaults; diagnostics name the
field and winning source.

The effective entrypoint set is a nonempty, unique string array. Every ID
must be declared in `input.entrypoints`, and every persona assignment must be
contained in the final set. A CLI or harness-default exclusion that drops a
persona assignment is an error; a fallback ID not declared by input is also an
error. A defined malformed `execution_overrides.entrypoints` value is an error;
it never falls back to the declared entrypoints.

Every declared entrypoint has a required environment of `local`, `dev`, or
`staging`. The root rejects production and unknown environments before any
browser leaf starts.

Issue thresholds resolve as follows:

- `configured` copies the input threshold object.
- `stricter.v1` maps severity `info→low→medium→high→critical→critical` and
  adds `0.10` to minimum confidence, capped at `1.0`.

`minimum_confidence` is finite and bounded from `0` through `1` for every
source, before and after the `stricter.v1` transformation.

The resolved threshold object and `source` plus `rule` are recorded in
`execution_overrides.provenance.issue_threshold`.

A dry run is the Plan phase only. It resolves personas, effective entrypoints,
all execution overrides, tracker selection, environments, and ceilings without
opening an application, invoking a persona, querying or writing a tracker, or
invoking a handoff. It emits no findings, strengths, suppressed friction,
tracker pages, creates, or read-backs; every persona is `planned` with zero
evidence. The normal run uses the same input without `--dry-run` and emits
`output.v1`.
