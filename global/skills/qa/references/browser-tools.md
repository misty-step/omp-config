# Browser Tools for Agent-Driven QA

Choose the control surface that the active Harness can actually host. In a
terminal Harness, prefer CLI and MCP tools. OpenAI's built-in Browser is not
available in Codex CLI; Computer Use and the Chrome-extension setup are
documented through the ChatGPT desktop app. Do not turn one native-bridge
availability failure into an extension reinstall, process-kill, or signing
investigation. Route to a CLI-native tool unless the task is running in the
desktop app and specifically requires its native surface.

## Selection

| Need | Default | Why |
|---|---|---|
| Browse, fill forms, inspect DOM, capture screenshots | `agent-browser` | Small CLI/skill surface, compact snapshots, no MCP schema tax |
| Reproducible app QA or a test artifact | Playwright CLI | Test-oriented sessions, traces, and generated proof |
| Console, network, performance, Lighthouse, heap, or live-Chrome debugging | Chrome DevTools MCP | Chrome-specific diagnostic depth |
| Persistent exploratory loop over structured page state | Playwright MCP | Stateful MCP loop when its larger tool/context surface earns the cost |
| Remote browser, proxies, geography, anti-bot, or shared cloud session | `agent-browser` with Browserbase provider | Keeps the same CLI contract; credentialed cloud escalation |
| Natural-language `act` / `observe` / `extract` backed by Stagehand | Browserbase MCP | Opt-in semantic layer, cloud boundary, credentials, and billing |

Stop at the first row that satisfies the task. Do not register every browser
MCP by default.

Registration examples below use Codex CLI. They are explicit operator setup;
other Harnesses use their own user-owned registration surface. Runtime agents
route among tools already available to the active Harness.

## agent-browser

Generic browser automation default for terminal agents.

```sh
npm install -g agent-browser
agent-browser install

agent-browser open https://example.com
agent-browser snapshot -i
agent-browser click @e1
agent-browser screenshot --annotate /tmp/qa-example.png
agent-browser close
```

Use named sessions when work must coexist. Re-snapshot after navigation or any
DOM-changing action; element refs are page-state handles, not durable selectors.
Connect through CDP only when existing Chrome state is actually required.

The curated `agent-browser` skill should teach the active CLI. If installing it
for another compatible coding agent, use the upstream discovery stub rather
than copying a versioned `SKILL.md`:

```sh
npx skills add vercel-labs/agent-browser
```

## Playwright CLI

Prefer the CLI for coding-agent QA that should leave tests, traces, or compact
disk artifacts instead of streaming a large MCP schema and page tree into
context.

```sh
npm install -g @playwright/cli@latest
playwright-cli install --skills
```

Use the repository's Playwright tests and configuration when present. A global
CLI does not replace repo-owned test fixtures, auth setup, or assertions.

## Chrome DevTools MCP

Use for Chrome diagnostics, not as the generic browser driver.
Runtime agents route here only when it is already available. The following is
operator setup that mutates Codex's user-owned configuration; do not run it as
availability repair during an ordinary task:

```sh
codex mcp add chrome-devtools \
  --env CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS=1 \
  -- npx -y chrome-devtools-mcp@latest \
  --no-performance-crux --redact-network-headers
```

Its unique surface includes console and network inspection, performance traces,
Lighthouse, heap snapshots, and Chrome emulation. It uses a dedicated profile
by default. Connecting to an existing logged-in Chrome is a separate, explicit
CDP/remote-debugging choice; never weaken Chrome security flags merely to avoid
using a dedicated automation profile.

## Playwright MCP

Use only when a persistent, iterative accessibility-tree loop is more valuable
than the CLI's smaller context footprint.
Runtime agents use it only when already registered. This is explicit operator
setup for Codex's user-owned configuration:

```sh
codex mcp add playwright -- npx -y @playwright/mcp@latest
```

It needs no API credential. Treat it as browser automation, not a security
boundary, and use isolated profiles for concurrent agents.

## Browserbase

Prefer Browserbase through the existing `agent-browser` interface when local
Chrome is unavailable or the task requires remote sessions, proxies,
geolocation, concurrency, or anti-bot infrastructure:

```sh
# BROWSERBASE_API_KEY must be resolved by the credential broker at invocation.
agent-browser -p browserbase open https://example.com
```

Do not put a Browserbase key in a command, hosted-MCP URL, repository, or
Harness config. The hosted Browserbase MCP authenticates through URL query
state, which does not fit Roster's secret-reference contract. The self-hosted
`@browserbasehq/mcp` server is allowed only behind a broker wrapper that injects
`BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID`, and the Stagehand model
credential required by the selected model (for the default, `GEMINI_API_KEY`)
at process launch. Never put a model credential in `--modelApiKey`.

Use Browserbase MCP rather than the provider only when Stagehand's semantic
`act`, `observe`, and `extract` operations are themselves the requirement.
That path adds a model layer, nondeterminism, cloud data handling, and billing.

## Evidence

- OpenAI: [Browser](https://learn.chatgpt.com/docs/browser),
  [Computer Use](https://learn.chatgpt.com/docs/computer-use), and
  [Chrome extension](https://learn.chatgpt.com/docs/chrome-extension)
- Vercel Labs: [agent-browser](https://github.com/vercel-labs/agent-browser)
- Microsoft: [Playwright CLI](https://github.com/microsoft/playwright-cli) and
  [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- Google: [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- Browserbase: [agent-browser integration](https://docs.browserbase.com/integrations/agent-browser/quickstart)
  and [MCP setup](https://docs.browserbase.com/integrations/mcp/setup)

Re-check upstream package names and support before changing installation or
routing policy; browser tooling is release-sensitive.
