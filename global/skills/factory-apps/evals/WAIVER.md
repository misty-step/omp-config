# /factory-apps eval waiver

expires: 2026-08-15

## Reason

This skill is a capability router over five live product repos, not a stable
single-task behavior. A useful eval needs fixture MCP configs or mocked CLI
surfaces for Canary, Powder, Landmark, Aesthetic, and Bitterblossom; otherwise
it would only test that the model can repeat the table.

## Disposition

Not exempt from the eval-coverage contract. When the waiver expires, add a
small routing eval with cold prompts such as "where do I check a production
incident?", "where do I claim backlog work?", and "where do I generate release
intelligence?", graded against the router plus at least one live or fixture
surface per app.

Until then, the falsifier is drift in the primitives catalog and this audit
matrix. The roster gate validates frontmatter, referenced-path existence,
skills-index/disk parity, and conflict markers:

```bash
cargo run --locked -p roster-cli -- check
```
