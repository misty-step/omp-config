# Primitive Routing Table

Route by outcome.
The chief executive must not load specialist workflows to do the work itself.
Give each skill to the lane that owns its outcome.


## Declared and bundled roles

| Work shape | Primary role | Specialist skills | Verification |
|---|---|---|---|
| systems architecture and decomposition | `daedalus` | `project-engineering` when the repository fitness contract matters | chief review; `solomon` for a contested choice |
| accepted implementation | `builder` | `deliver`, `ci`; add domain skills named below | `qa`; add `reviewer` for high-risk changes |
| remediate a ranked findings packet | `fixer` | `refactor`, `ci`, `review-tests` | `qa`; two-round cap, then report what remains |
| full-board or full-backlog grooming | `curator` | `groom`, `research`, `vision`, ledger skill | operator approves destructive backlog changes |
| broad research and repository sweep | `magellan` | `research`; add `peer-harnesses` for model or harness facts | `scout` source spot-check when risk is medium or higher |
| code-review program | `reviewer` | `code-review` for the gate-owned freeze/packet/submission/receipt protocol; `peer-harnesses` only for optional critics | its own bench: cross-family `code-critic` lanes plus `qa` for live claims |
| one static critique lane | `code-critic` | exactly one injected review lens; carries no standing doctrine | another model family if its finding decides release |
| live verification | `qa` | `verify-live`, `ci`; add surface-specific skills | a different model family from the author |
| persona-driven QA user coordination | `qa-user` | `qa-users`, `dispatch` | OMP root first explores repository/product docs, rules, scripts, and live local/dev/staging browser entrypoints; then the no-read coordinator dispatches browser-only `qa-user-leaf` instances; root owns validation, triage, suppression, RCA, deduplication, and serialized tracker or PR writes |
| production incident or digital forensics | `cassandra` | `factory-apps`, `estate-infrastructure` | replay the original failure and watch the live signal |
| contested decision | `solomon` | add `council` only through an ad-hoc lane that can execute it | reversal condition and cheapest experiment |
| visual product design | bundled `designer` | `design`, `image-gen`; add UI skills below | Gemini 3.6 Flash rendered pass plus `qa` for behavior |
| bounded read-only lookup | bundled `scout` | task-named hidden skill only | parent checks the cited source |
| external library or API source research | bundled `librarian` | `research`; add vendor documentation MCP | parent checks the primary source |
| mechanical inventory or collection | bundled `sonic` | none unless the task names one | parent checks count or set difference |

Use an ad-hoc task lane when no declared role fits.
Name its hidden skills in the brief.
Do not create a permanent agent for one unusual task.


## Agent tool envelopes

An agent that omits `tools` receives OMP's full built-in tool catalog.
Restricted agents must declare an explicit comma-separated list.
Validate every explicit tool name against OMP's existing built-in tool authority.
`*` is not a supported representation.


## Skill routes

