# Preferred Stack Defaults

Start here when you choose language, host, CI, observability, release,
design-system, storage, or agent-substrate defaults.
These are biases, not contracts.
Current pricing, runtime limits, client constraints, and live repo fit can
override them.
Name each override.

## Decision Rule

Default to owned, portable primitives when they sit close to the product's core
operating loop.
Buy or rent when the surface is undifferentiated, compliance-heavy,
standards-bound, or cheaper to rent than to maintain.

Before you commit to a provider, verify current facts with `/research`.
Check pricing, limits, deprecations, auth model, local deploy path, rollback
path, logs, and the smallest live smoke.
Provider facts rot quickly.

## Language And Runtime

- **Rust first** for durable software: CLIs, services, agents, gates, parsers,
  schedulers, release tooling, and harness checks.
- **TypeScript/React/Next only at the platform boundary**: product UI, app
  router surfaces, browser clients, or ecosystems where React is the product
  substrate.
- **Shell only as launcher glue**: bootstrap, curl-compatible install, tiny
  wrappers. No semantic workflow engines in shell.
- **Python only for narrow tooling exceptions**: notebooks, one-off data
  extraction, or dependency ecosystems that clearly beat Rust for the job.

## Build, CI, And Release

- **Repo-owned one-command gate first.**
  Every repo should have a canonical command, function, or build target that
  proves the change from local checkout state.
  Any host must be able to call it.
- **emulate.dev for supported third-party APIs** when local/CI gates need
  stateful GitHub, Stripe, AWS, etc. behavior without real credentials or
  network.
  Start only needed services (`npx emulate --service <svc>`).
  Seed and reset deterministically.
  Keep live-provider smokes for provider-only concerns.
  Usage details: https://emulate.dev/docs.
- **Dagger for infra-agnostic pipelines** when a repo needs portable CI
  execution across local and hosted runners, containerized dependencies,
  service orchestration, cache graph behavior, or traceable pipeline functions.
  Do not add Dagger merely to wrap ordinary host lint/typecheck/unit/build
  commands in the inner loop.
- **GitHub Actions as a thin caller**, not the product.
  Point it at the repo-owned portable gate or Dagger function.
  Do not bury logic in YAML.
- **Landmark by default** for release intelligence, versioning, changelog
  synthesis, and release distribution.
  Keep the core portable; GitHub is one adapter.

## Hosting

- **Cloudflare first** for DNS, CDN, static sites, mostly-static web, edge
  functions, Workers APIs, R2 public artifact/blob storage, D1 edge state,
  Queues, and Workflows.
- **Fly first** for Rust services, API backplanes, persistent volumes, ordinary
  process semantics, regional machines, WebSockets/TCP-ish assumptions, and
  agent sandboxes/Sprites.
- **Vercel by exception** when Next.js runtime fidelity, preview workflow,
  image pipeline, or product-team velocity beats portability.
  Re-check OpenNext on Cloudflare before keeping simple sites on Vercel.
- **Railway for prototypes** and short-lived demos, not durable idle services.
- **DigitalOcean as conventional fallback** for simple VPS/PaaS expectations or
  client familiarity, not as the strategic center.
- **AWS/GCP/Azure only for client/enterprise boundaries** or hard service
  requirements.
  Do not add hyperscaler gravity for small owned tools.

Financial default: Cloudflare + Fly is the portfolio spine.
Cloudflare reduces static/edge/blob spend.
Fly keeps small always-on services simple and predictable.
Do not move Fly-shaped services to Cloudflare Containers for cost alone unless
they sleep most of the time or can be rewritten to Workers/D1.

## Observability And Analytics

- **Canary first** for owned monitoring, health checks, service evidence, error
  timelines, and agent-readable operational truth.
- Production debugging starts by reading Canary state:
  health, incidents, checks, recent errors, and service evidence.
  Read it before forming a repo-local hypothesis.
- New services should include a Canary integration path unless you name a reason
  not to.
