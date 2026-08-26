---
name: exocortex
description: Read and write registered fleet-memory cortices through the exocortex CLI.
---

# Exocortex

Exocortex is the authoritative interface to fleet memory. It protects committed
state, provenance, and concurrent writes. Do not edit a cortex checkout
directly.

## Read

Search before inferring prior decisions:

```sh
exocortex search "<query>" --json
exocortex get <path>
exocortex log <path>
```

Treat search results as leads. Read the source note before using a claim.

## Write

Use `exocortex note "<one durable fact>"` for small capture. Use `put` for a
full note:

```sh
exocortex put <path> --from <file>
exocortex put <path> --from <file> --expects <stored-revision>
```

A bare `put` creates only. Updates require the revision returned by `get`. On a
conflict, read the current note, reapply the change, and retry. Never overwrite
or fake provenance. Link related notes and supersede stale claims instead of
deleting history.

Done when the source was read, the write has one owner, and the stored result
was verified through `get`.
