---
name: powder
description: >
  Powder is the exclusive-work ledger. Use when listing takeable jobs,
  taking a job, asking the operator, or completing work with proof.
---

# Powder

Powder stores jobs. Take one. Finish it. Write proof.

## When

Use Powder when work must be exclusive across agents: the next takeable
job, a known job id, an operator question, or a completion.

## Origin

The CLI is an HTTP client of the deployed instance.

Origin is `POWDER_URL`, else `POWDER_API_BASE_URL`. Identity is
`POWDER_AGENT`. `--agent` wins.

`powder <command> --help` is flag truth. JSON on stdout. `list --plain`
and `show --plain` print text. Errors are JSON on stderr with `code`.

## Loop

1. `powder list --takeable --plain`
   Done when the list is on screen or empty.
2. `powder show <id>`
   Done when you can state the goal and the proof the spec asks for.
3. `powder take <id>`
   Done when the job is yours, or the `code` names why not.
4. Do the work the spec names.
5. `powder done <id> --proof <url-or-text>`
   Done when the job is terminal and you hold no lease.

One live lease per agent. `already_holding` means finish, ask, or
release first.

## Ask

Holder only. `powder ask <id> --question '...'` parks the job and
releases you. Any principal may `powder answer <id> --text '...'`.
Then someone takes it again.

## Take

`take` succeeds when the job is takeable and you hold no other live
lease. Takeable means: not terminal, not waiting, spec nonempty, no
live lease, every **direct** `blocked_by` exists and is terminal.

The `code` is the reason: `empty_spec` `blocked` `waiting` `held`
`already_holding` `terminal` `not_found` `no_origin`.

If you already hold `id`, `take` returns it.

## Verbs

```
powder serve
powder version
powder skill
powder list --takeable
powder show <id>
powder take <id>
powder release <id>
powder renew <id>
powder note <id> --text '...'
powder ask <id> --question '...'
powder answer <id> --text '...'
powder done <id> --proof <url-or-text>
powder abandon <id>
powder reopen <id>
powder create --id <slug> --title '...'
powder set-title <id> --title '...'
powder set-spec <id> --spec '...'
powder set-repo <id>
powder set-blockers <id>
```

`list` filters: `--takeable --waiting --repo --mine`. Order is
`created_at` ascending (scan order, not rank).