- **PostHog/Vercel Analytics by exception** when the product needs a
  mature external workflow now:
  session/product analytics, client-facing dashboards, or
  integrations Canary does not yet cover.
- Do not add Sentry. The account is retired and no service depends on it.
- If an external tool becomes recurring operating leverage, decide explicitly:
  build the missing Canary capability, keep renting it, or remove the workflow.

## Backlog And Work State

- Use Powder CLI/API through its root product skill for backlog management,
  work cards, issue discovery, claims, relations, operator input requests, and
  durable work status. Never register or call a Powder MCP surface.
- Do not keep durable backlog state in chat, TODO prose, or ad-hoc markdown
  when Powder is available.
  Markdown can brief or summarize.
  Powder owns the work-state record.

## Agent Substrate

- **Mode B unavailable**: event-triggered dispatch, reflex agents, CI-native
  review, incident response, scheduled workflows, and durable control loops
  have no active workflow plane.
- **OMP for Mode A**: ad-hoc operator work, skills, agents, shared doctrine,
  peer lanes, and local evidence loops.
- **Fly Sprites for heavy or isolated lanes**: remote sandboxes, golden
  checkpoints, long-running or parallel work.
- **OpenCode as the first open candidate for code-centric review runners** when
  we are building an owned reviewer or review-eval lane.
  Its server/session shape, SDK surface, JSON/event output, and provider
  neutrality fit coordinator/specialist designs better than terminal scraping.
  Keep the durable queue, sandbox, policy, model gateway, publisher, and eval
  warehouse outside OpenCode.
- **Goose for MCP-heavy cross-system workflows** where the agent's job spans
  code plus trackers, docs, browsers, chat, and internal tools.
  Do not choose it over OpenCode for review-first work unless MCP side effects
  are central.
- **Pi/OMP for local hackability and peer lanes**, not as a shared production
  control plane.
  Use Pi through OpenRouter when a small decorrelated lane is enough.
  Use OMP as an expert local environment when its LSP/debugger/worktree
  surface matters.
- **Buy before building commodity review** when automated PR review is not a
  differentiated capability.
  Run a bake-off against managed reviewers before adding harness machinery.
- Use Claude, Codex, Cursor, Antigravity, or Grok when their particular surface
  answers a distinct question.
  (Gemini CLI is retired — use Antigravity/`agy` for a Google-family lane.)

## Design And Artifact Surfaces

- **Repo `DESIGN.md` first** for product identity: palette, type, spacing,
  motion, and non-goals. Prefer one deliberate direction over house chrome.
- Use `/design`, `/prototype`, and `/improve-ui` for net-new or existing
  surfaces. Use `anthropic-frontend-design` when the risk is templated-default
  UI.
- **When agents author the UI, the design system must enforce itself.**
  A rules file (`AGENTS.md`/`CLAUDE.md`) rots and loses to nearby examples.
  Prefer a closed, intent-named token layer and a CI gate that fails on
  off-system values when the repo has a real design system package.
- **Prefer gating the rendered output** where a live surface exists.
  Lint authored source where no surface can render.
- For non-trivial plans and specs, use local HTML as the thinking medium.
  Open it for review before execution when the browser can load it.

## Data And Storage

- **SQLite first** for owned small services and local-first durable state.
- **D1 first** for edge-local relational state that fits Cloudflare's runtime.
- **Postgres when multi-writer relational scale earns it**.
  Do not add it for dashboard-sized data by habit.
- **R2 first** for public artifacts, evidence packets, screenshots, release
  assets, and blob storage where egress would otherwise dominate spend.
- Keep repo evidence in git when it is part of the source contract.
  Use object storage when artifacts are large, public, or operational.

## Override Checklist

Name the override in the plan or PR when departing from these defaults:
- Which default is being overridden?
- What live constraint forces the override?
- What current pricing/limit/source did you check?
- What local smoke proves the chosen platform works?
- What rollback or migration path remains open?
- What owned-system gap should be built later, if any?
