---
name: research
description: Verify unfamiliar APIs, errors, protocols, and dependencies against current primary sources before coding.
---

# Research

Frame one answerable implementation question. Verify the exact version in use
before code depends on it.

Search primary sources in this order: installed source or types, official
documentation, source repositories, changelogs, standards, and papers. Use
secondary sources only to locate primary evidence. Confirm consequential
behavior against the installed version.

For dependencies, prefer the standard library, then a small maintained package,
then owned code. Check license, maintenance, transitive weight, and version
compatibility.

Return the chosen answer, direct sources, rejected alternatives, version limits,
and open gaps. Exclude any implementation path that depends on an unresolved
claim.
