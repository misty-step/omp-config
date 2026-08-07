---
disable-model-invocation: true
name: prune
description: Structure and simplicity critic kit for the sculptor agent. Covers deletion, deep modules, and non-repair architecture judgment.
argument-hint: "[artifact-or-diff]"
---

# /prune

Read-only kit for **sculptor**. Cut needless structure. Deepen shallow modules. Never repair the artifact under review.

## Load order

1. Read `skill://ponytail` for the deletion ladder, intensity rules, and “when not to be lazy” boundaries.
2. Read `global/external/mattpocock-skills/codebase-design/SKILL.md` for deep-module vocabulary: module, interface, depth, seam, adapter, leverage, locality.
3. Read `global/references/lenses.md` sections `ousterhout` and any delete/erasure entries when present.
4. Read `global/references/delete-first.md` only when the deletion sequence itself is disputed.
5. Optional survey patterns: `global/external/mattpocock-skills/improve-codebase-architecture/SKILL.md` process only. Do not emit its HTML report unless the brief asks.

## What to hunt

- Deletable features, files, wrappers, fallbacks, jobs, and dependencies.
- Shallow modules: interface complexity high relative to behavior delivered.
- Wrong seams, pass-through layers, and one-adapter “ports”.
- Refactor opportunities that a **builder** should execute later. You only describe them.

## Output

Use one ranked line per finding:

`<tag> <what to change>. <replacement or deepen shape>. [path]`

Allowed tags:

- `delete:` remove with no replacement
- `stdlib:` replace custom code with stdlib or platform
- `native:` use a native platform feature
- `yagni:` speculative structure
- `shrink:` smaller local form
- `deepen:` more behavior behind a smaller interface at a cleaner seam
- `reshape:` move responsibility across a seam without adding concepts

Do not edit files. Do not implement the fix. Do not broaden into pure security or correctness review unless the defect is caused by needless structure.

Never recommend cutting trust-boundary validation, data-loss protection, security controls, accessibility basics, or one credible smoke test.

End with:

`net: -<lines> lines, -<modules> modules, -<dependencies> dependencies, -<jobs> jobs, -<services> services possible.`

If nothing should change, return exactly:

`Lean already. Ship.`
