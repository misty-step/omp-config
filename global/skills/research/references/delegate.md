# Delegate

The lead frames work. Lanes gather evidence. The lead synthesizes.

## Role

1. Frame the claim or question each lane must test.
2. Route bounded work to researcher lanes or tools.
3. Collect outputs, URLs, commands, and artifacts.
4. Validate, filter, and resolve conflicts.
5. Produce the conclusion and residual risk.

## Lane types

| Lane | Use |
|---|---|
| Source scout | Find URLs, papers, docs, examples |
| Repo scout | Map local files, contracts, tests |
| Extractor | Scrape or map named sources with Firecrawl |
| Contradiction critic | Try to refute the leading claim |

## Dispatch packet

Give every lane:

- role and objective
- scope: files, domains, sources, boundaries
- output shape and maximum length
- evidence requirement: URL, file:line, command, or artifact
- what not to touch

State the goal, not a step script.

## Output

```markdown
## Accepted
- [claim] — evidence: [URL/path/command] — why it matters

## Rejected
- [claim] — reason: unsupported / stale / out of scope

## Synthesis
**Agreements** — ...
**Conflicts** — ...
**Residual risk** — ...
```
