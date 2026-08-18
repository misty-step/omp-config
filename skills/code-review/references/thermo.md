# Thermo

Be ambitious about structure. Search for a code-judo move that preserves
behavior and deletes branches, helpers, modes, or layers.

Flag:

- a file the change pushes across 1000 lines;
- ad-hoc conditionals bolted onto unrelated flows;
- thin wrappers and identity abstractions;
- casts, `any`, `unknown`, or optional fields that hide the invariant;
- logic in the wrong layer;
- sequential orchestration of independent work;
- partial updates that leave state half-applied;
- refactors that move complexity without reducing it.

Do not approve because it works. Prefer a smaller number of high-conviction
structural findings over nits.
