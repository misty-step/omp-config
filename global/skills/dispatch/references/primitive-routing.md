# Primitive Routing Table

Route by outcome. The chief executive must not load specialist workflows to do
the work itself. Give the skill to the lane that owns the outcome.

## Declared and bundled roles

| Work shape | Primary role | Specialist skills | Verification |
|---|---|---|---|
| systems architecture and decomposition | `daedalus` | `project-engineering` when the repository fitness contract matters | chief review; `solomon` for a contested choice |
| accepted implementation | `builder` | `deliver`, `ci`; add domain skills named below | `qa`; add `reviewer` for high-risk changes |
| remediate a ranked findings packet | `fixer` | `refactor`, `ci`, `review-tests` | `qa`; two-round cap, then report what remains |
| full-board or full-backlog grooming | `curator` | `groom`, `research`, `vision`, `grilling`, ledger skill | operator approves destructive backlog changes |
| broad research and repository sweep | `magellan` | `research`; add `peer-harnesses` for model or harness facts | `scout` source spot-check when risk is medium or higher |
| code-review program | `reviewer` | `code-review`, `peer-harnesses`, `dispatch` | its own bench: cross-family `code-critic` lanes plus `qa` for live claims |
| one static critique lane | `code-critic` | exactly one injected review lens; carries no standing doctrine | another model family if its finding decides release |
| live verification | `qa` | `verify-live`, `ci`; add surface-specific skills | a different model family from the author |
| production incident or digital forensics | `cassandra` | `factory-apps`, `estate-infrastructure`, `mint` | replay the original failure and watch the live signal |
| contested decision | `solomon` | add `council` only through an ad-hoc lane that can execute it | reversal condition and cheapest experiment |
| visual product design | bundled `designer` | `design`, `image-gen`; add UI skills below | Gemini 3.6 Flash rendered pass plus `qa` for behavior |
| bounded read-only lookup | bundled `scout` | task-named hidden skill only | parent checks the cited source |
| external library or API source research | bundled `librarian` | `research`; add vendor documentation MCP | parent checks the primary source |
| mechanical inventory or collection | bundled `sonic` | none unless the task names one | parent checks count or set difference |

Use an ad-hoc task lane when no declared role fits. Name its hidden skills in
the brief. Do not create a permanent agent for one unusual task.

## Agent tool envelopes

An agent that omits `tools` receives OMP's full built-in tool catalog. Restricted agents must declare an explicit comma-separated list. Every explicit tool name is validated against OMP's existing built-in tool authority; `*` is not a supported representation.

## Skill routes

