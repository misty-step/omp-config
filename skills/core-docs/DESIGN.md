# Core documentation design note

This note defines the core documentation standard for fleet repositories.

## Audit findings

We surveyed eight targets across R90 and Misty Step.

### Olympus (R90 repository)
Olympus provides the mature exemplar. It maintains all five core documents: `README.md`, `AGENTS.md`, `VISION.md`, `GLOSSARY.md`, and `docs/adr/`.
`GLOSSARY.md` establishes a binding ubiquitous language. It categorizes terms into owned assets, external systems, agent behaviors, and retired words.
`AGENTS.md` acts as a tight router. It points to authoritative documents and defines non-negotiable invariants.
`VISION.md` defines product identity and deliberate architectural refusals.
Six active ADRs (`0021` through `0026`) record architectural decisions cleanly.

### Habitat (R90 repository)
Habitat maintains `README.md`, `AGENTS.md`, `VISION.md`, and ten ADRs in `docs/adr/`.
Its ADRs show naming and maturity variance. Records use `ha-` and `bug-` prefixes.
Record `ha-005` remains in status Proposed as a 450-line extraction plan.
Habitat lacks `DOMAIN.md` or a glossary. Because it lacks a domain document, `AGENTS.md` grew to 327 lines with duplicated schemas and setup commands.

### Tach (`agent-usage-telemetry`, R90 repository)
Tach maintains `README.md`, `VISION.md`, `DATA.md`, and `WATCHDOG.md`. It lacks `AGENTS.md`, `DOMAIN.md`, and `docs/adr/`.
`DATA.md` defines domain data contracts well. However, agents lack an entry router and durable decision records.

### omp-config (Misty Step repository)
omp-config maintains `README.md`, `CANON.md`, `global/AGENTS.md`, and `global/RULES.md`.
Its `global/` directory stores session context, core rules, and watchdog configuration.
Its `skills/` directory holds forty-one skills using explicit operator or model invocation.
It currently lacks a root `AGENTS.md` and `CLAUDE.md` symlink. This absence represents an active rollout gap.
The repository exhibits duplication. `global/RULES.md` repeats deletion and verification principles from `CANON.md` and `global/AGENTS.md`.
The `writing-for-agents` guide sits under `.agents/skills/` rather than the deployed `skills/` directory.
It lacks repository-local `VISION.md`, `DOMAIN.md`, and `docs/adr/` because it configures the harness.

### Iron Forest (Misty Step repository)
Iron Forest maintains `README.md`, `VISION.md`, `AGENTS.md` (46 lines), and twenty-one ADRs.
It lacks `DOMAIN.md`.
Domain concepts like Builder, Verifier, and Kernel repeat across `README.md` and ADRs without a single domain document.

### Daybook (Misty Step repository)
Daybook maintains `README.md` and `AGENTS.md` (247 lines). It lacks `VISION.md`, `DOMAIN.md`, and `docs/adr/`.
Documentation drift exists. `README.md` forbids creating journal entries, while `AGENTS.md` permits creating absent entries.

### Finances (Misty Step repository)
Finances maintains `README.md`, `AGENTS.md` (56 lines), and one ADR (`0001-simplefin-integration.md`).
It lacks `VISION.md` and `DOMAIN.md`.
`AGENTS.md` carries domain ledger data contracts that belong in a dedicated domain document.

### Misty Step organization root (`~/Development/misty-step/AGENTS.md`)
The organization root `AGENTS.md` defines fleet accounts, infrastructure, and boundaries with R90.
It states: "Do not copy project context up here."
It acts as an organization router rather than a project document.

## External best practices

We evaluated four industry documentation models against fleet requirements.

### AGENTS.md router pattern
Agents read `AGENTS.md` on every turn or session start.
Always-loaded text consumes context tokens and dilutes model attention.
Strong index patterns separate routing from documentation. Pointers name out-of-context documents and define trigger conditions.
Progressive disclosure keeps primary files clean. Reference material stays behind pointers until an agent needs it.
A router document must stay under one hundred lines.

### Domain-Driven Design ubiquitous language
Eric Evans and Martin Fowler define ubiquitous language within a bounded context.
It establishes a single rigorous vocabulary.
Two terms for one concept creates defects. One term with two meanings causes worse failures.
Effective domain documents divide terms into owned entities, external systems, and lifecycle transitions.
A table of retired terms stops obsolete concepts from re-entering prompts and code.

### Architectural Decision Records
Michael Nygard introduced ADRs in 2011 to document architecture decisions.
Each record tracks title, status, context, decision in active voice, and consequences.
Markdown Architectural Decision Records (MADR) standardized this format for version control.
Durable decision records explain why an architecture exists. Code and configuration show only what exists.
Git retains commit history, but ADRs explain the rejected alternatives and accepted tradeoffs.

