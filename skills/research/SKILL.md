---
name: research
description: Verify unfamiliar APIs, errors, protocols, and dependencies against current primary sources before coding.
---

# Research

Memory is not an interface contract. Verify the exact version in use before
code depends on it.

Frame one answerable question. Search current primary sources first: installed
source or types, official documentation, source repositories, changelogs,
standards, and papers. Use secondary sources only to find primary evidence.
Confirm consequential behavior against the installed version.

For a dependency, prefer standard library, then a small maintained package,
then owned code. Check license, maintenance, transitive weight, and version
compatibility.

Timebox the search. Return the chosen answer, direct sources, rejected answers,
version limits, and open gaps. Choose the safest path that does not depend on an
unresolved claim.

Done when every implementation-critical claim is source-verified or explicitly
excluded from the design.
