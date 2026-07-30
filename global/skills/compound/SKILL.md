---
disable-model-invocation: true
name: compound
description: |
  Capture one compounding repo-technical learning while the solved problem is
  fresh. Trigger: /compound, /capture-learning, /learning.
argument-hint: "[solved-problem-summary]"
---

# /compound

Capture the learning, not the full history.


## Contract

- One solved problem -> one learning.
- Corpus: `docs/solutions/<category>/<slug>.md`; schema:
  `global/references/learnings.md`.
- Check overlap first:
  `rg -n --glob '*.md' '^(title|tags|applies_when):|<module>|<failure-mode>' docs/solutions`.
- If an existing learning covers the problem, update that file only when fresh
  evidence contradicts or sharpens it.
  Otherwise, do not add a near-duplicate.
- If the learning is new, use grep-ready frontmatter:
  `title`, `tags`, `module`, `problem_type`, `applies_when`, `severity`, `date`.
- Cite checkable evidence: `repo@SHA`, PR, command, route, and `file:line`
  when possible.
  Session notes can provide context, but they are not the anchor.
- Promote pattern docs from multiple learnings.
  Never author a broad doctrine page from one bug.


## Write Discipline

At read, let present evidence win.
At write, refresh only nearby learnings that could conflict.
When evidence contradicts, refresh the smallest corpus slice that could be wrong.


## Completion Gate

See `global/references/verification-system-first.md` for the shared proof contract.
`/compound` adds the path written or updated, the overlap query used, the
evidence anchor, and 3-6 retrieval terms that future agents should grep.
