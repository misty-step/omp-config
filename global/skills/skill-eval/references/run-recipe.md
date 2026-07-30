# /skill-eval run recipe

Use this recipe to produce arm A, arm B, and the blind grader, from cheap smoke
to serious runs.

## Cheap smoke (free, native subagents)

Prove that the loop fires and can return A≠B. Use one fixture and a shared
family (waiver). Use this on every skill edit and to debug an eval before you
pay for the decorrelated run.

1. **Arm A** — Give a fresh subagent the fixture prompt and a read-only repo.
   Tell it to invoke the skill (`/<skill>`). Request the artifact only. Do not
   allow repo edits.
2. **Arm B** — Give a fresh subagent the same fixture prompt and repo. Give it
   the bare instruction a sharp operator would type, without mentioning the
   skill. Request the artifact only.
3. **Grader** — Give a fresh subagent both artifacts, labeled X/Y and shuffled,
   plus the fixture and the eval spec's checks and rubric. Do not tell it which
   arm uses the skill. Request objective-check results, rubric scores, and a
   "which is more <claim>" verdict.

Run A and B in parallel. Run the grader after both arms finish. Save all three
outputs to the evidence packet. The smoke has an honest limit: workers and
grader share a family, so it proves the mechanism and catches gross regressions.
It does not certify the margin. The serious run must establish the margin.

## Serious run (paid, decorrelated)

For contract changes and model-upgrade re-audits, use `council.sh`. It runs the
arms and grader on *different model families* from one another.

- Write each arm's full task to one file. Lanes are cold. Include the fixture,
  repo context, forbidden edits, and what "done" means.
- `members.tsv` = one line per arm/grader: `label  cli  model  persona`.
- `global/skills/council/scripts/council.sh --task /tmp/<arm>.txt --members
  /tmp/members.tsv --outdir .evidence/harness-evals/<skill>/<date>/<arm>`
- Pull live slugs (roster index / OpenRouter MCP). Never hardcode them. An
  instantly failing lane usually has a dead slug or auth lapse, not a verdict.
- Grader lane: use a family distinct from *every* worker lane.

## The clean A/B knob (enforced skill visibility)

The prompt-level "invoke the skill / do not mention it" split uses the
honor-system. A worker can ignore it. When the harness can enforce skill
visibility, prefer that. Let arm A allow only `<skill>` and arm B allow none.
Use the same provider target, oracle, and evidence expectations. Then "skill on
vs off" is a config diff, not an instruction that the worker can defy.

## Evidence packet

```
.evidence/harness-evals/<skill>/<date>/
  fixtures/<id>/{prompt.md, repo-sha}
  arm-a/{artifact, transcript}
  arm-b/{artifact, transcript}
  arm-c/...                      # optional alternative primitive
  grader-<family>.md             # objective results + rubric + verdict
  report.md                      # score matrix, variance note, decision label
```

Sanitize the packet to final artifacts and scored receipts only. Exclude
secrets, raw provider logs, and customer data. Use one decision label:
`keep` / `adapt` / `cut` / `needs-more-tasks` / `graduate-to-Daedalus`.
