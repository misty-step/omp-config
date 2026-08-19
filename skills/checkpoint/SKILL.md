---
name: checkpoint
description: >
  Checkpoint is the local interval ledger CLI. Use when you start or stop a
  work clock, read the open clocks, read one day, or correct a recorded entry.
---

# Checkpoint

Checkpoint records work time. It keeps open clocks and closed intervals.

## Types

An `Open` has a start time `t0`. It has no end time.

An `Interval` has a start time `t0` and an end time `t1`. `t1` is always
after `t0`.

A stream is one client. This version uses the client name as the stream name.

## Rules

Checkpoint appends each command to a log. It never rewrites a log line.

To pause a clock, stop it. To continue the work, start the clock again.

To change a recorded entry, append a correction. Do not edit the log file.

## Verbs

```
checkpoint start <client> [label]
checkpoint stop <client> [reason]
checkpoint status
checkpoint day [YYYY-MM-DD]
checkpoint correct <id> [--t0 <time>] [--t1 <time>] [--label <text>] [--reason <text>]
```

`label` defaults to `general`. `date` defaults to today. `checkpoint <command>
--help` lists the exact flags.

## Run

The binary is not on `PATH`. The repository is
`~/Development/misty-step/checkpoint`.

Run `cargo run --` in that repository, then the command. Write
`cargo run -- status`. The examples below use `checkpoint` for the binary.

## Clock and data

`--at <RFC3339>` sets the time for one process. `CHECKPOINT_NOW` does the same.

Put `--at` before the command. Write `checkpoint --at <time> stop r90`.

`--data-dir <path>` sets the data directory. `CHECKPOINT_DATA_DIR` does the
same. The default directory is `~/.checkpoint`. The log file is `log.jsonl`.

## Read the output

`status` prints one line for each open clock, then one total line:

```
open  r90 / payroll-migration  39600s  r90-1787022000000
total 43200s
```

`idle` means that no clock is open. The last field is the entry id. Give that
id to `correct`.

`day` prints the date, then each open clock of today, then each interval of
that day:

```
day 2026-08-17
interval  r90 / audit  2026-08-18T03:00:00+00:00  2026-08-18T04:00:00+00:00  leftover  r90-1787022000000
```

Times in `day` output are UTC. An interval belongs to every local day that its
range touches. A closed interval that ran through midnight is on both days.

An open clock belongs only to today. `day` shows no open clock for an earlier
date. To find a clock that ran all night, use `status` or `day` with no date.

## Correct a clock that ran too long

A clock that ran all night is still open. Stop it at the intended time:

```
checkpoint --at 2026-08-17T23:00:00-05:00 stop r90 leftover
```

A closed interval has the wrong end time. Append a correction:

```
checkpoint correct r90-1787022000000 --t1 2026-08-17T23:00:00-05:00 --reason "stopped earlier"
```

## Rejects

Checkpoint writes the reason to stderr. It exits with status 1. It writes no
log line.

- `stream <name> is already running` — that stream has an open clock.
- `stream <name> is not running` — that stream has no open clock.
- `stop time is not after start` — `t1` is not after `t0`.
- `entry <id> not found` — no entry has that id.
- `correct has no fields` — give at least one option to `correct`.
- `use stop to close an open clock` — do not send `--t1` for an open clock.
- `reason only applies to a closed interval` — do not send `--reason` for an
  open clock.

## Refusals

Checkpoint is a Misty Step tool. It is not R90 Time Tracker. Do not read or
write `~/.timesheet-tracker`.
