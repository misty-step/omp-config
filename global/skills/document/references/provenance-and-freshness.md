# Provenance & freshness — the committed-docs contract

Committing docs into `docs/` versions them with the code. It includes doc changes in PR diffs and carries docs through forks and offline clones. It also means docs drift when code changes. Drift in committed docs can persist without an error or clear signal. Make drift **detectable** with provenance and **checkable** with a falsifier.

## Per-page provenance stamp

Every generated page carries front-matter (see `templates/page.md`):

```yaml
---
title: Authentication
generated-at-sha: a3f1c2d          # repo HEAD when this page was written
covers:                            # source globs this page describes
  - src/auth/**
  - src/middleware/session.ts
verified: 2026-06-25               # last accuracy-oracle pass
model: <generating model + verifier family>
---
```

`covers:` carries load-bearing semantics. Coverage, incremental scope, and freshness use it. Be precise. Over-broad globs make pages stale too often. Over-narrow globs let drift escape.

## Freshness falsifier

- **Claim:** every committed page is true of the current HEAD.
- **Falsifier:** a page whose `covers:` globs match files changed since its `generated-at-sha`.
- **Driver:** `scripts/freshness.py [docs_dir]` — parses each page's stamp, runs `git diff --name-only <sha>..HEAD`, and reports pages whose covered files moved. Exits non-zero if any page is stale, so it can gate.
- **Grader:** zero stale pages = synced. Stale pages are the incremental-scope work list.
- **Cadence:** start every run (to scope the work) and run on `--check`.

## Incremental scope

The quality bar stays constant. Run the full verify loop every time. Scope does not.
On a rerun, regenerate only:

1. pages the freshness driver flagged stale, plus
2. their cross-link neighbors (a changed system can falsify a claim on a page that points at it).

Use `--full` to regenerate everything after large refactors or IA changes. This keeps the world-class standard while limiting work on small changes.

Keeping committed docs fresh on every push would be an event-triggered Mode B
loop, but no active event plane is available. `/document` is the on-demand
Mode A generator. The freshness driver is the local trigger contract. Do not
build push-triggered automation inside this skill or invent a replacement
service.

Until a future product is explicitly named, staleness stays visible (stamped
and `--check`-able) between manual runs. This is better than invisible drift in
an unstamped wiki.