### Vision documents
A vision document establishes the product North Star.
It defines target users, operational premises, and long-term direction.
The most effective section defines deliberate non-goals. Olympus and Tach call this section "What we refuse."
Stating explicit refusals prevents agents from rebuilding deleted abstractions.

## Principles and decisions

The principal established core documentation rules:

1. **Minimal documentation:**
   Documents record only what code cannot reveal.
   They explain philosophy, non-obvious invariants, domain boundaries, and decisions.
   They never describe implementation mechanics.

2. **README role:**
   README records non-obvious operational truth: identity, external prerequisites, and the canonical gate.
   It never restates discoverable package scripts or compiler invocations.

3. **Domain document naming:**
   Olympus proved this pattern using `GLOSSARY.md` as prior art.
   The principal selected `DOMAIN.md` as the fleet standard.
   This name unifies domain entities, data contracts, state models, and retired terms.
4. **Direct deletion of bloat:**
   Overhauling bloated files deletes code-discoverable text outright.
   We never create archive directories. Git commit history retains deleted text.

5. **Unified symlink standard:**
   `CLAUDE.md` must always exist as a symlink pointing to `AGENTS.md`.
   This rule binds across all fleet repositories.

6. **Consultative workflow:**
   The skill explores and investigates code first.
   The agent brainstorms with the operator to acquire missing non-obvious context before writing.

## Composition architecture

The survey reveals a two-tier documentation architecture across fleet repositories.

### Tier 1: Universal Base Floor
Every repository requires:
1. `README.md` (Operational truth: entrypoint identity, non-obvious prerequisites, and the canonical gate).
2. `AGENTS.md` (Agent router: non-negotiable invariants, stop signals, and authority pointers).
3. `CLAUDE.md` (Always exists as a symlink pointing to `AGENTS.md`).

Repositories currently lacking root router files treat this as a rollout repair gap.
### Tier 2: Conditional Core Documents
Repositories add these documents when they own those boundaries:
3. `VISION.md`: Required when the repository defines an external product identity, multi-user surface, or strategic refusals.
4. `DOMAIN.md`: Required when the repository defines domain models, state machines, or ubiquitous language.
5. `docs/adr/`: Required when the repository makes non-obvious, high-consequence architectural choices.

## Content contracts

### README.md
- Belongs: Operational identity, non-obvious environment prerequisites, canonical quality gate command, and core document pointers.
- Must never appear: Discoverable package script mirrors, dependency inventories, code walkthroughs, and generic tutorials.

### AGENTS.md
- Belongs: Brief orientation, core document pointers, non-negotiable repository invariants, hard stop signals, ground-truth ownership table, and commit protocol.
- Must never appear: Duplicated setup commands, coding tutorials, class summaries, ticket dumps, secrets, and detailed domain definitions. Length must stay under one hundred lines.

### VISION.md
- Belongs: Product purpose, target audience, core operating bet, strategic direction, deliberate non-goals ("What we refuse"), and ADR references.
- Must never appear: Day-to-day task lists, sprint backlogs, implementation mechanics, code snippets, and ephemeral status.

### DOMAIN.md
- Belongs: Ubiquitous language for owned assets, external systems, lifecycles, and retired terms.
- Must never appear: General computing definitions (HTTP, JSON), framework documentation, code syntax, and speculative buzzwords.

### docs/adr/
- Belongs: Numbered records (`NNNN-slug.md`) with status, date, context, decision in active voice, and consequences.
- Must never appear: Meeting minutes, trivial code review comments, routine dependency updates, and unsettled debates.

## Quality enforcement and rollout

Enforcement uses the skill checklist rather than third-language scripts.

The skill audits documents against explicit contracts:
1. Verifies required core files exist based on repository scope.
2. Verifies `README.md` omits discoverable package scripts.
3. Verifies `AGENTS.md` acts as a tight router under one hundred lines.
4. Verifies `CLAUDE.md` exists and is a symlink pointing to `AGENTS.md`.
5. Verifies all relative markdown links resolve to existing files.
6. Verifies sentences comply with ASD-STE 100 limits (maximum twenty words).

Rollout proceeds repository by repository:
1. Explore the repository and audit existing core documents.
2. Brainstorm with the operator to capture non-obvious context.
3. Author or overhaul documents in an uncommitted working tree.
4. Human reviews diffs. PRs open only after principal alignment.

## Settled decisions

The principal settled the core policy:
1. **Base floor:** Repositories maintain only `README.md` and `AGENTS.md` unless domain boundaries require conditional documents.
2. **Domain naming:** The ubiquitous language document is named `DOMAIN.md`.
3. **Bloat migration:** Overhauls delete code-discoverable text directly without archive directories.
4. **Tooling symlink:** `CLAUDE.md` is always a symlink pointing to `AGENTS.md`.
