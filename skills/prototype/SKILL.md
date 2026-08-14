---
name: prototype
description: Prototype uncertain logic, state, data, interaction, or UI decisions before production implementation.
license: MIT; modified from Matt Pocock's prototype skill
---

# Prototype

Answer one material question with disposable code.

## Choose

- Logic, state, data shape, or business rules: read `LOGIC.md`.
- Visual hierarchy or interaction: read `UI.md` and `frontend-design`.

Use `grill-me` only when the branch or question is a material operator choice.

## Define

State:

- question and riskiest assumption;
- observation that confirms or falsifies it;
- unchanged production behavior;
- stop condition;
- code to delete afterward.

Use a direct command or runtime probe instead when it can answer the question.

## Build

- Mark the path or visible title `PROTOTYPE`.
- Isolate the surface from production paths and mutations.
- Keep state in memory unless persistence is under test.
- Add no framework, service, dependency, abstraction, or telemetry unless it is
  the tested variable.
- Make relevant state and transitions visible.
- Start with one existing command or one self-contained file.

## Decide

Exercise the real surface. Record `confirmed`, `falsified`, or `inconclusive`
with the observed evidence. Source inspection is not proof.

Delete prototype code from the production tree. Preserve it elsewhere only when
the user asks or it is the only reproducible evidence. Reimplement the validated
decision to production standards; do not promote prototype shortcuts.
