# Primitive Routing Table

Route by outcome. The chief executive must not load specialist workflows to do
the work itself. Give the skill to the lane that owns the outcome.

## Declared and bundled roles

| Work shape | Primary role | Specialist skills | Verification |
|---|---|---|---|
| systems architecture and decomposition | `daedalus` | `project-engineering` when the repository fitness contract matters | chief review; `solomon` for a contested choice |
| accepted implementation | `hephaestus` | `deliver`, `ci`; add domain skills named below | `scully`; add `argus` for high-risk changes |
| full-board or full-backlog grooming | `curator` | `groom`, `research`, `vision`, `grilling`, ledger skill | operator approves destructive backlog changes |
| broad research and repository sweep | `magellan` | `research`; add `peer-harnesses` for model or harness facts | `scout` source spot-check when risk is medium or higher |
| code-review program | `argus` | `code-review`, `peer-harnesses`, `ci` | cross-family reviewers plus `scully` for live claims |
| one adversarial read-only review lane | `cerberus` | no workflow skill; its role prompt owns the review contract | another model family if its finding decides release |
| live verification | `scully` | `ci`; add surface-specific skills | a different model family from the author |
| production incident or digital forensics | `cassandra` | `factory-apps`, `estate-infrastructure`, `mint` | replay the original failure and watch the live signal |
| contested decision | `solomon` | add `council` only through an ad-hoc lane that can execute it | reversal condition and cheapest experiment |
| visual product design | bundled `designer` | `design`, `image-gen`; add UI skills below | Gemini 3.6 Flash rendered pass plus `scully` for behavior |
| bounded read-only lookup | bundled `scout` | task-named hidden skill only | parent checks the cited source |
| external library or API source research | bundled `librarian` | `research`; add vendor documentation MCP | parent checks the primary source |
| mechanical inventory or collection | bundled `sonic` | none unless the task names one | parent checks count or set difference |

Use an ad-hoc task lane when no declared role fits. Name its hidden skills in
the brief. Do not create a permanent agent for one unusual task.

## Skill routes

| Outcome | Skills to load | Role or composition |
|---|---|---|
| build one accepted ticket | `deliver`; add `refactor` only for an explicit architecture refactor | `hephaestus` |
| run or strengthen gates | `ci`, `project-engineering` | `hephaestus` authoring; `scully` verification |
| review a meaningful change | `code-review`, `peer-harnesses` | `argus`, which runs Cerberus and Cursor Thermo-Nuclear lanes |
| capture a durable solved pattern | `compound` | the implementing lane after verification |
| groom, prioritize, rethink, or find ambitious work | `groom`, `vision`, `grilling`, `research` | `curator`; never use a one-ticket shape workflow |
| settle project identity or long-term direction | `vision`, `grilling`, `research` | `curator` with `solomon` for a contested decision |
| produce interface alternatives | `design`, `image-gen` | bundled `designer`; use `daedalus` first when architecture is unsettled |
| improve an existing interface without replacing its identity | `improve-ui`, `baseline-ui` | bundled `designer` for review; `hephaestus` for implementation |
| accessibility or motion defects | `fixing-accessibility`, `fixing-motion-performance` | `hephaestus` plus `scully`; add a vision pass |
| produce a rendered report | none — bare lane with a browser render loop | ad-hoc authoring lane; verify in a browser |
| create public proof and launch material | `showcase` | `hephaestus` plus `designer` and `scully` |
| create or repair documentation | `document` | `magellan` sources; `hephaestus` writes; `cerberus` checks claims |
| edit operator prose to STE | `simplified-technical-english` | the lane that owns the prose |
| research external facts | `research` | chief for decision support; `magellan` for broad work; `librarian` for APIs |
| get independent model views | `council` or `oracle` | ad-hoc tool-capable lane; `solomon` rules on the evidence |
| engineer harness primitives | `harness-engineering`, `writing-great-skills` | `hephaestus`; `argus` review; `scully` live probe |
| evaluate a skill | `skill-eval`, `eval-design` | ad-hoc eval lane; use Crucible; blind grader from another family |
| design an MCP surface | `mcp-design`, `harness-engineering` | `daedalus` architecture; `hephaestus` implementation; `scully` replay |
| operate Misty Step apps | `factory-apps`; then the named app skill or MCP | `cassandra` for incidents; `hephaestus` for planned changes |
| operate Estate infrastructure | `estate-infrastructure` | `cassandra` for incidents; `hephaestus` for approved changes |
| call a credentialed vendor API | `mint` | the specialist lane that owns the call; never expose credential bytes |
| manage Powder work | `powder` | the lane that owns the card; `curator` for board-wide work |
| manage personal tasks | `todoist` | one ad-hoc bounded mutation lane |
| prepare remote public sandboxes | `sprites` | `hephaestus` with a clean checkpoint |
| post an Overmind milestone | `overmind-feed-post` | the lane that produced the milestone |
| operate a herdr fleet | `herdr-fleet-ops` | one ad-hoc operations lane |
| enforce the R90 ledger split | `r90-ledger-guard` | the R90 operations lane; Habitat only |
| fix Yew draft loss | `yew-draft-persistence` | `hephaestus`; `scully` verifies reload and entity switching |

## MCP and tool routes

| Need | Primitive |
|---|---|
| repository code intelligence | LSP before text search for symbols |
| bounded repository search | `scout`, `grep`, `glob`, `read` |
| current external facts | `web_search`; use `librarian` for API and library source |
| broad local knowledge search | QMD MCP |
| browser behavior or visual proof | Browser or Chrome DevTools MCP; add Gemini vision |
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
  also uses `argus` before integration.
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
