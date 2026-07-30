# image-gen eval waiver

expires: 2026-09-30

## Reason

image-gen's load-bearing claim is a routing judgment: image or HTML/CSS
prototype. It also covers provider/model selection and mockup prompting craft.
A falsifiable A/B needs a rubric-graded image-quality judge for legible in-image
text and spatial layout fidelity.
It also needs a frozen set of design briefs.
That harness does not exist yet. Routing depends on model-capability facts that
change within weeks.

## Disposition

Defer this work for a fixed time. Do not treat the waiver as a permanent opt-out.
When it expires, add an eval spec at
`global/skills/image-gen/evals/image-gen-eval.md`.
Use `global/skills/skill-eval/templates/eval-spec.md` as the template.
A cheap first cut can test the routing decision alone: skill-on versus raw
same-model on prompts that should route to HTML.
Grade it objectively without an image judge.
Alternatively, renew this waiver with a fresh reason and date.
A silently renewed waiver is itself a finding for `/harness-engineering`'s next
skill-health audit.
