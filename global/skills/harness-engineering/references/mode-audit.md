# /harness-engineering audit — Harness Health

Measure what the catalog earns, then recommend lifecycle actions.

## Data

OMP does not ship semantic skill-invocation telemetry or a PostToolUse hook by
default.
Mine local session logs directly for usage signals.
Count distinct sessions that read a skill through `skill://<name>`:

```sh
cd ~/.omp/agent/sessions && find . -name '*.jsonl' -mtime -60 -print0 \
  | xargs -0 grep -EHo '"skill://[a-z-]+' \
  | awk -F: '{n=split($0,a,"skill://"); print $1" "a[2]}' \
  | sort -u | awk '{print $2}' | sort | uniq -c | sort -rn
```

Cross-check durable lane evidence in the relevant Issues.
Analyze the JSONL directly or with a bounded one-off query.
Keep only the resulting judgment.

Raw occurrence counts without the per-session `sort -u` are catalog noise, not
usage.
The skill list rides in every prompt.
A session can re-read a skill's sub-references many times.

## Judgment

Usage is a power law; that is normal.
For each skill, ask, "Does low usage have a value-when-used story, or no
story?"
Only the second case is a deletion candidate.
- Recency matters.
  A skill created last week with zero usage is unproven, not dead.
- Check staleness in the other direction.
  Heavy use of a skill with rotted prose signals a rewrite, not health.
- Cross-check the primitive test in `SKILL.md`.
  A skill invoked only by the operator, never automatically, may really be a
  prompt.

Output a verdict for each skill: keep, rewrite, demote to prompt, or delete.
Include the usage number, recency, and reason.
Send findings to `/groom` tickets.
Do not auto-fix.
