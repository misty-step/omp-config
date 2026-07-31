# /factory-apps eval waiver

expires: 2026-08-15

## Reason

This skill routes capabilities across five live surfaces.
It does not define stable single-task behavior.
A useful eval needs fixture MCP configs or CLI surfaces for Canary, Powder,
Landmark, and Aesthetic, plus a status-only local Agent Vault wrapper probe.
Without those surfaces, the eval only tests whether the model repeats the
table.
## Disposition

This skill is not exempt from the eval-coverage contract.
When the waiver expires, add a small routing eval with cold prompts:
"where do I check a production incident?",
"where do I claim backlog work?", and
"where do I generate release intelligence?"
Grade it against the router and at least one live or fixture surface per app.

Until then, use drift in the skill catalog and this audit matrix as the falsifier.
The omp-config gate (`bin/check`) validates frontmatter shape and
config-contract integrity:

```bash
bin/check
```
