# Review council

The council finds release risk through independent model families. More agents
do not make a review stronger; distinct evidence and immutable scope do.

## Roster

A trivial local change uses one `scout` with `torvalds.md` and `thermo.md`.
Other executable changes use three parallel lanes:

| Lane | Agent | Primary Selector | Fallback Order | References | Focus |
|---|---|---|---|---|---|
| Structure | `scout` | `@slow` (`openai-codex/gpt-5.6-sol:max`) | `cursor/gpt-5.6-sol:max` → `anthropic/claude-fable-5:max` | `torvalds.md`, `ousterhout.md`, `hickey.md`, `taelin.md` | Data ownership, invalid states, module boundaries |
| Behavior | `scout` | `anthropic/claude-fable-5:max` | `cursor/gpt-5.6-sol:max` → `google-antigravity/gemini-3.7-flash:high` | `uncle-bob.md`, `kcd.md` | Contracts, failure paths, tests |
| Practicality | `scout` | `xai-oauth/grok-4.6:xhigh` | `google-antigravity/gemini-3.7-flash:high` → `kimi-code/k3:max` | `carmack.md`, `thermo.md`, `ponytail.md` | Inspectability, cost, YAGNI |

Auth, secrets, privilege, cryptography, or trust-boundary changes also require
operator-invoked `/security-review`.

## Packet

Freeze one packet before dispatch:

- base and exact head SHA;
- complete diff and affected surrounding code;
- accepted intent, invariants, removals, and non-goals;
- checks, real-surface observations, and inspected evidence;
- deployed entrypoints when release behavior is relevant;
- only that lane's references.

Each lane reviews only that SHA and exits after yielding. A head change creates a
new review. A lane reports its resolved model and zero to five findings:

```yaml
- symbol: exact file, symbol, or interface
  mechanism: trigger and failure
  evidence: observed or source-complete proof
  repair: smallest coherent repair
  severity: block | should | note
  scope: in | out
```

A clean lane says so. Missing output, model identity, packet fields, or exact-SHA
binding fails the lane.

## Judgment

Block only a supported violation of accepted correctness, security, data
integrity, migration, rollback, public contract, or required release proof that
this change causes or worsens. A required but absent migration blocks.

Use **Take** for useful non-blocking work. Default it to the follow-up record.
Use **Drop** for taste, speculative flexibility, unmeasured performance, and
unrelated debt.

The council is complete when every required lane returned and every finding has
one evidence-backed disposition.
