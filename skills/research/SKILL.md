---
name: research
description: Research unfamiliar APIs, libraries, errors, protocols, and technology choices against primary sources before coding from memory. Use whenever about to implement against an interface you cannot currently read, debug an unexplained error, or adopt a dependency.
---

# Research

Close the gap between memory and the source before code touches it.
Hallucinated APIs are a standard failure mode, not an edge case.

## Trigger

Use this skill whenever about to write code against an interface you cannot
currently read: an unfamiliar library API, an unexplained error, a protocol
or file format, a technology choice. If the installed source or types are
readable locally, read them first — local truth outranks the web.

## Procedure

1. Frame the question so a source can answer it outright: "does X exist in Y
   at version Z", "what does error E mean coming from W".
2. Web-search first (exa is the default provider). Prefer primary sources:
   official docs, the project's source and changelogs, RFCs, papers. Blog
   posts are leads, not answers.
3. Verify consequential behavior against the actual source or types of the
   version in use. A v3 README does not describe the v4 in the lockfile.
   Before calling an API, confirm the symbol exists at the installed version.
4. Timebox. If the question is still open after a bounded pass, say what is
   open and choose the safest path that does not depend on it.

## Adopting something?

Apply the dependency ladder: stdlib, then a small maintained dependency,
then your own code. Before adopting, check license, maintenance activity,
and transitive weight — adopting a dependency adopts its security and
maintenance burden.

## Output

Research ends in a decision artifact, never silence: chosen option,
rejected options with the reason each lost, open questions. Durable choice
becomes an ADR; ephemeral, a ticket, PR description, or conversation note.
