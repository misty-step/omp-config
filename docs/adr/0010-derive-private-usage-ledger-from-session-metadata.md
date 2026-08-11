# ADR 0010: Derive a private usage ledger from session metadata

- Status: Accepted
- Date: 2026-08-11

## Context

OMP session files contain model usage, cost, timing, and agent attribution. They also contain prompts, completions, tool arguments, and possible credentials. Raw session scans are too slow and difficult to query for routine cost analysis.

The ledger is derived instrumentation. Session files remain the source of truth.

## Decision

`bin/usage_ledger.py` reads session files and stores only response identity, model, provider, agent, repository, token, cost, and timing metadata in local SQLite.

The ledger must not store prompts, completions, tool arguments, or credentials. Its directory must have mode `0700`. Its database must have mode `0600`.

The default database is `~/.omp/agent/usage-ledger.sqlite3`. Incremental ingestion records file inode and byte offset. Repeated ingestion is idempotent.

Schema versions use SQLite `user_version`. A report refuses an incompatible schema. An ingest run drops and rebuilds derived tables from session files instead of migrating them.

## Consequences

Queries become fast and reproducible without creating another source of sensitive conversation content. Deleting the database loses no authoritative data because ingestion can rebuild it.

Retention follows the source session files. The ledger cannot retain a response after every source copy disappears unless it was ingested earlier. Operators can remove the database independently.

## Rejected alternatives

- Query raw JSONL for every report. This repeats parsing and makes cross-session analysis slow.
- Store complete session records in SQLite. This duplicates sensitive content and expands the credential boundary.
- Add a service. One local user and one derived database do not justify deployment or network access.
- Migrate old schemas. Rebuilding is simpler because every row is derived from local session files.
