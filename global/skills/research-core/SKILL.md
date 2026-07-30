---
name: research-core
description: Apply harness-neutral evidence discipline to current research and synthesis.
disable-model-invocation: true
---

# Research evidence core

This is the canonical, harness-neutral research contract. The consuming harness
adds only its routing, acquisition, and closeout surfaces after loading this
skill. Do not substitute a provider, role, or tool for an evidence rule here.

## Evidence discipline

1. Frame the question as two to four independent angles. Each angle MUST have a
   distinct claim, source path, or falsifier; changing only the wording is not
   independence.
2. Acquire the strongest current evidence available. Prefer primary sources:
   official documentation, specifications, source repositories, release notes,
   direct measurements, and first-party records. Treat search snippets and
   summaries as discovery pointers, never as evidence.
3. Read the source behind each consequential claim and capture the exact
   supporting passage, stable URL or repository path, source publication date
   when available, and retrieval date. Never fabricate a citation.
4. Triangulate consequential, comparative, and fast-changing claims across
   independent source types or publishers. Record convergence and preserve
   conflicts instead of choosing the convenient result.
5. Keep the result's layers separate:
   - **Observed fact:** directly measured or read in the local/live surface.
   - **Source claim:** what a cited source states.
   - **Inference:** reasoning that connects facts or source claims; label it.
   - **Recommendation:** an action chosen from the evidence and its constraints.
6. Date every fact likely to rot, including availability, pricing, versions,
   benchmarks, policies, and other current-state claims. Use both publication
   and retrieval dates when they differ.
7. Keep a rejected-evidence record. Name sources or results that were stale,
   secondary, partial, inaccessible, conflicting, or too weak, and state why
   each was rejected or limited. Do not hide a source-coverage gap.
8. State residual uncertainty explicitly: unresolved conflicts, unverified
   assumptions, missing primary evidence, and the cheapest next probe. Absence
   of a search result is not evidence of absence.

## Evidence-shaped output

Return the answer in a form a later reviewer can audit:

- direct answer or bounded conclusion;
- findings with inline citations and exact passages for consequential claims;
- fact/source/inference/recommendation labels where the layer could be confused;
- publication and retrieval dates for volatile claims;
- accepted evidence and rejected or conflicting evidence;
- coverage gaps, residual uncertainty, and the next uncertainty-reducing probe.
