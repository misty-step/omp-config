# Skill authoring standard (roster house conventions)

The judgment layer lives in the vendored
`primitives/skills/.external/mattpocock-writing-great-skills/SKILL.md`
(predictability, invocation choice, the six failure modes, information hierarchy,
leading words, positive framing, and the no-op test) and Anthropic's
progressive-disclosure guidance
(`docs/research/roster-926-import-design-brief.md`). This file resolves their
frontier-model tension and adds only the house conventions they leave open.
Apply the no-op test to every line — including lines from this standard.

## Frontmatter

- `name`, `description`, `argument-hint` — all three, always.
- Model-invoked skills: description is the trigger. Give each distinct branch
  one recognizable phrase; start with a compact leading word repeated in the
  body. Cut identity and procedure already available after invocation.
- Hand-only skills: `disable-model-invocation: true`; description becomes a
  one-line human-facing summary with no autonomous trigger language.
- `argument-hint` uses bracketed-token form: `"[--foo|--bar] [target]"`.

## Body shape

- H1 is the trigger form: `# /<name>`.
- Three tiers: frontmatter → SKILL.md body → `references/` on demand.
  A body pushing past ~900 words is a signal to extract, not a violation —
  the test is whether the inline prose is load-bearing for every invocation.
- Fenced examples must not contain lines that scan as real headings
  (indent them or use placeholder text).

## Canonical section names

- `## Completion Gate` — the single wrap-up header. It points to the Shared
  Operating Spine (`Prove`; `Durable State and Closeout`) first, then adds only
  phase-specific fields. Retire: Output, Verdict, Completion, Done means,
  Verification-as-wrap-up.
- `## Gotchas` — bespoke traps only. If a frontier model already knows it,
  it fails the no-op test.

## Shared doctrine: point, never restate

One-line pointers instead of local rewordings:

- Critics: `Critics get the artifact and the oracle only — never the author's
  reasoning trail (Shared Operating Spine: Prove).`
- Delegation: `Delegate per the Shared Operating Spine (Act).`
- Compression: `julius-caveman for interim synthesis only; findings, code,
  commits, and final artifacts stay normal English.`
- Vision: `Read root VISION.md when present; if missing or stale, route to
  /vision.`
- Verification loops: point at
  `primitives/shared/references/verification-system-first.md` — do not
  re-derive it.
- Simplicity: the delete-first/Ponytail load trigger lives inside
  `primitives/shared/references/delete-first.md`; skills just point there.

A skill that needs a *different* rule than the shared line says is making a
claim — state the delta explicitly and say why, next to the pointer.

## Routing tables

One signal→skill routing table exists, in `/orient`. `/next` and any other
skill that routes consumes it by pointer and adds only its own framing.
Never fork the table.

## Frontier-model resolution

WGS asks for ordered steps with completion criteria; current frontier-model
guidance warns that procedural checklists over-constrain capable models. Roster
targets frontier orchestrators by default, so encode the invariant process,
boundaries, oracle, and stop condition—not a narrated SDLC. Ordered steps earn
their place only when tool order is semantically required or `/skill-eval`
shows that the target model fails without them.

Additional Fable 5 deltas (2026-07):

- Deletion is the top rewrite move. Strip prior-model coaching before adding.
- Never ask the model to expose or transcribe internal reasoning.
- Over-firing skills need a `Do not use when:` boundary beside `Use when:`.
- A reference pointer states the condition and intended use; weak “see also”
  pointers are variance bugs.
- Pair every prohibition with the target behavior. A bare negation makes the
  forbidden path more salient.
- Completion-reporting skills point to the Shared Operating Spine rather than
  repeating universal evidence prose.
