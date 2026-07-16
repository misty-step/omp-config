# /log-issues

Audit a domain and persist every verified finding in the registry-routed work
ledger.

## Usage

```text
/log-issues stripe
/log-issues production
/log-issues --all
```

## Domains

Scan `references/*-checklist.md` for available domains.

## Process

1. Run every check in `audit/references/{domain}-checklist.md` or the matching
   generated checklist. With `--all`, cover every applicable domain.
2. Resolve the repository's board from the routing registry. Ordinary Misty
   Step repositories use Powder; Adminifi and r90 use Habitat. No registered
   route is a harness gap: report it instead of inventing a file ledger.
3. Enumerate existing work before creating anything. Deduplicate by outcome,
   affected surface, and acceptance criteria—not title alone. Link related work
   when overlap is partial.
4. Create one card per distinct finding:
   - title: `[P0-P3] {Domain} — {failure}`
   - goal/body: what is wrong, impact, location, and constraints
   - acceptance: mechanically verifiable fix criteria
   - proof plan: exact command, route, or artifact that will prove resolution
   - priority, estimate, and labels: `domain/{domain}` plus `type/bug`,
     `type/enhancement`, or `type/chore`
5. Read each created card back. Report created IDs, duplicates skipped, related
   cards linked, and any finding that could not be persisted.

## Related

- `/audit <domain>` — audit without creating work
- `/fix <domain>` — fix findings instead of logging them
- `/groom` — reconcile and prioritize the resulting cards
