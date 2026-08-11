# Tracker protocol

The selected tracker adapter is explicit in `tracker.v1` and in `output.v1`'s `execution_overrides.selected_tracker`. The default Misty Step adapter is GitHub Issues; another tracker is valid only when the harness supplies the same query/create/read-back contract.

One serialized OMP-root tracker writer owns this protocol:

1. Build the canonical v1 finding fingerprint with `finding-fingerprint.mjs`. Normalize every string with Unicode NFC, CRLF/CR to LF, collapse all whitespace runs to one ASCII space, trim, and lowercase with the `en-US` locale. Normalize reproduction steps in order and join them with U+001F. Encode the version tag and each ordered field name/value pair (`affected_entrypoint`, reproduction, `expected`, `observed`, `category`) as UTF-8 byte-length-prefixed frames, join frames with U+0000, and hash the UTF-8 payload with SHA-256 as lowercase hex. Use the 64-character digest as the create idempotency key.
2. Exhaustively query the selected tracker with its `cursor` or `page` pagination contract. Follow every cursor/page until the adapter says there is no next page; no bounded result mode or caller-imposed result limit is valid.
3. Treat an ambiguous result, unavailable pagination, an explicit truncation signal, or an inconsistent read as a blocked write. Record `ambiguous: true` or `truncated: true` and create nothing.
4. Compare fingerprints and the normalized `affected_entrypoint` to existing items. Mark matching findings `deduplicated` and retain the existing issue identifier; their `tracker_issue_id` is required. Do not create a second issue for a similar but unresolved match.
5. File only findings that are both actionable and evidence-backed, meet the configured severity and confidence threshold, and fit under `maximum_creates`; mark them `accepted` only after the adapter creates the issue and the read-back succeeds, then record `tracker_issue_id`.
6. Read every newly created issue back through the adapter. Verify its identifier and required fields before marking it created. A failed read-back is a blocked result, not a success.
7. Preserve strengths and every suppressed friction reason in the report, even when no issues are created.

The tracker writer never fixes code. An authorized `fix-and-pr` handoff is a separate post-filing operation and receives the read-back issue IDs; it is never called from a persona or RCA session.
