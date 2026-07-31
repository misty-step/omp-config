# Exemplar Discovery

Find best-in-class implementations for techniques that a project should study.
Use cross-language and cross-domain sources, not only same-domain prior art.

## The `exemplars.md` Convention

Keep `exemplars.md` at project root as a curated list of reference implementations.
Organize entries by technique, not language or domain.

```markdown
# Exemplars

## Search / Indexing
- [fff.nvim](https://github.com/dmtrKovalenko/fff.nvim) (Zig)
  **Technique:** SIMD-accelerated fuzzy finding, cache-oblivious memory layout
  **Study for:** hardware-aware search optimization
  **Key file:** `src/simd_search.zig` — core matching loop

## Concurrency
- [crossbeam](https://github.com/crossbeam-rs/crossbeam) (Rust)
  **Technique:** Lock-free data structures, epoch-based memory reclamation
  **Study for:** concurrent data structure design
  **Key file:** `crossbeam-epoch/src/internal.rs` — epoch reclamation
```

### Entry fields

- **Technique** — What it does exceptionally well. Hardware-aware optimization,
  algorithmic breakthrough, elegant API design, etc.
- **Study for** — Why it matters to *this* project. Show the cross-domain transfer.
- **Key file** — Where to look first. Agents read this file, not the whole repo.
  Keep one file per entry. Add a second file only when one file cannot show the full technique.

### What makes a good exemplar

- **Disproportionate performance** — much faster than expected.
  Choose projects with unusually strong performance.
- **Hardware-aware design** — exploits modern hardware: SIMD, cache-oblivious
  algorithms, io_uring, lock-free concurrency, massive parallelism (64+ cores),
  NVMe-optimized I/O, large memory (256GB+) data structures.
- **Cross-domain transferability** — the technique teaches something applicable
  beyond the project's specific domain. A Zig fuzzy finder can teach a Rust
  search library. A Go scheduler can teach a Python task queue.
- **Readable excellence** — structured enough for an agent to clone and read the key file.
  Require the agent to extract the core insight in under 5 minutes.

## What is NOT an exemplar

- Projects that are popular but only competent.
- Projects valuable only for their API surface, not implementation.
- Frameworks whose value comes from ecosystem, not technique.
- Abandoned projects without a maintenance signal.

## Discovery: Exa Queries

### Find best-in-class implementations

```bash
curl -s https://api.exa.ai/search \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "fastest [DOMAIN] implementation [TECHNIQUE]",
    "type": "code",
    "numResults": 10,
    "useAutoprompt": true,
    "contents": { "text": { "maxCharacters": 2000 } }
  }'
```

Good query patterns:
- `"fastest [domain] implementation"` — finds performance-focused projects
- `"SIMD [domain] rust OR zig OR c++"` — finds hardware-aware implementations
- `"zero-copy [domain] implementation"` — finds allocation-conscious designs
- `"lock-free [domain]"` — finds concurrent data structures
- `"io_uring [domain]"` — finds modern I/O designs
- `"cache-oblivious [domain]"` — finds memory-hierarchy-aware algorithms

### Expand from a known exemplar

```bash
curl -s https://api.exa.ai/findSimilar \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/KNOWN_EXEMPLAR",
    "numResults": 10,
    "contents": { "text": { "maxCharacters": 1000 } }
  }'
```

When the user provides a seed exemplar, find more projects like it.

## Discovery: xAI Social Signal

Use the configured research provider surface for xAI X Search when the
operator has enabled it. If the request needs vendor credentials, run the
caller inside the Agent Vault wrapper with an approved service rule; the rule
owns `Authorization`. This source does not define an xAI credential
placeholder or expose provider keys in agent context.

Social signal finds projects that benchmarks and READMEs miss.
It finds projects that developers praise.

## Output Format

Format results for direct inclusion in `exemplars.md`.

```markdown
## [Technique Domain]
- [Project Name](URL) (Language)
  **Technique:** [what it does exceptionally well]
  **Study for:** [why it matters to the target project]
  **Key file:** `[path]` — [what to learn from this file]
```

When updating an existing `exemplars.md`, preserve existing entries.
Add new entries under existing sections or create new sections.
Remove entries only when the user requests removal or the project is dead or archived.

## Integration with Default Fanout

When standard `/research` fanout finds exemplary implementations through Exa code search, format implementation-worthy results with the convention above.
These results often answer queries about "how to build X" or "best approach for Y".
If `exemplars.md` exists at project root, offer to add discoveries to it.
