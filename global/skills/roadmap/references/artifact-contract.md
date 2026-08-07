# Roadmap artifact contract

Use this contract when you create or update `ROADMAP.html`.

## Authority

- `VISION.md` owns durable direction when the repository has that file.
- `ROADMAP.html` owns the human view of strategic sequence and open decisions.
- The repository work ledger owns tasks, claims, attempts, relations, and proof.
- Link these surfaces. Do not copy detailed work state into the roadmap.

## File

- Keep one self-contained root `ROADMAP.html` file.
- Use inline CSS, JavaScript, and JSON.
- Make no external network request.
- Support direct use through a `file://` URL.
- Use `templates/ROADMAP.html` when no artifact exists.
- Replace `__ROADMAP_DATA__` with the final JSON data.
- Leave no template marker in the final artifact.
- Preserve the existing layout during a normal content update.

## Content

- State one clear purpose and one target state.
- State the human role and the main system rule.
- Include three to six outcome measures.
- Include five to twelve strategic roadmap items.
- Keep exactly one item in the `current` horizon.
- Use `next`, `later`, or `explore` for all other items.
- Preserve stable item identifiers across updates.
- Use an outcome, not an implementation task, as each item title.
- Give each item observable proof.
- Give each item one next question.
- Give each item one bounded research need.
- Map each supplied concern to one item coverage list.
- Record an explicit exclusion when a supplied concern does not belong.
- Keep ticket state and attempt history out of the artifact.

## Data

Put one JSON object in the `roadmap-data` script element.
Use this shape:

```json
{
  "schemaVersion": 1,
  "project": "Project name",
  "updated": "YYYY-MM-DD",
  "visionSource": "VISION.md or inline",
  "vision": {
    "purpose": "One sentence.",
    "target": "One sentence.",
    "humanRole": "One sentence.",
    "systemRule": "One sentence."
  },
  "measures": [
    {"name": "Measure name", "description": "Observable measure"}
  ],
  "workAuthority": {
    "name": "Work ledger name",
    "description": "What this system owns"
  },
  "items": [
    {
      "id": "R01",
      "horizon": "current",
      "title": "Outcome title",
      "outcome": "One outcome sentence.",
      "proof": "One proof sentence.",
      "question": "One decision question?",
      "research": "One bounded research need.",
      "coverage": ["Input concern"]
    }
  ],
  "exclusions": []
}
```

## Validation

Check all conditions before you open the file:

1. Parse the JSON data block.
2. Confirm that the template marker does not remain.
3. Confirm that item identifiers are unique.
4. Confirm that five to twelve items exist.
5. Confirm that exactly one item is current.
6. Confirm that every item has each required field.
7. Confirm that each supplied concern appears once or has an exclusion.
8. Check all visible prose with `skill://comms`.
9. Open the file at desktop and mobile widths.
10. Check content, filters, expansion controls, JavaScript errors, and horizontal overflow.
