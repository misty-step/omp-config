# Glossary — Building Great Skills

This glossary defines the domain model for great skills. A skill extracts determinism from a stochastic system. **Predictability** is the root virtue, and every term below serves it. This file is the disclosed reference for [`writing-great-skills`](SKILL.md).

The terms use four axes: **Invocation**, **Information Hierarchy**, **Steering**, and **Pruning**. Each **failure mode** appears beside the lever that cures it.

**Bold terms** in definitions are defined in this glossary. Find each term by its heading.

## Predictability

Predictability is the degree to which a skill makes an agent follow the same
_process_ on every run, not produce the same output. A brainstorming skill can
_predictably_ diverge: its tokens vary, but its behaviour does not. Predictability
is the root virtue. Cost and maintainability support it.

_Avoid_: consistency, reliability, robustness, output-determinism

## Invocation

Invocation describes how a skill is reached and the two loads that the choice
costs.

### Model-Invoked

A skill is **model-invoked** when it keeps its **description** field. The agent
can see and fire it autonomously. The human can still type its name, so
model-invocation always includes user reach. A description adds agent discovery;
it never removes human reach. The skill pays permanent **context load** on every
turn. Other skills can reach it. If its content is all **reference**, it can host
shared reference. Pick model-invocation only when the agent must reach the skill
on its own. If it fires only by hand, remove the description and pay no context
load.

_Avoid_: ability, tool, capability

### User-Invoked

A **user-invoked** skill has no **description**. The agent cannot see it, and the
human reaches it by typing its name. User-invoked means user-_only_; **model-invoked**
means user-_and-agent_. User-invocation trades agent discovery for zero **context
load**. Only the human can reach it. Other skills cannot fire it.

_Avoid_: procedure, workflow, command

### Description

The **description** is a machine-readable trigger and the one **context pointer**
that a **model-invoked** skill keeps loaded. Its presence defines the invocation
axis. Keep it and the skill is model-invoked and reachable by other skills.
Delete it and the skill is **user-invoked** and human-only. The description
creates the skill's **context load**.

_Avoid_: frontmatter, summary

### Context Pointer

A **context pointer** names material outside the agent's current context and
states when to reach it. The **description** is the top-level pointer from the
context window to a skill. A pointer to a disclosed file works the same way one
level down. Its wording, not its target, controls when and how reliably the
agent reaches the material. A weak pointer to must-have material creates a
variance bug. Sharpen the wording first. Inline the material only if sharpening
fails.

_Avoid_: link, reference, import

### Context Load

**Context load** is the cost a **model-invoked** skill adds to the agent's
context window. Its always-loaded **description** spends tokens and attention.
User-invoked skills avoid this cost by having no description. Context load limits
how many model-invoked skills you split out.

_Avoid_: token cost, context bloat

### Cognitive Load

**Cognitive load** is the cost a **user-invoked** skill adds for the human. The
human must remember which skills exist and when to reach for each. This skill
acts as the human's index. Model-invocation removes this cost through agent
discovery. Cognitive load is the price of human agency, not a cost to minimize.
Spend it where human judgment matters. Remove it where it does not.

_Avoid_: human index, burden, overhead

### Router Skill

A **router skill** is a **user-invoked** skill that points to other user-invoked
skills. It names each skill and when to reach for it. It can hint but never fire
them because only the human can reach user-invoked skills. Use it to reduce
**cognitive load** when user-invoked skills multiply.

_Avoid_: dispatcher, menu, registry, index, router procedure

### Granularity

**Granularity** is how finely you divide skills. Finer division spends one of
the two loads. More **model-invoked** skills spend **context load** through more
descriptions. More **user-invoked** skills spend **cognitive load** through more
skills for the human to remember. Split by **invocation** when a distinct
**leading word** should trigger a skill. Split by **sequence** when later
**post-completion steps** need hiding. Merging sequences exposes later steps
and invites **premature completion**.

_Avoid_: chunking, modularity

## Information Hierarchy

### Information Hierarchy

The **information hierarchy** ranks skill content by how soon the agent needs
it. It has three rungs:

