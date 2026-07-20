---
name: subagent-dispatch-routing
description: |
  Capability matrix for the OMP model palette (Fable 5, Sol, Luna, Sonnet 5,
  Kimi K3, Grok 4.5, GLM 5.2, Gemini 3.5 Flash) and a deterministic procedure
  mapping a work item's estimate x risk x work-shape to a subagent composition
  manifest. Use when: 'compose a subagent', 'which model should I use', 'what
  effort should this run at', 'does this lane need a verifier', 'dispatch
  routing', '/dispatch-routing', composing a team for a Powder card, or
  choosing model:effort before spawning a lane.
---

# /dispatch-routing

Two separate questions get conflated constantly. Keep them apart:

- **Capability routing** — which model fits this lane's cognitive shape. Decided
  once, deliberately, from the matrix and procedure below.
- **Fallback chains** — `config.yml`'s `retry.fallbackChains`, fired only when a
  call to the *chosen* model errors or times out. Pure resilience: never a
  second opinion, never a capability upgrade, never something you pick for.

Never read a fallback chain as a ranked capability list. `anthropic/claude-sonnet-5`
falls back to `openai-codex/gpt-5.6-luna:high` on error — that says nothing about
which one is the better *choice* for a given lane.

## Palette matrix

Grounded in `~/.omp/agent/AGENTS.md` (Model palette) and `config.yml`
(`modelRoles`, `retry.fallbackChains`). Effort ceiling is the highest tier either
file attests for that model.

| Model | Provider route | Effort tiers seen | Ceiling | Strengths (AGENTS.md) |
|---|---|---|---|---|
| Claude Fable 5 | `anthropic` | medium, high, xhigh | xhigh | Chief execution, ambiguous synthesis, integration, high-consequence judgment |
| GPT-5.6 Sol | `openai-codex` | high, xhigh, max | max | Architecture, decomposition, formal reasoning, hard cross-system debugging |
| GPT-5.6 Luna | `openai-codex` | high, xhigh, max | max | Focused implementation, refactoring, repo mechanics, long autonomous coding lanes |
| Claude Sonnet 5 | `anthropic` | high, xhigh | xhigh | Tool-heavy execution, careful verification, reliable generalist work |
| Kimi K3 | `kimi-code` (native OAuth) | high | high | Long-context research, broad synthesis |
| Grok 4.5 | `xai-oauth` | high | high | Adversarial review, assumption-breaking, strategy, independent challenge |
| GLM 5.2 | `openrouter/z-ai` (via Mint) | high | high | Design exploration, implementation alternatives, visual/product work without an agent-readable Z.AI key |
| Gemini 3.5 Flash | `google-antigravity` | auto/default, high | high | Multimodal inspection, broad fast analysis, vision fallback |

`kimi-code` keeps native OAuth; GLM has no agent-readable key and routes through
OpenRouter via Mint instead. Reserve `cursor` for Composer 2.5 — never a generic
router for these eight.

## Native role bindings

The procedure below dispatches through these declared `global/agents/*.md`
roles wherever one fits — reuse them; do not re-derive a model choice a role
already declares. `model:` lists primary then per-agent fallback (resilience,
not a ranked alternative).

| Role | model: (primary, fallback) | thinkingLevel | spawns | autoloadSkills |
|---|---|---|---|---|
| `hephaestus` | Luna xhigh, Sonnet 5 high | xhigh | scout, cerberus, scully | orient, deliver, qa, ci, diagnose |
| `daedalus` | Sol high, Fable high, GLM 5.2 high | high | — | orient, shape, design, oracle, project-engineering, council |
| `magellan` | Kimi K3 high, Luna xhigh, Sonnet 5 high | high | — | orient, research, diagnose |
| `cerberus` | Grok 4.5 high, Sol high | high | — | orient, code-review, ci, diagnose |
| `scully` | Sonnet 5 high, Luna high | high | — | orient, qa, ci, diagnose |
| `solomon` | Fable high, Sol high | high | — | orient, council |
| `cassandra` | Luna xhigh, Sonnet 5 high | xhigh | scout | orient, diagnose, qa |

Bundled agents (`scout`, `designer`, `librarian`, `sonic`, `task`) carry no
`global/agents/*.md` file — no per-repo model override exists for `scout`,
`librarian`, or `sonic`; use the harness's built-in default rather than forcing
a model string for them. `designer` and `task` do have a `config.yml`
`modelRoles` override: `designer: kimi-code/k3:high`, `task: anthropic/claude-sonnet-5:xhigh`.

## Procedure

