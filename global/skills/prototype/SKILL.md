---
name: prototype
description: |
  Explore a design or product question before implementation. Clarify intent,
  dispatch parallel distinct directions, synthesize one browsable HTML catalog,
  and lock one direction before production work. Use for net-new UI, product
  surfaces, flows, or uncertain state models. Trigger: /prototype.
disable-model-invocation: true
argument-hint: "<surface-or-question> [intent] [N]"
---

# /prototype

Prototype to answer one question. Keep the artifact cheap, runnable, and
throwaway. Do not write production UI before the operator locks a direction.

## Route the question

Classify the question before you create files:

- **UI or product direction** — use the parallel exploration and HTML catalog
  flow below.
- **Logic, state, or data shape** — use a small state prototype. Keep the logic
  in a pure reducer, state machine, or function module. Put a thin TUI around
  it. Render the full state after every action. Do not force a visual catalog
  onto a logic question.
- **Existing surface with no new design decision** — do not prototype. Route a
  mechanical change to the owning implementation or accessibility skill.

State the question and the selected route at the top of the work artifact.
If the route is unclear, inspect the host code and ask the operator. Do not
start generation with an unstated assumption.

## Non-negotiable boundaries

- Keep exploration outside production paths. Use the host project's scratch or
  prototype convention. Do not add prototype routes to a production build.
- Use the host runtime, component library, tokens, and task runner. Do not add a
  package manager, dependency, or styling system for a prototype.
- Use fixtures and in-memory state by default. Do not call real mutations or
  write to a production database. Catalog-only notes may use `localStorage`;
  never treat those notes as product persistence.
- Make the artifact runnable with one documented command. A static catalog may
  use the host preview command or `python3 -m http.server` in its scratch
  directory.
- Keep the full direction set as a primary source until the lock is recorded.
  Fold only the selected direction into production. Remove the prototype
  switcher and losing directions from the production path.
- Do not add tests, polish, abstractions, or error handling that do not answer
  the question. The final implementation is held to the normal design gates.

## 1. Clarify intent before generation

Read `skill://dispatch` before substantive work. Apply the grilling contract
below, based on the upstream `grilling` skill: ask one decision question at a
time, recommend an answer, and wait for confirmation. Use facts from the
filesystem, live entrypoints, and existing design sources. Do not ask the
operator for facts that tools can establish.

Run a grilling-style clarification before dispatching directions:

1. Ask one decision question at a time.
2. Give one recommended answer with each question.
3. Resolve dependencies in order. Do not ask a downstream question before its
   prerequisite decision is settled.
4. Record each answer in an intent brief. Record facts with their source.
5. Wait for explicit confirmation that the brief is shared before generation.

The brief must state:

- audience and primary task;
- host route or reason no host route exists;
- content, data states, and required actions;
- fixed brand, platform, token, accessibility, and responsive constraints;
- success signals and known risks;
- what the prototype must decide;
- what is out of scope;
- direction count `N`.

Default `N` to **3**. Accept **2–5** when the operator chooses another count.
Reject more than five as noise and recommend five or fewer. Do not silently
change `N`.

If the operator is not available, do not invent a decision or start generation.
Return the unanswered question and the recommended answer. A prototype starts
only after the operator confirms the brief.

## 2. Dispatch distinct directions in parallel

After confirmation, dispatch exactly `N` parallel native `designer` lanes in one
batch through `skill://dispatch`. A lane never redispatches. Give every lane
the same confirmed brief and one different lead lens. Keep lane work in
separate scratch directories. Do not let one lane read another lane's result.

Use real available skills for the lead lens. Choose lenses that change
structure, hierarchy, or interaction, not only colors. Suitable examples are:

| Lane | Lead lens | Required disagreement |
| --- | --- | --- |
| A | workflow and information hierarchy | Put the primary task first and make progress obvious. |
| B | product identity and narrative | Use a strong identity device and a different page rhythm. |
| C | dense operations and spatial scanning | Optimize for repeated work, comparison, and keyboard reach. |
| D | baseline accessibility and low cognitive load | Reduce choice cost and make states legible without color. |
| E | deliberate radical alternative | Reject the default card grid and choose a different composition. |

For each lane, name the lead skill in the brief. Examples include
`skill://baseline-ui`, `skill://quality` with the `design` domain,
`skill://improve-ui`, or a host-approved design skill. Do not route a lane back through `/prototype`.
Each lane must make a structural choice. Count two lanes as one direction when
they share the same layout and differ only in paint or copy; ask for a redo.

Each lane returns one direction packet with all fields below:

```text
Direction ID and title
One-sentence thesis
Lead lens and skill read
Host route or standalone-route reason
Information hierarchy and primary interaction
Layout and responsive behavior
Token and accessibility notes
Self-contained preview HTML or a screenshot with its source
Render evidence at desktop and mobile when the host can render both
Tradeoffs: gains, costs, risks, and rejected defaults
Assumptions and unresolved questions
One-command run instruction
```

