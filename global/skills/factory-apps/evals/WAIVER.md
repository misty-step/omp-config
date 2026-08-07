# /factory-apps eval waiver

expires: 2026-08-15

## Reason

This skill routes capabilities across four live surfaces (Canary, Powder, Landmark, Mint).
It does not define stable single-task behavior.
A useful eval needs fixture CLI/API surfaces for Canary, Powder, and Landmark, plus a status-only Mint `/healthz` probe.
Without those surfaces, the eval only tests whether the model repeats the
table.
## Disposition

This skill is not exempt from the eval-coverage contract.
When the waiver expires, add a small routing eval with cold prompts:
"where do I check a production incident?",
"where do I claim backlog work?", and
"where do I generate release intelligence?"
Grade it against the router and at least one live or fixture surface per app.

Until then, use drift in the skill catalog and router table as the falsifier.
The omp-config gate (`bin/check`) validates frontmatter shape and
config-contract integrity:

```bash
bin/check
```
