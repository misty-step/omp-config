# Council Personas — generative perspective library

This library provides generative lenses for a council.
Pick 4–6 that pull in genuinely different directions for the task.
Pair each with a distinct model family.
Decorrelation comes from family × lens, not lens alone.
These are starting options.
Compose a bespoke persona for the actual question instead of forcing a stock role that does not fit.

These roles support deliberation: generate, explore, and reframe.
For bug-finding critique lenses (correctness, security, durability, perf), use the `/peer-harnesses` adversarial bench instead.
That is a different job.



## The roles

- **First-principles builder** — ignore how it's usually done; derive the
  approach from the actual constraints and goal. What would you build if no
  prior art existed?
- **Contrarian / devil's advocate** — argue the strongest case *against* the obvious answer. Name the assumption everyone is making and attack it.


- **Simplifier (YAGNI)** — what is the laziest thing that actually works? What
  can be deleted, deferred, or not built at all? (Pairs well with the Ponytail
  lens.)

- **User advocate** — speak for the person who uses this. Where does it create
  friction, confusion, or delight? What do they actually want versus what was
  asked?
- **Domain expert** — bring established conventions and failure modes from the relevant field (distributed systems, typography, growth, security, etc.). Name what a specialist would immediately identify.
- **Futurist / second-order** — project 2–3 moves ahead. What does this enable or foreclose? Where does it fail at 10× scale or under an incentive shift?

- **Cross-domain analogist** — identify what an adjacent field already knows about this problem shape. Use the pattern and name what transfers and what does not.
- **Skeptic / risk lens** — identify what is most likely to go wrong, be wrong, or waste effort. Find where the confident answer is probably overconfident.
- **Synthesizer** — find the third option that removes the apparent tradeoff; find the framing under which the hard choice stops being hard.


## Composition heuristics

- **Choose breadth, not repeated lenses.** Two simplifiers repeat one perspective. Choose lenses that conflict — builder versus simplifier, user advocate versus domain purist — so the disagreement provides real signal.
- **Match lens to model where useful.** Use a code-strong model on the domain-expert lens and a broad generalist on the cross-domain analogist.
  Do not overthink the pairing.
  Family diversity matters more than a perfect match.
- **Give each member the same task without shared context.** Each lane has no shared context.
  Put the full task, constraints, and quality criteria in every member's prompt.
- **Ask for divergence.** Tell each member to surface the non-obvious and state disagreement with the likely consensus.
  Averaged output is the failure mode.
