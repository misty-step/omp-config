# Nonvisual Evidence

Use the smallest real-boundary artifact that proves the claim.

| Surface | Evidence |
|---|---|
| CLI | Command, exit status, output, and resulting state |
| TUI | Terminal recording and plain transcript |
| API or protocol | Real request, response, and resulting effect |
| Persistence or migration | State before and after restart or readback |
| Concurrency or ordering | Reproduction and ordered event or state trace |
| Performance | Same workload with before and after measurements |
| Infrastructure | Applied change, health probe, and operator-visible result |

## Capture

Use the real entry point. Record exact arguments and exit status. Keep stderr
when it explains the result.

For stateful behavior, prove the final state at its owning boundary. Do not infer
it from an adjacent log when direct readback is available.

For concurrency, reproduce the original execution order. Include timestamps or
sequence numbers that distinguish the correct order from the failure.

For performance, keep the workload, data, environment, warm-up, and measurement
method equal. Report the complete observed values. Do not use a screenshot of a
single favorable sample.

For infrastructure, use sanitized output. Include the health check that the
operator uses. Do not expose credentials, private addresses, customer data, or
unrelated production state.

## Inspect

Read the saved artifact. Confirm that it contains the declared command or
scenario, the observable result, and no secret.

Set `sanitized: true` and `inspected: true` only after this inspection.