The lane must keep prototype code minimal. It must not edit production files,
claim a direction is selected, or hide a state needed for comparison. The chief
checks every packet for the required fields, runnable evidence, and structural
distinctness before catalog synthesis.

## 3. Synthesize one self-contained HTML catalog

The chief synthesizes the accepted packets. Do not ask a lane to choose the
winner. Create exactly one catalog file at a stable scratch path, for example:

```text
<scratch>/prototypes/<surface-slug>/catalog.html
```

The catalog is self-contained:

- Put all catalog CSS and JavaScript in the file.
- Inline direction markup and styles, or embed each preview in an `iframe`
  using `srcdoc`.
- Prefer a live preview. If a live preview cannot run, embed the screenshot as
  a data URL. Do not link to a dev server, remote image, CDN, font, or external
  stylesheet.
- Use fixture data. Do not connect previews to real mutations or credentials.
- Keep each direction in one semantic `<section>` with a unique heading.

Every direction section must contain:

1. The direction ID, name, and one-sentence thesis.
2. A live preview or an embedded screenshot for that direction.
3. The lead lens and the layout or interaction decision.
4. A **Tradeoffs** block with gains, costs, risks, and rejected defaults.
5. A **Notes** field for operator feedback.
6. A **Lock this direction** control.

The catalog must also contain:

- a brief and the fixed constraints above the directions;
- a comparison summary that names the structural difference between directions;
- keyboard-accessible section navigation;
- a visible selected or locked state;
- a single lock record that names one direction, the rationale, retained
  constraints, and rejected directions;
- a visible way to clear an accidental lock before confirmation.

Use inline browser behavior so the operator can browse without a build step:

- Previous and next controls move between sections.
- A direction control updates the URL hash, so a section is shareable.
- Notes persist in `localStorage` under a surface-specific key.
- Selecting **Lock this direction** marks the candidate and shows the lock
  record. It does not silently change production code.
- A **Clear lock** control removes the candidate lock.
- The chief records the operator's explicit confirmation after the browse
  session. A browser click alone is not an inferred product decision.

A minimal catalog shape is:

```html
<main>
  <header id="brief">...</header>
  <nav aria-label="Direction navigation">...</nav>
  <section id="direction-a" aria-labelledby="direction-a-title">
    <h2 id="direction-a-title">A — Workflow first</h2>
    <p class="thesis">...</p>
    <div class="preview" aria-label="Direction A preview">...</div>
    <details><summary>Tradeoffs</summary>...</details>
    <label>Notes<textarea data-notes="a"></textarea></label>
    <button data-lock="a">Lock this direction</button>
  </section>
  <!-- one equivalent section for each accepted direction -->
  <aside id="lock-record" aria-live="polite">No direction locked.</aside>
</main>
```

Do not substitute a gallery of names or text cards for previews. The operator
must judge rendered pixels. Do not call a reskin a distinct direction.

## 4. Browse and iterate until one direction is locked

Serve or open the catalog with the documented one-command instruction. Inspect
all directions in the browser. Compare pixels, states, density, task flow, and
tradeoffs. Do not choose by title, lane order, or model confidence.

The operator may request another pass. For each pass:

1. Preserve the confirmed brief and all useful notes.
2. State which direction or disagreement needs revision.
3. Dispatch only the required independent lane or lanes.
4. Replace the affected sections in the same catalog.
5. Re-render the changed previews and keep the comparison visible.

Keep iterating until the operator explicitly locks one direction. Record this
lock outside the browser state in the implementation issue or a scratch
`LOCK.md` beside the catalog:

```markdown
# Prototype lock

- Question:
- Selected direction:
- Why it wins:
- Constraints retained:
- Directions rejected and why:
- Open implementation risks:
- Catalog source:
```

The lock is a decision, not a production merge. If no direction meets the
brief, keep the work unlocked and ask which constraint or question must change.

## 5. Promote the locked direction

After the lock, rewrite the winner as production code. Do not promote
prototype-only code by copy-paste when it lacks production error handling,
semantics, or tests required by the host. Keep the catalog and losing directions
on a throwaway branch or scratch artifact, with a context pointer from the
implementation issue. Keep only the validated decision in the main branch.

Render the real production surface after implementation. Inspect desktop and
mobile screenshots. Run the applicable design, accessibility, token, keyboard,
and reduced-motion gates. Report named evidence. The catalog is exploration
evidence, not proof that the production implementation passes.

## Handoff

Return:

- the confirmed brief and question;
- the catalog path and one-command preview command;
- the direction IDs and their structural differences;
- the operator's lock record;
- the production entrypoint rendered after promotion;
- remaining risks or unanswered decisions.

Never claim a direction is locked without the operator's explicit decision and
a recorded lock.