| Outcome | Skills to load | Role or composition |
|---|---|---|
| build one accepted ticket | `deliver` (loads `deliver-core`); add `refactor` only for an explicit architecture refactor | `builder` |
| run or strengthen gates | `ci`, `project-engineering` | `builder` authoring; `qa` verification |
| audit, assess, and remediate lint, build, typecheck, and hook gates | `quality-toolchain`; the program composes `ci` and `project-engineering` lanes | one owning lane runs the program: `scout`/`sonic` inventory, ad-hoc audit lanes, `builder` or `fixer` remediation, fresh `qa` verification |
| audit, assess, and remediate the automated test system | `quality-tests`; the program composes `review-tests` and `ci` lanes | one owning lane runs the program: `scout`/`sonic` inventory, ad-hoc audit lanes, `builder` or `fixer` remediation, fresh `qa` verification |
| review a meaningful change | `code-review` for `freeze -> prepare -> submit -> record -> verify`; `autoreview`, `thermo-nuclear-review`, and `thermo-nuclear-code-quality-review` are ordinary skills loaded explicitly by the caller; add `peer-harnesses` only for optional extra critics | `reviewer` |
| capture a durable solved pattern | `compound` | the implementing lane after verification |
| groom, prioritize, rethink, or find ambitious work | `groom`, `vision`, `research` | `curator`; never use a one-ticket shape workflow |
| settle project identity or long-term direction | `vision`, `research` | `curator` with `solomon` for a contested decision |
| shape or refresh a human project roadmap | `roadmap`, `simplified-technical-english`; add `vision` when direction changes | `curator` for decisions; `builder` for artifact edits; `qa` for browser proof |
| produce interface alternatives | `design`, `image-gen` | bundled `designer`; use `daedalus` first when architecture is unsettled |
| improve an existing interface, fix accessibility, or improve motion performance | `improve-ui`, `baseline-ui` | bundled `designer` for review; `builder` for fixes; `qa` for accessibility and motion behavior |
| run a whole-product design audit-assess-remediate program against a project DESIGN.md | `design-audit` | chief owns the program; scout discovery, designer audit lanes, builder remediation, qa browser verification |
| produce a rendered report | none — bare lane with a browser render loop | ad-hoc authoring lane; verify in a browser |
| create public proof and launch material | `showcase` | `builder` plus `designer` and `qa` |
| create or repair documentation | `document` | `magellan` sources; `builder` writes; `code-critic` checks claims |
| edit operator prose to STE | `simplified-technical-english` | the lane that owns the prose |
| research external facts | `research` (loads `research-core`) | chief for decision support; `magellan` for broad work; `librarian` for APIs |
| restore ambition after unsupported scope retreat | `capability-confidence` | the lane that is reducing the requested outcome without blocker evidence |
| get independent model views | `council` | one consult lane; `solomon` rules on the evidence |
| engineer harness primitives | `harness-engineering` | Read `global/references/skill-authoring-standard.md` for skill-authoring rules; `builder`; `reviewer` review; `qa` live probe |
| evaluate a skill | `skill-eval`, `eval-design` | ad-hoc eval lane; use Crucible; blind grader from another family |
| design an MCP surface | `mcp-design`, `harness-engineering` | `daedalus` architecture; `builder` implementation; `qa` replay |
| operate Misty Step apps | `factory-apps`; then the named app skill and its CLI/API | `cassandra` for incidents; `builder` for planned changes |
| operate Estate infrastructure | `estate-infrastructure` | `cassandra` for incidents; `builder` for approved changes |
| call a credentialed vendor API | Mint broker | the specialist lane that owns the call; never expose credential bytes |
| manage Powder work | `powder` | the lane that owns the card; `curator` for board-wide work |
| prepare remote public sandboxes | `sprites` | `builder` with a clean checkpoint |
| judge whether tests defend the change | `review-tests` | `code-critic` with the lens injected; `fixer` inherits its fix-vs-weaken rule |
| find security defects in a diff | `review-security` | `code-critic` with the lens injected; escalate credential findings immediately |
| judge a change against stated product intent | `review-vision` | `code-critic` with the lens injected; requires a written authority |
| verify live behavior end to end | `verify-live` | `qa`; cheapest browser tier first, CLI escalation only when needed |
| coordinate persona-driven application QA | `qa-users` | OMP root discovery and frozen input, then `qa-user` coordinator with browser-only `qa-user-leaf`; root owns validation, triage, suppression, RCA, and serialized tracker query/create/read-back plus deduplicated PR or work-ledger writes |
| audit, assess, and remediate operational quality with trend evidence | `quality-operations`; audit lanes add `verify-live`, `ci`, `factory-apps` per domain | lead lane owns the loop; `scout` inventory; `qa` audit probes; `fixer` remediation; independent `qa` verification |
| audit, assess, and remediate system architecture statically | `audit-architecture`; critic lanes inject the `review-tests` lens | chief runs the loop; `magellan`/`scout` discovery; `daedalus` target state at XL; `code-critic` lens audit; `fixer` or `builder` remediation; `qa` plus a fresh `code-critic` verify |
| audit, assess, and remediate live product correctness | `audit-product`; deterministic lanes load `verify-live`; persona track follows `qa-users` | chief discovery and frozen input; `qa` scenario verdicts; existing `qa-user` coordinator with browser-only `qa-user-leaf` personas; `builder` or `fixer` remediation; fresh `qa` re-verification |

## MCP and tool routes

Disabled-server policy and CLI replacements are recorded in
`mcp-pruning.md`.
A disabled MCP name is never a route.


| Need | Primitive |
|---|---|
| repository code intelligence | LSP before text search for symbols |
| bounded repository search | `scout`, `grep`, `glob`, `read` |
| current external facts | `web_search`; use `librarian` for API and library source |
| broad local knowledge search | `grep`, `glob`, `read`, or the local search CLI |
| browser behavior or visual proof | builtin `browser` first, then the `agent-browser` CLI, then the `chrome-devtools` CLI for scored audits/traces/heap work; the Chrome DevTools MCP stays disabled |
| Powder work ledger | `powder` CLI/API through the `powder` skill; claim one card before mutation. Powder MCP stays disabled. |
| R90 work ledger | Habitat MCP only; never Powder |
| production health and incidents | Canary CLI/API through `factory-apps`; the Canary MCP stays disabled |
| vendor credentials | Mint-brokered call; no local secret bytes |
| GitHub repository operations | GitHub device tool; use repository URLs as evidence |
| model or harness second opinion | `peer-harnesses` or `council` according to the required surface |

Mint calls use
`http://mint.tail5f5eb4.ts.net:4949/proxy/https/<host>/<path>` with a
value-free `__mint.<service>.<name>__` placeholder. Tailnet WhoIs identifies
the caller. Mint policy is the grant and owns `Authorization` at the upstream
boundary.

## Risk and team width

- Low-risk S work uses one lane and no verifier.
- Medium-risk M+ work uses one author and one independent verifier.
- High-risk work always uses an independent verifier.
  High-risk implementation also uses `reviewer` before integration.
- Unknown estimate or risk uses the medium-risk floor.
- XL architecture, implementation, or design starts with `daedalus`.
  Then fan out by independent dependency or surface.
- Never pad a team.
  One lane per real independent constraint is sufficient.


## Hidden-skill mechanics

`disable-model-invocation: true` removes a skill description from the model's
visible catalog.
It does not remove the skill from the session.
A declared agent's `autoloadSkills` bundle preloads its recurring specialist guidance.
For an ad-hoc lane, write `Read skill://<name> first` in the brief.
True per-agent catalogs require the composer extension.

Do not use `skills.includeSkills` to implement the chief boundary.
That filter removes skills globally before child sessions and prevents the desired bundles.
