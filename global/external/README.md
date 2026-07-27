# Vendored external skills

Skills under this directory are copied bodies of externally owned skills, not
locally authored content. `registry.yaml` is the canonical provenance ledger.

Each committed vendor directory has one `.sync-meta.json` receipt. The receipt
pins the upstream commit, license bytes, payload file list, and SHA-256 for
every payload file. The matching registry entry names the vendor directory,
redistribution license, and live consumer paths. `bin/check` rejects registry,
receipt, payload, license, symlink, and consumer drift.

To advance a pin, fetch upstream at the new immutable SHA, copy the payload,
update its receipt and registry entry together, then run the source gate. Do
not edit a vendored payload in place; an edited copy is a fork and must not
pretend to be an upstream pin.