- **Steps** — in-file, primary content.
- **Reference**, in-file — secondary content.
- **Reference**, disclosed — content behind a **context pointer**.

A skill without **steps** uses the bottom two rungs. A flat peer-set can be
correct; every review rule can sit on one rung. Invocation is independent of
the hierarchy. A skill can be model- or user-invoked and use either content
type. In-file reference that should be disclosed buries steps and adds variance.
Keep the top legible. Push down material that the agent does not need yet.

_Avoid_: structure, organization, layout

### Steps

**Steps** are the ordered actions an agent performs. They are the primary tier
when a skill has them. Every step ends with a **completion criterion**, clear or
vague. A skill can contain only steps, only **reference**, or both.

_Avoid_: workflow, instructions, choreography

### Reference

**Reference** is material that the agent consults on demand. It includes
definitions, facts, parameters, examples, and conditional instructions. It is
secondary when a skill has **steps**. It is the entire content when a skill has
none. **Context pointers** reach reference, making it the main candidate for
**progressive disclosure**.

_Avoid_: supporting material, docs, background

### External Reference

**External reference** is **reference** outside the skill system. It is a plain
file with no **description** and no **steps**, so it is not invocable. Any skill
can point to it. It is the shared home for reference that need not fire on its
own. It is the only shared home for two **user-invoked** skills.

_Avoid_: doc, resource, knowledge base

### Progressive Disclosure

**Progressive disclosure** moves **reference** down the ladder and behind a
**context pointer**. It keeps the top legible and protects the **information
hierarchy**. Use **branching** to decide what to disclose. Inline what every
path needs. Disclose what only some paths need. If a pointer reaches must-have
material unreliably, sharpen its wording. Pull the material inline only if
sharpening fails.

_Avoid_: lazy loading, chunking

### Co-location

**Co-location** keeps a concept's definition, rules, and caveats under one
heading. Reading one part then brings its neighbours with it. The
**information hierarchy** ranks how far down each piece sits. Co-location
decides what sits beside it. Co-location differs from **Duplication**:
duplication repeats one meaning, while scattering fragments one meaning.

_Avoid_: grouping, clustering, cohesion

### Sprawl

_Failure mode._ **Sprawl** is a skill that is too long, regardless of whether
its lines are stale or repeated. Even an all-live, all-unique skill can sprawl.
Sprawl costs readability, maintainability, and tokens. Use the **information
hierarchy** to cure it. Push **reference** behind **context pointers**. Split by
**branch** or sequence so each path carries only what it needs. Sprawl differs
from **sediment**, which comes from stale accumulation, and **duplication**, which
comes from repeated meaning.

_Avoid_: bloat, length, size, verbosity

## Steering

Steering shapes an agent's runtime behaviour toward **Predictability**.

### Branch

A **branch** is a distinct way to invoke a skill. It is a case the skill handles,
so different runs take different paths. A skill with many steps can have many
branches. A linear skill has none.

_Avoid_: path, case, fork

### Leading Word

A **leading word** is a compact concept already in the model's pretraining. The
agent thinks with it while running a skill. A leading word, also called a
_Leitwort_, encodes a behavioural principle in few tokens by invoking existing
priors. Examples include _lesson_, _proximal zone of development_, _fog of war_,
and _tracer bullets_. Repeat the token, not a sentence, to anchor a region of
behaviour. Define a made-up word clearly; existing words recruit priors for free.

A leading word serves **Predictability** twice. In the body it anchors
**execution**. In the **description** it anchors **invocation**. Use the same
word in prompts, docs, and code when you want the skill to fire reliably.

_Avoid_: keyword, term, motif

### Completion Criterion

A **completion criterion** tells the agent when a unit of work is done. It gives
the target for judgment. Its **clarity** tells the agent whether work is done.
Clarity resists **premature completion**. A vague bound such as "understanding
reached" lets the agent stop and slip to the next step. This property needs
**steps** because premature completion occurs between steps.