| Outcome | Skills to load | Role or composition |
|---|---|---|
| build one accepted ticket | `deliver`; add `refactor` only for an explicit architecture refactor | `builder` |
| run or strengthen gates | `ci`, `project-engineering` | `builder` authoring; `qa` verification |
| review a meaningful change | `code-review`, `peer-harnesses` | `reviewer`, which fans out `code-critic` lenses and Cursor Thermo-Nuclear lanes |
| capture a durable solved pattern | `compound` | the implementing lane after verification |
| groom, prioritize, rethink, or find ambitious work | `groom`, `vision`, `grilling`, `research` | `curator`; never use a one-ticket shape workflow |
| settle project identity or long-term direction | `vision`, `grilling`, `research` | `curator` with `solomon` for a contested decision |
| produce interface alternatives | `design`, `image-gen` | bundled `designer`; use `daedalus` first when architecture is unsettled |
| improve an existing interface without replacing its identity | `improve-ui`, `baseline-ui` | bundled `designer` for review; `builder` for implementation |
| accessibility or motion defects | `fixing-accessibility`, `fixing-motion-performance` | `builder` plus `qa`; add a vision pass |
| draft or input loss on remount in a Yew WASM app | `yew-draft-persistence` | `builder`; `qa` confirms the draft survives on the live surface |
| produce a rendered report | none — bare lane with a browser render loop | ad-hoc authoring lane; verify in a browser |
| create public proof and launch material | `showcase` | `builder` plus `designer` and `qa` |
| create or repair documentation | `document` | `magellan` sources; `builder` writes; `code-critic` checks claims |
| edit operator prose to STE | `simplified-technical-english` | the lane that owns the prose |
| research external facts | `research` | chief for decision support; `magellan` for broad work; `librarian` for APIs |
| get independent model views | `council` or `oracle` | ad-hoc tool-capable lane; `solomon` rules on the evidence |
| engineer harness primitives | `harness-engineering`, `writing-great-skills` | `builder`; `reviewer` review; `qa` live probe |
| evaluate a skill | `skill-eval`, `eval-design` | ad-hoc eval lane; use Crucible; blind grader from another family |
| design an MCP surface | `mcp-design`, `harness-engineering` | `daedalus` architecture; `builder` implementation; `qa` replay |
| scope an MCP server to one directory subtree | `r90-ledger-guard` | the lane changing OMP configuration; also audits the R90 Habitat and Powder split |
| operate Misty Step apps | `factory-apps`; then the named app skill or MCP | `cassandra` for incidents; `builder` for planned changes |
| operate Estate infrastructure | `estate-infrastructure` | `cassandra` for incidents; `builder` for approved changes |
| call a credentialed vendor API | `mint` | the specialist lane that owns the call; never expose credential bytes |
| manage Powder work | `powder` | the lane that owns the card; `curator` for board-wide work |
| manage operator tasks, reminders, and follow-ups | `todoist` | the lane that owns the request; Todoist holds life tasks, Powder holds work |
| prepare remote public sandboxes | `sprites` | `builder` with a clean checkpoint |
| post an Overmind milestone | `overmind-feed-post` | the lane that produced the milestone |
| operate a herdr fleet | `herdr-fleet-ops` | one ad-hoc operations lane |
| judge whether tests defend the change | `review-tests` | `code-critic` with the lens injected; `fixer` inherits its fix-vs-weaken rule |
| find security defects in a diff | `review-security` | `code-critic` with the lens injected; escalate credential findings immediately |
| judge a change against stated product intent | `review-vision` | `code-critic` with the lens injected; requires a written authority |
| verify live behavior end to end | `verify-live` | `qa`; cheapest browser tier first, CLI escalation only when needed |

## MCP and tool routes

| Need | Primitive |
|---|---|
| repository code intelligence | LSP before text search for symbols |
| bounded repository search | `scout`, `grep`, `glob`, `read` |
| current external facts | `web_search`; use `librarian` for API and library source |
| broad local knowledge search | QMD MCP |
| browser behavior or visual proof | builtin `browser` first, then the `agent-browser` CLI, then the `chrome-devtools` CLI; add Gemini vision. The Chrome DevTools MCP stays disabled |
| Powder work ledger | Powder MCP; claim one card before mutation |
| R90 work ledger | Habitat MCP only; never Powder |
| production health and incidents | Canary MCP through `factory-apps` |
| vendor credentials | Mint broker; no local secret bytes |
| GitHub repository operations | GitHub device tool; use repository URLs as evidence |
| model or harness second opinion | `peer-harnesses`, `council`, or `oracle` according to the required surface |
| durable operator feed update | Overmind tools; use `overmind-feed-post` when attribution requires stdio |

## Risk and team width

- Low-risk S work uses one lane and no verifier.
- Medium-risk M+ work uses one author and one independent verifier.
- High-risk work always uses an independent verifier. High-risk implementation
  also uses `reviewer` before integration.
- Unknown estimate or risk uses the medium-risk floor.
- XL architecture, implementation, or design starts with `daedalus`, then fans
  out by independent dependency or surface.
- Never pad a team. One lane per real independent bottleneck is sufficient.

## Hidden-skill mechanics

`disable-model-invocation: true` removes a skill description from the model's
visible catalog. It does not remove the skill from the session. A declared
agent's `autoloadSkills` bundle preloads its recurring specialist guidance.
For an ad-hoc lane, write `Read skill://<name> first` in the brief.

Do not use `skills.includeSkills` to implement the chief boundary. That filter
removes skills globally before child sessions and prevents the desired bundles.
True per-agent catalogs require the composer extension.
