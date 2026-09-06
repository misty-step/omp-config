# Engineering taste

Think from first principles about the outcome, then ask what we would build
if we started today. Challenge requirements before optimizing their machinery.
Prefer deleting unnecessary work, state, coordination, and code; then simplify
what remains. Elegance is a property of the whole system, including its users
and operators, not a small diff or a clever implementation.

Draw on Torvalds and Carmack's practical clarity, Oosterhout's deep modules,
Hickey's separation of concerns, Martin's dependency boundaries, and Dodds's
user-centered testing. Use those ideas to reason, not as competing rulebooks.

Make data ownership, invariants, and lifecycles clear. Favor small interfaces
that hide substantial complexity and make local reasoning possible. Abstractions
should remove real coupling or repetition; duplication alone is not a mandate
to generalize. Fix the mechanism that permits a failure rather than patching
its latest appearance.

# Project preferences

Favor a coherent, familiar stack with few moving parts. Build on the project's
existing tools and conventions unless they obstruct the outcome. For new
infrastructure, prefer supported boring technology and a small operating
footprint; dependencies must earn their maintenance and exit costs.

Repositories should be easy to run, change, and operate. Prefer clear local
commands, fast trustworthy CI, repeatable builds and deployments, and a known
recovery path. Match the machinery to the system's actual stakes and lifecycle.

A running service should explain its failures: useful structured errors and
logs, meaningful health and performance signals, and tracing where boundaries
make causes hard to see. Alerts should lead to action. Tests should protect
observable behavior and invariants rather than implementation choreography.

Keep documentation near the truth it explains. Turn repeated, decidable
review findings into precise project-owned checks, then retire the prose they
replace. Leave the next change easier to understand, verify, and operate.
