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

# Naming

Choose precise, professional domain vocabulary for files, scripts, directories,
symbols, branches, commits, and interface labels. Names should state purpose or
behavior, not personality: no slang, chat shorthand, or cute and clever names.
Prefer explicit terms to opaque abbreviations, while retaining standard technical
vocabulary and established protocol or API names. Follow the project's casing
conventions; do not rename unrelated code merely to impose this preference.

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

Repository docs own version-bound behavior, interfaces, accepted technical
decisions, and reusable operating procedures. Work records own priorities,
owners, blockers, and change-specific conclusions. Link maintained procedures
instead of copying them into a second manual. Retain raw run evidence under its
appropriate artifact and privacy lifecycle; curated fixtures and shipped assets
remain source inputs, and runtime ledgers remain runtime authority.

A vision document is optional context, not a product lock or a mandatory first
read. Preserve useful purpose, constraints, and non-goals where they help the
current task; remove duplicated roadmaps and stale prescriptions. Current
operator direction and observed behavior outrank inherited prose.

# Visual design

For new operator-owned surfaces without an established identity, draw on U.S.
Graphics Company's engineering functionalism: expose real state and inner
workings, favor dense but legible information, and make typography, alignment,
rules, and color explain the system. Use deliberate monospaced typography where
it aids comparison or technical character. Performance and accessibility are
design properties, not concessions to the aesthetic.

Use ASCII or box-drawing diagrams when they make technical relationships easier
to understand. Character art, halftone, and dithering can provide a distinctive
image treatment; keep controls and essential content readable, selectable, and
accessible. Avoid decorative terminal noise, gratuitous banners, and continuous
CRT or glitch effects. Respect existing product identities and explicit briefs;
this is a design direction, not a universal skin.
