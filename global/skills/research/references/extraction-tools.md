# Extraction tools

Use extraction when the task names a URL, site, crawl, sitemap, or page-content target.

Do not route ordinary broad discovery here.

## Route table

| Need | Prefer | Fallback |
|---|---|---|
| Fetch known URL | Firecrawl scrape | Exa fetch |
| Clean markdown from a page | Firecrawl scrape | browser snapshot |
| Map a site or docs corpus | Firecrawl map | manual link walk |
| Crawl a bounded docs site | Firecrawl crawl with `limit` | map + selective scrape |
| Dynamic or logged-in page | builtin `browser` or `agent-browser` | operator artifact |

Load `firecrawl-tools.md` for commands. Load `browser-fallback.md` for interaction.

## Rules

- Bound crawls by domain, path, max pages, and time.
- Emit source URLs and extraction status.
- Prefer official docs or repo-local files before paid extraction.
- Browser is the fallback for dynamic pages, not the default for static pages.
