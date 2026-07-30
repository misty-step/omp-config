---
name: roadmap
description: Grill the operator, then create or update and open a concise project ROADMAP.html.
disable-model-invocation: true
argument-hint: "[project|path]"
---

# /roadmap

Create or update root `ROADMAP.html` as the human project planning surface.
Keep vision, roadmap, and work authority separate.

## Boundaries

- Keep `VISION.md` as the durable direction source when that file exists.
- Keep `ROADMAP.html` as a concise view of outcomes, sequence, questions, research, and proof.
- Keep tasks, claims, attempts, relations, and proof records in the repository work ledger.
- Keep five to twelve strategic items in the roadmap.
- Keep exactly one item current.
- Keep ticket detail out of the roadmap.
- Open the local artifact after each successful create or update operation.
- Publish the artifact only when the operator asks.

## Procedure

### 1. Ground the project

Find the repository root and active workspace.
Read the current `ROADMAP.html` when it exists.
Read root `VISION.md` when it exists.
Read only the repository sources that can settle project facts or authority.
Resolve factual questions with tools before you question the operator.

Complete this step when you can state the current vision, roadmap, work authority, and relevant source files.

### 2. Grill the decisions

Read `skill://grilling` before you question the operator.
Batch every open decision about the vision and immediate roadmap.
Cover purpose, target state, human role, measures, current item, sequence, proof, research, exclusions, and work authority.
Give one recommended answer and one short reason for each question.
Absorb free-form dictation, remove settled questions, and batch the remaining questions again.
State the full shared understanding after no question remains open.
Get explicit operator confirmation before you change the artifact.

Complete this step only when the operator confirms the full shared understanding.

### 3. Shape the roadmap

Read `references/artifact-contract.md`.
Convert the confirmed understanding into the required data shape.
Preserve existing item identifiers when their outcomes remain the same.
Map every supplied concern to one roadmap item or one explicit exclusion.
Write outcomes instead of implementation tasks.
Write one observable proof condition for each item.
Write one next decision and one bounded research need for each item.

Complete this step when the data satisfies every content rule in the artifact contract.

### 4. Update the artifact

Write the confirmed data to a temporary JSON file outside the repository.
Set the final update date in that data.
Run `scripts/render_roadmap.py <data-file> <repository-root>/ROADMAP.html` from this skill directory.
The renderer creates a missing artifact or updates the existing data block.
Preserve the existing layout unless the operator confirmed a layout change.
Remove the temporary JSON file after the renderer succeeds.

Complete this step when root `ROADMAP.html` contains the full confirmed data and no template marker.

### 5. Prove and open the artifact

Read `skill://simplified-technical-english`.
Apply its rules to all visible artifact prose.
Run `scripts/validate_roadmap.py <repository-root>/ROADMAP.html` from this skill directory.
Resolve each validator error before you run the repository gate.
Run the repository gate.
Open the absolute `file://` URL in the browser.
Check the desktop view and the mobile view.
Check the filter and expansion controls.
Check for JavaScript errors and horizontal overflow.
Keep the browser open for the operator.

Complete this step when the gate passes and the browser shows the current artifact without a failed check.

## Completion Gate

Report the artifact path, vision changes, roadmap item changes, deferred decisions, exclusions, gate result, and browser evidence.
End with the current item and its next question.

## Gotchas

- A backlog dump hides strategy. Keep task state in the work ledger.
- A second vision source creates drift. Summarize and link `VISION.md` when it exists.
- A fresh identifier breaks history. Preserve an identifier until its outcome ends.
- A large artifact defeats the human surface. Keep details behind item expansion controls.
- A silent update loses operator intent. Require confirmed shared understanding before every write.
