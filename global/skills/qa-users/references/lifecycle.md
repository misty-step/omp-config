# Lifecycle

A run is a bounded state machine. State table and illegal transitions:
[`fsm.md`](fsm.md). `qa-master` records each transition through freeze and
synthesis. The chief records tracker and PR transitions after the packet returns.

1. **Explore and mint.** `qa-master` explores repository and product docs, routes, scripts, project rules, and live non-production entrypoints. Browser use on the master is limited to entrypoint smoke or later reproduction confirmation. Mint personas from product evidence. Each persona includes mission, knowledge, and blind_spots. Ask the operator only for persona, access, or entrypoint facts tools cannot establish.
2. **Freeze.** Validate `input.v1` once with [`input-semantic.mjs`](input-semantic.mjs) and its fixture contract, passing the same `{ cli, harnessDefaults }` options used by the harness. The validator performs duplicate and membership checks, resolves execution overrides, and returns the effective entrypoint set, threshold, and structured provenance. Reject duplicate persona IDs, duplicate entrypoint IDs, undeclared IDs, persona references outside the final set, missing environments, and any environment other than `local`, `dev`, or `staging`.
3. **Dispatch.** Start exactly one browser-only `qa-persona` per frozen persona with the configured concurrency and session-length ceilings. Each leaf uses only its assigned real browser entrypoint and returns evidence. It does not inspect product source, tracker state, or issue APIs. A failed persona returns a `failure_reason`.
4. **Reproduce.** A candidate friction becomes a finding only after the same user-path observation is reproduced. Master may use browser only for that confirmation. Record exact steps, expected result, observed result, and evidence references.
5. **RCA.** Optional read-only RCA starts only after a confirmed reproduction. It may inspect confirmed runtime evidence and public runtime diagnostics. It cannot mutate application or tracker state. Record `root_cause` only when evidence directly establishes it; otherwise use `null`.
6. **Synthesize.** `qa-master` applies severity and confidence thresholds, accepts or suppresses findings, and keeps strengths and suppressed friction in the report. Non-actionable or below-threshold observations stay suppressed with a reason.
7. **Report packet.** Before emitting `output.v1`, run [`output-semantic.mjs`](output-semantic.mjs) against the resolved input and report. Reject missing, wrong, or duplicate `persona_id` values so the output set equals the selected input persona set. Emit frozen `execution_overrides`, provenance, persona statuses, findings, strengths, suppressed friction, and residual risk. Return the packet to the chief.
8. **Chief tracker write.** Exactly one serialized chief tracker writer performs fingerprinting and exhaustive deduplication, creates at most `maximum_creates` actionable findings, reads every created issue back, and assigns `tracker_issue_id` values. The chief may add PR comments or work-ledger notes from the packet.

A dry run stops after Freeze. It must not open the application for persona missions, invoke a persona, query a tracker, create an issue, or invoke a handoff.

`fix-and-pr` is a separate handoff. Request it only with explicit authorization, after the chief tracker writer has filed and read back issues, and with `inside_user_session: false`. It never runs in a persona session.
