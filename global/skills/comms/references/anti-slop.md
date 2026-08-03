# Anti-slop critic checklist

## Use this file only for critics

Agents follow negative instructions poorly. Do not load this file as a normal
drafting register. Load it when a dedicated critic subagent must hunt violations
in finished text. The critic quotes evidence, names the violated pattern, and
suggests a repair that preserves the target register and required meaning.

Do not flag verbatim text, code, commands, paths, identifiers, citations,
mathematics, schemas, or required machine-readable fields. Do not let this
checklist override a user, system, harness, safety, or output contract.

## Negative-register checks

Check the target text for each pattern from the operator's negative register:

- Antithesis.
- Corrective negation.
- Paragraph pinning.
- Parataxis.
- Summary beats.
- Rhetorical crutches.
- Negative parallelisms.
- Negative anaphoras.
- Contrasting pairs.
- Rule of three.
- Em dashes.
- Throat-clearing openers.
- Landing sentences.
- Setup/payoff constructions.
- Parallel sentence structures within a paragraph.
- Predictable sentence length. The target register may require sentence limits.
- Stacked noun phrases.
- Filler intensifiers, including “genuinely,” “really,” “truly,” and “actually.”
- Corporate-register verbs, including “leverage,” “underscore,” and “reflect.”
- Nominalization.
- Hedging qualifiers that add no real uncertainty.
- Written phrasing that does not fit the spoken voice when spoken voice is the target.
- Performed enthusiasm.

## Critic report

For each finding, record:

1. The exact quote.
2. The pattern name.
3. The audience and surface.
4. The smallest repair that preserves meaning.
5. Any conflict with the target register or output contract.

If no violation is present, state that the checklist found no violation. Do not
invent a rewrite.

## Source

Adapted from the “quarterly reminder” block in `~/notes.md:99-108`, with the
operator's ruling that dedicated critic subagents must hunt these violations.