Input: a work item's `estimate` (S/M/L/XL), `risk` (low/medium/high, may be
absent), and `work-shape` (implementation, research, review, verification,
design, mechanical). Powder cards carry `estimate` and `risk` as literal
fields (`query_work_items`/`get_card`/`list_ready`); `work-shape` is not a
Powder field — classify it yourself from the card's title, body, and labels
against the six shapes below before entering the table. A card predating the
`risk` field, or with `risk` unset, is risk-missing — go to Step 4, not Step 3.

### Step 1 — base role by work-shape and estimate

| Work-shape | S | M / L | XL |
|---|---|---|---|
| implementation | `hephaestus` | `hephaestus` | `daedalus` decomposes first (Step 5), then fan out `hephaestus` per slice |
| research | `scout` (bounded lookup) | `magellan` (broad synthesis) | `magellan`, one lane per independent question |
| review | `cerberus` | `cerberus` | `cerberus`, one lane per independently reviewable slice |
| verification | `scully` | `scully` | `scully`, one lane per independently verifiable slice |
| design | `designer` (bundled) | `designer` (bundled) | `daedalus` scopes the surfaces first, then `designer` per surface |
| mechanical | `sonic` (bundled) | `sonic` (bundled) — reconsider the estimate | flag for re-shape: mechanical work this size is a signal mismatch, not a lane |

This step fixes the *role*. Steps 2-4 tune model:effort and the verifier lane
within that role; they never swap the role work-shape already chose.

### Step 2 — pin model:effort

Use the role's declared primary from **Native role bindings**. Exceptions:

- `mechanical` at S/low: pin `smol` (`openai-codex/gpt-5.6-luna:xhigh`,
  `config.yml` `modelRoles.smol`) on the `sonic` lane — sized for bounded,
  low-consequence collection.
- `design`: `designer` primary is `kimi-code/k3:high`
  (`config.yml` `modelRoles.designer`). Add a second lane pinned to
  `openrouter/z-ai/glm-5.2:high` when the operator wants a second design
  opinion or `designer`'s tool envelope does not fit — GLM 5.2 is the palette's
  named alternative for design exploration.
- `verification` or `review` touching rendered UI: add a
  `google-antigravity/gemini-3.5-flash` vision pass (`config.yml`
  `modelRoles.vision`) alongside the base lane.

### Step 3 — risk sets the verifier lane (known risk)

| Risk | Verifier lane | Effort |
|---|---|---|
| low | off | role's declared primary |
| medium | on only if estimate is M or larger | role's declared primary |
| high | always on | escalate every lane's model to its ceiling (**Palette matrix**); `implementation` also gets a `cerberus` adversarial pass before integration |

Verifier lane meaning by work-shape: `implementation`/`design` -> `scully`
(or the vision pass above for UI). `review`/`verification` -> a second,
independently-modeled lane (never the same model checking itself) —
`cassandra` instead of `scully` if `verification` turns out to mean a live
production incident. `research`/`mechanical` -> a `scout` spot-check of the
output.

### Step 4 — unknown or missing risk (or estimate)

Conservative default, not a guess: treat the missing axis as clearing the
M-or-larger / medium-or-higher bar in Step 3 — verifier lane is always on.
Additionally, pin the chosen role to its own declared **fallback** model at
`high`, not its primary — every native role above except `daedalus` and
`solomon` already lists `anthropic/claude-sonnet-5:high` in its `model:`
field; use that slot explicitly. For `daedalus`/`solomon` (no Sonnet 5 in
their declared list), override explicitly to
`anthropic/claude-sonnet-5:high` on top of the role. Do not persist this
substitution as if it were the real signal — re-route through Step 1-3 the
moment `estimate`/`risk` are known.

### Step 5 — XL decomposition (implementation, design)

`daedalus` maps the dependency graph or surface list first, at depth 0.
Fan out per-slice lanes at depth 1, capped at `config.yml` `task.maxConcurrency`
(12) concurrent lanes. A per-slice lane's own permitted spawns (e.g.
`hephaestus` spawning `scully`) land at depth 2 — `config.yml`
`task.maxRecursionDepth` is 2, so no lane below that may spawn a further layer.

## Manifest output

The procedure's output is always these six fields, in this order:

1. **role/agent** — from Step 1.
2. **model:effort** — from Step 2/3/4.
3. **skills to load** — the role's `autoloadSkills` (**Native role bindings**),
   plus any skill the card itself names.
4. **MCPs** — the repo's ledger MCP per the Work ledger rule in
   `~/.omp/agent/AGENTS.md` (Powder by default, Habitat for Adminifi/r90),
   plus shape-specific servers only when the lane needs them: `chrome-devtools`
   for UI/browser work, `qmd`/`parallel-search` for research, `canary` for a
   production-incident `verification` lane.