Its **demand** sets **legwork**. "Every modified model accounted for" forces
thorough work; "produce a change list" does not. Demand can bind flat
**reference** as well as steps. Thus a skill without steps can require "every
rule applied". Strong criteria combine clear bounds with enough demand.

_Avoid_: done condition, exit condition, stopping rule

### Legwork

**Legwork** is the work an agent performs within one step. It includes reading
files, exploring the codebase, making changes, and finding needed information.
It stays below the step structure and remains controlled by the agent. A
**leading word** or a demanding **completion criterion** can raise legwork.
Missing demand or **premature completion** makes legwork thin.

_Avoid_: scope, effort, diligence, coverage

### Post-Completion Steps

**Post-completion steps** are the **steps** that follow the current step. When
visible, they pull the agent toward **premature completion**. Hide them by
splitting the sequence.

_Avoid_: horizon, fog of war, lookahead

### Premature Completion

_Failure mode._ **Premature completion** ends the current step before the work is
genuinely done. The agent's attention shifts to being done. This failure occurs
between **steps**. A skill without steps that quits early has thin **legwork**,
not premature completion.

Visible **post-completion steps** pull the agent forward. A clear **completion
criterion** resists that pull. Fuzziness makes premature completion possible.
First **sharpen the bound**. If it remains fuzzy and the rush occurs, split the
sequence to hide later steps. Use both levers in that order.
Hide later steps only across a real context boundary: a user-invoked hand-off
or subagent dispatch. An inline model-invoked call leaves later steps in
context and clears nothing.

_Avoid_: premature closure, the rush, rushing, shortcutting

### Negation

_Failure mode._ **Negation** steers by prohibition. It tells the agent what _not_
to do, names the forbidden behaviour, and makes it more available. _Don't think
of an elephant_ makes the elephant the active concept. _Never write verbose
comments_ makes verbosity the pattern in context. A strongly activated concept
overwrites the weak modifier.

Its **leading word** is the _elephant_: whatever the prohibition names. Prompt
the **positive** target instead. State the required behaviour, such as "write
one-line comments", so the forbidden behaviour never enters the frame. Keep a
prohibition only as a hard guardrail that cannot use positive wording. Pair it
with the required action.

_Avoid_: ironic rebound, don't-prompting, the pink elephant

## Pruning

Pruning keeps a skill lean. Pair each remedy with the failure it cures.

### Single Source of Truth

The desired state is a **single source of truth** for each meaning. A change to
skill behaviour then requires one edit. **Duplication** violates this state.

_Avoid_: home, canonical location

### Duplication

_Failure mode._ **Duplication** gives the same meaning more than one **single
source of truth**. It costs maintenance and tokens. It also raises the meaning's
prominence above its proper rank. A **leading word** repeats a token on purpose;
duplication repeats a meaning.

_Avoid_: repetition, redundancy

### Relevance

**Relevance** asks whether a line bears on what the skill does. A line loses
relevance when it never bears on the task or becomes stale as behaviour or the
world changes. Shorter skills are easier to keep relevant. **Relevance** differs
from **no-op**: relevance asks whether a line bears on the task, while no-op asks
whether it changes behaviour.

_Avoid_: load-bearing, staleness, freshness

### Sediment

_Failure mode._ **Sediment** is old content that settles because adding feels safe
and removing feels risky. Stale and irrelevant lines accumulate. The agent must
core down through them to find live content. Sediment is the default fate of a
skill without pruning discipline. It erodes **relevance**; **duplication** repeats
meaning instead.

_Avoid_: accretion, bloat, cruft, rot

### No-Op

_Failure mode._ A **no-op** is an instruction that changes nothing because the
model already follows it by default. It adds load without changing behaviour.
Test each line against the default. A line can be **relevant** and still be a
no-op. A weak **leading word** can also be a no-op; use a stronger word instead
of another technique.

A leading word is a _technique_; No-Op is a _verdict_ on a line. A leading word
can therefore be a no-op. This verdict depends on the model's default, not the
reader's preference. Run the skill to settle disagreement.

_Avoid_: redundant instruction, restating the obvious, belaboring
