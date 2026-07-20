# /harness-engineering audit — Harness Health

Measure what the catalog actually earns, then recommend lifecycle actions.

## Data

OMP does not ship a semantic skill-invocation telemetry engine or a
PostToolUse hook by default. Usage signal comes from mining local session
logs directly — count distinct sessions that actually read a skill via
`skill://<name>`:

```sh
cd ~/.omp/agent/sessions && find . -name '*.jsonl' -mtime -60 -print0 \
  | xargs -0 grep -EHo '"skill://[a-z-]+' \
  | awk -F: '{n=split($0,a,"skill://"); print $1" "a[2]}' \
  | sort -u | awk '{print $2}' | sort | uniq -c | sort -rn
```

Cross-check durable lane evidence on the relevant Powder cards. Analyze the
JSONL directly or with a bounded one-off query and preserve only the
resulting judgment.

Raw occurrence counts without the per-session `sort -u` are catalog noise,
not usage — the skill list rides in every prompt and a single session can
re-read a skill's sub-references many times.

## Judgment

- Usage is a power law; that's normal. The per-skill question is "low usage
  with a value-when-used story, or low usage with no story?" Only the
  second is a deletion candidate.
- Recency matters: a skill created last week with zero usage is unproven,
  not dead.
- Check staleness the other way too: heavy usage of a skill whose prose has
  rotted is a rewrite signal, not a health signal.
- Cross-check the primitive test (SKILL.md): a "skill" only ever invoked
  explicitly by the operator, never auto-triggered, may really be a prompt.

Output: per-skill verdict (keep / rewrite / demote to prompt / delete) with
the usage number, recency, and story behind each. Findings feed `/groom`
tickets; do not auto-fix.
