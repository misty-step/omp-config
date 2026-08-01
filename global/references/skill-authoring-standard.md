# Skill authoring standard (OMP house conventions)

Use this file as the only shared skill-authoring authority.
Make predictability the goal: keep the agent's process stable, not its output.
Use model invocation only when the agent or another skill must reach the skill.
Use `disable-model-invocation: true` for hand-only skills; use a router when hand-only skills multiply.
For each ordered step, define a checkable and exhaustive completion criterion.
If the criterion remains vague and the agent stops early, split later steps across a user or subagent hand-off.
Split skills only for a distinct invocation branch or to hide later steps that cause premature completion.
Keep each meaning in one source. Delete irrelevant, stale, duplicated, and no-op lines.
Use one compact leading word to anchor behavior; repeat it in the body, description, prompts, and code.
Move branch-only reference behind a condition-specific pointer; keep universal rules inline.
State the positive target. Pair every unavoidable prohibition with the required action.
Apply the no-op test to every line, including lines from this standard.

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
  Treat a body over ~900 words as a signal to extract content, not as a violation.
  Keep inline prose only when every invocation needs it.
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
  `global/references/verification-system-first.md` — do not
  re-derive it.
- Simplicity: the delete-first/Ponytail load trigger lives inside
  `global/references/delete-first.md`; skills just point there.

A skill that needs a *different* rule than the shared line says is making a
claim — state the delta explicitly and say why, next to the pointer.

## Routing tables

One signal→skill routing table exists in `/orient`.
`/next` and other routing skills consume it by pointer and add only their framing.
Never duplicate the table.

## Frontier-model resolution

Ordered steps expose completion criteria, but frontier guidance warns that checklists can over-constrain capable models.
OMP targets frontier orchestrators by default.
Encode the invariant process, boundaries, oracle, and stop condition, not a narrated SDLC.
Add ordered steps only when tool order is semantically required or `/skill-eval` shows the target model fails without them.

Additional Fable 5 deltas (2026-07):

- Deletion is the top rewrite move. Strip prior-model coaching before adding.
- Never ask the model to expose or transcribe internal reasoning.
- Over-firing skills need a `Do not use when:` boundary beside `Use when:`.
- A reference pointer states the condition and intended use. Weak “see also” pointers create variance bugs.
- Pair every prohibition with the target behavior. Bare negation makes the forbidden path more salient.
- Completion-reporting skills point to the Shared Operating Spine rather than
  repeating universal evidence prose.
