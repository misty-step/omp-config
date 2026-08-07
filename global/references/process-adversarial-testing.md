# Process adversarial testing

Use this when the change is a **multi-agent process**, not only product code.

Ordinary unit tests prove functions. They do not prove a squad, gate, or
lifecycle under delay, flake, and illegal ordering.

## When required

Require process-level proof when you change any of:

- dispatch roster, spawn graph, or recursion ceilings
- review / ship receipt gate
- qa-users freeze → persona → chief write lifecycle
- recipe sealed launch or other fixed harness protocol
- loop or daemon orchestration owned in this org (see Iron Forest for delivery FSM sim)

Skip this bar for ordinary feature work inside one skill body with no protocol change.

## Minimum kit

1. **States and transitions** — name durable states, legal events, halt states, and illegal moves.
2. **Simulator or deterministic harness** — drive the protocol without relying on a single golden chat transcript.
3. **Fault model** — at least delay, failure, duplicate, and out-of-order where the protocol allows concurrency.
4. **N-run or multi-seed campaign** — more than one path; fixed seeds when random.
5. **Human-owned oracles** — invariants agents implement against; agents rarely invent the regime.
6. **Halt rules** — budget, attempt cap, and fail-closed behavior.

## Ownership split

| Layer | Owner |
|---|---|
| OMP fixed protocols (review gate, qa-users, recipes) | omp-config tests + FSM notes |
| Product delivery daemon (Builder/Verifier/Fixer) | Iron Forest (`forest sim`, delivery FSM) |
| One-off session workflows | Mode A chief; not an unattended loop |

Do not build a global theme → Gherkin → architecture waterfall into OMP.
Do not grow an agent zoo for cleaner/hardener/gherkin-author roles. Encode
phases as checks, skills, or protocol steps on broad agents.

## Relationship

- `verification-system-first.md` — claim, falsifier, driver, grader, evidence.
- `testing-principles.md` — one journey per test; process campaigns are journeys over the protocol.
- `loop-readiness.md` — unattended loops need verifier, budget, and halt rules first.
- Iron Forest issues track productized `forest sim`; this file is the omp-config duty.

## Stop rule

If you cannot name an illegal transition and a test that would catch it, the
protocol change is not ready to ship.
