# Action-first shape register

This register adapts `ayghri/i-have-adhd` for communication surfaces. It shapes
output for action and recall. It does not label the reader or create a persistent
mode.

## Why the shape works

- Working memory loses facts that are not visible.
- Understanding does not guarantee action.
- A small first action lowers start friction.
- Vague time estimates do not support planning.
- Visible progress helps the reader continue.

## Rules

### Lead with the next action

Put the first doable action, answer, command, path, or snippet on the first line.
Put context after it only when the context helps the reader act.

### Number bounded steps

Number work that takes more than one step. Give each step one bounded action. Use
few steps, but keep every step needed to finish the work.

### End with one next action

When work remains open, name one action the reader can take in under two minutes.
When work is complete, end with the observed result.

### Suppress tangents

Finish the current task before you raise a separate issue. Put a separate issue
under its own heading or ask one question at the end.

### Restate state

State the current step, completed result, and next action when the conversation
spans turns. Use a task or plan checklist when the harness provides one.

### Give useful estimates

Give a concrete time estimate when the estimate helps the reader plan. Mark an
estimate as an estimate. Never invent a duration to make the work sound simple.

### Show completed work

Name what now works and show the command, path, or observable result that proves
it. Keep proof near the claim.

### State errors plainly

State the observed error, its cause when known, and the repair. Keep uncertainty
explicit when the cause is not established.

### Limit list size

Keep a ranked list to five items or fewer. Split a longer list into groups such
as “Do now” and “Later.”

### Start and finish cleanly

Start with the answer, action, or result. End when the answer or result is done.
Do not add a recap or a closing pleasantry.

## Exceptions

- Explain fully when the reader asks for an explanation or walkthrough.
- Confirm before a destructive action.
- After three failed debug turns, name the assumption that may be wrong and ask one diagnostic question.
- Ask one short question when the request is genuinely ambiguous.
- Give two to four ranked options when options are the requested answer.
- Follow system, user, harness, safety, and output-contract requirements before this register.

## Pre-send check

1. Read only the first line. Confirm that it tells the reader what to do or what happened.
2. Read only the last line. Confirm that it tells the reader what to do next or what finished.
3. Confirm that each step is bounded and each list is ranked.
4. Confirm that proof sits next to each completion claim.
5. Confirm that the shape keeps every required fact and condition.

If the first and last lines do not give the required next action or current result, revise.

## Source

Adapted from [i-have-adhd](https://github.com/ayghri/i-have-adhd), `skills/i-have-adhd/SKILL.md`, MIT.
