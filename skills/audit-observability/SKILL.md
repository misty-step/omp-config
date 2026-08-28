---
name: audit-observability
description: Check whether operators can answer a named failure or recovery question.
disable-model-invocation: true
argument-hint: "[system and operator question]"
---

# Audit observability

This audit is read-only. Start from the operator question, not an observability
catalog.

Name the failure, affected boundary, release identity, and evidence sources.
Trace only the signal path needed to answer what failed, who was affected, which
release caused it, or how to recover. Use safe read probes and current
infrastructure authority.

A finding states the unanswered question, missing or misleading signal,
consequence, evidence, and smallest repair. Recommend a provider only when the
required signal is clear and the current system cannot supply it.

Return the answer, evidence gaps, confirmed findings, and ordered repairs. Do
not implement them.

Done when each recommendation closes a demonstrated operator question.
