# Browser fallback

Use browser automation only when static extraction fails or the page needs interaction.

## Prefer order

1. Firecrawl scrape or Exa fetch for static content.
2. Builtin OMP `browser` tool for simple rendered reads and clicks.
3. `agent-browser` CLI for harder automation, snapshots, network, and console evidence.

Do not add Playwright MCP or chrome-devtools MCP for research.

## When to escalate

- Firecrawl or Exa return empty, blocked, or login-walled content.
- The claim depends on client-rendered state after user actions.
- You need screenshots, console errors, or network calls as evidence.

## agent-browser

Discover commands with:

```bash
agent-browser skills get core
```

Typical research uses:

```bash
agent-browser open https://example.com
agent-browser snapshot
agent-browser screenshot /tmp/research.png
agent-browser close --all
```

Close sessions when finished.

## Rules

- Bound the session to one named URL or flow.
- Capture URL, steps, and artifact paths with the finding.
- Do not browse production admin surfaces unless the operator authorizes it.
- Prefer read-only observation during research. Mutation belongs to product workflows, not `/research`.