5. **verifier lane** — yes/no, from Step 3 or 4.
6. **budget guidance** — from **Budget guidance** below.

## Budget guidance

Grounded in `config.yml` `task`: `maxConcurrency: 12`, `maxRuntimeMs: 2700000`
(45 min), `maxRecursionDepth: 2`.

| Estimate | Lanes | Per-lane runtime | Recursion depth |
|---|---|---|---|
| S | 1, no fan-out | well under 45 min | 0-1 |
| M | 1 (the role's own permitted spawns still apply) | up to 45 min | <=1 |
| L | 1 extended lane, or 2-4 if the card decomposes cleanly | up to 45 min each | <=2 |
| XL | `daedalus` + up to 12 per-slice lanes (Step 5) | up to 45 min each | <=2, strictly |

## Worked fixtures

### S / low / mechanical

- role/agent: `sonic` (bundled)
- model:effort: `openai-codex/gpt-5.6-luna:xhigh` (`smol` role override)
- skills: none declared for `sonic`; card-named skills only
- MCPs: the repo's ledger MCP only
- verifier lane: no
- budget: 1 lane, well under 45 min, no fan-out

### M / medium / implementation

- role/agent: `hephaestus`
- model:effort: `openai-codex/gpt-5.6-luna:xhigh` (declared primary)
- skills: orient, deliver, qa, ci, diagnose
- MCPs: ledger MCP; add `chrome-devtools` if the change touches UI
- verifier lane: yes — estimate M meets the M-or-larger bar at risk medium;
  `hephaestus` spawns `scully` itself
- budget: 1 lane, up to 45 min, depth <=1

### XL / high / implementation

- Step 5 first: `daedalus` (`openai-codex/gpt-5.6-sol:max` — risk high
  escalates to ceiling) maps the dependency graph, depth 0
- Then per-slice: `hephaestus` at `openai-codex/gpt-5.6-luna:xhigh` (already
  at ceiling), depth 1, fanned out up to 12 concurrent lanes
- verifier lane: yes, mandatory — each slice gets a `scully` verification pass
  plus a `cerberus` adversarial review before integration, depth 2
- MCPs: ledger MCP per lane; `chrome-devtools` per lane that touches UI
- budget: multi-lane manifest, each lane <=45 min, total lanes <=12, depth
  strictly <=2

### L / high / design

- role/agent: `designer` (bundled), primary lane
- model:effort: `kimi-code/k3:high` (`designer` role); second lane pinned to
  `openrouter/z-ai/glm-5.2:high` for an independent design alternative
- verifier lane: yes (risk high) — add a `google-antigravity/gemini-3.5-flash`
  vision pass (`modelRoles.vision`) over the rendered result
- skills: card-named design skills; `harness-engineering` not implied
- budget: 2 parallel lanes (designer + GLM alternative), 1 verification pass
  after both land, depth <=1

### estimate missing / risk missing / implementation

- role/agent: `hephaestus` — work-shape still picks the role
- model:effort: `anthropic/claude-sonnet-5:high` — `hephaestus`'s own declared
  fallback slot, pinned explicitly instead of its Luna xhigh primary (Step 4)
- skills: orient, deliver, qa, ci, diagnose (unchanged)
- verifier lane: yes, forced on by Step 4 — `hephaestus` spawns `scully`
- budget: treat as at least M for sizing; do not undersize unknown-signal work
- once real `estimate`/`risk` land on the card, re-route through Steps 1-3 and
  drop this substitution

## Gotchas

- **Fallback chain is not a menu.** `retry.fallbackChains` fires only on error;
  it never justifies picking a model because it is "next on the list".
- **`mechanical` at L/XL is a mis-sized card, not a lane.** Route it back to
  `/shape` or `/groom` instead of forcing a fan-out sonic can't use.
- **A verifier is never the same model checking its own work.** `review` and
  `verification` work-shapes need a genuinely different model in the second
  lane, not a re-run.
- **Unknown risk is a floor, not a ceiling.** Step 4 only ever adds a verifier
  and pins a more conservative model; it never removes a verifier a known
  high-risk signal would have required.
- **This skill owns the matrix; Powder and Roster do not.** Powder cards carry
  only the signal (`estimate`, `risk`); Roster resolves and launches without
  choosing a model. Do not copy this decision table into either.
- **`designer`/`task` have a `config.yml` override; `scout`/`librarian`/`sonic`
  do not.** Do not invent a model string for the latter three — using the
  harness's built-in default is the correct, deterministic answer.

