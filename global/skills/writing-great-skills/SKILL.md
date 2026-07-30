---
name: writing-great-skills
description: Reference for writing and editing skills well — the vocabulary and principles that make a skill predictable.
disable-model-invocation: true
---

A skill extracts determinism from a stochastic system. **Predictability** means
that the agent follows the same _process_ on every run, not the same output.
A brainstorming skill can _predictably_ diverge: its tokens vary, but its
behaviour does not. Predictability is the root virtue; cost and maintainability
support it.

**Bold terms** are defined in [`GLOSSARY.md`](GLOSSARY.md). Look them up there.

## Invocation

Invocation offers two choices with different costs:

- A **model-invoked** skill keeps a **description**. The agent can fire it
  autonomously, and the human can still type its name. Model-invocation always
  includes user reach. The description adds agent discovery; it never removes
  human reach. It adds permanent **context load** on every turn. Other skills can
  reach it. If its content is all **reference**, it can host shared reference.
  Omit `disable-model-invocation` and write a model-facing description with
  distinct trigger branches.
- A **user-invoked** skill removes its description from the agent's reach. Only
  the human can invoke it by typing its name. It has zero **context load**, but
  it adds **cognitive load** because the human must remember it. Set
  `disable-model-invocation: true`; make the `description` human-facing with
  one line and no trigger list.

Pick model-invocation only when the agent or another skill must reach the skill.
If it fires only by hand, make it user-invoked and pay no context load.

When user-invoked skills multiply beyond memory, use a **router skill**. It names
the other skills and when to reach for each. The human remembers one skill.

## Writing the description

A model-invoked **description** does two jobs. It states what the skill does and
lists the **branches** that trigger it. Every word adds **context load**, so prune
the description more aggressively than the body:

- **Front-load the skill's leading word.** The description performs invocation.
- **Use one trigger per branch.** Synonyms for one branch are **duplication**.
  Collapse them. Keep only distinct branches.
- **Cut identity already in the body.** Keep triggers and any reach clause for
  another skill.

## Information hierarchy

A skill contains **steps**, **reference**, or both. Arrange each item on the
**information hierarchy** by how soon the agent needs it:

1. **In-skill step** — an ordered action in `SKILL.md`. Each step ends on a
   **completion criterion**. Make it _checkable_ and, where needed, _exhaustive_.
   "Every modified model accounted for" is stronger than "produce a change list."
   A vague criterion invites **premature completion**.
2. **In-skill reference** — a definition, rule, or fact in `SKILL.md`, consulted
   on demand. A flat peer-set can be correct. _This skill is all reference._
3. **External reference** — **reference** moved out of `SKILL.md` into a separate
   file behind a **context pointer**. A sibling file such as `GLOSSARY.md` is
   disclosed reference. Fully external reference lives outside the skill system.

A demanding completion criterion drives **legwork**, whether the skill has steps
or not. "Every rule applied" binds flat reference as "every step done" binds a
sequence.

Push down material that the agent does not need immediately. Keep material at
the top when the agent needs it on every path.

**Progressive disclosure** moves **reference** down the ladder into a linked
file. Keep the top legible. Use a `.md` file in the skill folder for disclosed
reference. Each distinct use is a **branch**. Inline material that every branch
needs. Disclose material that only some branches need. A **context pointer**'s
wording controls when and how reliably the agent reaches its target.

The ladder decides how far down material sits. **Co-location** decides what sits
beside it. Keep a concept's definition, rules, and caveats under one heading.

## When to split

**Granularity** describes how finely you divide skills. Each cut spends one load,
so make a cut only when it earns its cost:

- **By invocation** — split off a **model-invoked** skill when a distinct
  **leading word** should trigger it, or another skill must reach it. Its
  always-loaded **description** must justify its **context load**.
- **By sequence** — split steps when later **post-completion steps** tempt the
  agent toward **premature completion**. Hide later steps so the agent does more
  **legwork** on the current task.

## Pruning

Keep each meaning in a **single source of truth**. Change behaviour in one place.

Check every line for **relevance**. Keep it only when it bears on the skill.

Run the **no-op** test on every sentence, not only every line. Delete a sentence
that does not change behaviour. Do not trim it into a weaker restatement.

## Leading words

A **leading word** is a compact concept already in the model's pretraining. The
agent thinks with it while running the skill. It encodes a principle in few
tokens by invoking existing priors. Examples include _lesson_, _fog of war_, and
_tracer bullets_. Repeat the token when it anchors one region of behaviour.

A leading word serves **Predictability** twice. In the body it anchors
_execution_. In the description it anchors _invocation_. Use the same word in
prompts, docs, and code when you want the skill to fire reliably.

Refactor repeated explanations into leading words. Use a single token instead
of spelling out one idea at several sites. Examples:

- "fast, deterministic, low-overhead" -> _tight_ — one quality across a phase.
- "a loop you believe in" -> _red_ — a binary gate that marks a bug.

Fewer tokens and a sharper hook improve predictability. Find restatements that
leading words can retire.

## Failure modes

Use these terms to diagnose skill problems:

- **Premature completion** — ending a step before it is genuinely done. First
  sharpen the **completion criterion**. If it remains fuzzy and the rush occurs,
  hide **post-completion steps** by splitting the sequence.
- **Duplication** — giving the same meaning in more than one place. It costs
  maintenance and tokens and raises that meaning above its proper rank.
- **Sediment** — stale layers that settle because adding feels safe and removing
  feels risky. A pruning discipline prevents sediment.
- **Sprawl** — a skill that is too long, even when every line is live and unique.
  Use the ladder: disclose **reference** behind pointers and split by **branch**
  or sequence.
- **No-op** — a line the model already follows by default. Ask whether it
  changes behaviour. Replace a weak leading word with a stronger one, not another
  technique.
- **Negation** — steering through prohibition. It names the forbidden behaviour
  and makes it more available. Prompt the **positive** target instead. Keep a
  prohibition only as a hard guardrail that cannot use positive wording, and pair
  it with the required action.
