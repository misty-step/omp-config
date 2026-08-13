---
name: firecrawl
description: Extract a known page or bounded site tree through OMP's Mint-backed Firecrawl route.
argument-hint: "[scrape|map|crawl|search] [URL|query] [--limit N]"
disable-model-invocation: true
---

# /firecrawl

Use Firecrawl to extract a known page, map a site, or run an explicitly bounded crawl. Use Exa first when the job is source discovery.

Read `skill://research/references/firecrawl-tools.md` before the first call. That reference owns the current MCP and REST contract, Mint marker, bounds, polling behavior, and fallback route. Use `skill://research` when the request also needs evidence synthesis or independent research lanes.

Do not add another Firecrawl wrapper, MCP server, credential path, or command recipe here. Keep the canonical procedure in `/research`.

## Completion Gate

Apply the Shared Operating Spine (`Prove`; Durable State and Closeout). Report the operation, target, explicit map or crawl bound, response status, extracted URLs, and unresolved acquisition gaps.
