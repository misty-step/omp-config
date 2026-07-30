---
name: simplified-technical-english
description: Audit or rewrite operator, agent, prompt, tool, and technical prose with ASD-STE100 language and action-first structure.
---

# Simplified Technical English

Use this skill to write, audit, or revise natural-language communication.
The universal rules in `RULES.md` apply even when a model does not invoke this skill.

## Scope

Use this skill for these communication surfaces:

- operator replies;
- agent and subagent briefs;
- handoffs and findings;
- status updates and comments;
- prompts and tool descriptions;
- issue, pull-request, and work-ledger text.

Use it for root agents, declared agents, temporary agents, subagents, and nested
subagents.

## Meaning first

Understand the required meaning before you write or revise the text.
Preserve every fact, condition, number, scope limit, safety requirement, and
uncertainty statement.
Do not shorten text when the shorter form removes necessary meaning.

Use one term for one concept.
Define a necessary domain term once, then keep that term.

## ASD-STE100 language rules

### Sentences

- Use a maximum of 20 words in an instruction.
- Use a maximum of 25 words in a description.
- Give one instruction in one sentence.
- Write one fact, decision, action, reason, risk, or evidence item in each sentence.
- Do not omit articles, subjects, or verbs to make a sentence shorter.

### Verbs

- Use active voice. Make the actor the subject.
- Use the imperative for instructions.
- Use simple present, simple past, or simple future tense.
- Do not use the verb "to be" plus a past participle in an instruction.
- Do not use an "-ing" form when a simpler form gives the same meaning.

### Words

- Use one clear meaning for each word.
- Use one part of speech for each word.
- Use plain, common words.
- Use one term for one concept. Do not rotate synonyms.
- Do not use idioms, metaphors, jokes, or decorative language.
- Do not use a cluster of more than three nouns.

### Paragraphs

- Give each paragraph one topic.
- Start each paragraph with its point.
- Use a maximum of six sentences in one paragraph.

## Action-first structure

- Start with the answer, required action, or observed result.
- Do not use a preamble.
- Number multi-step procedures.
- Put one bounded action in each step.
- Keep one active subject.
- Put unrelated information under a separate optional heading.
- State errors as cause, evidence, and repair.
- Show completed work with concrete proof.
- Restate each decision, current state, and required next action.
- Make each reply sufficient without conversation recall.
- Split long lists into named groups that preserve priority and completeness.
- End with the result or one required next action.
- Do not add a recap, invitation, or closing pleasantry.

## Warnings, cautions, and notes

- Put the command first in a warning or caution.
- Keep the condition and consequence with the command.
- Use a note only for information.

## Output contracts and verbatim text

Exempt verbatim text, code, commands, paths, identifiers, citations,
mathematics, schemas, and required machine-readable fields.

If an output contract conflicts with these style rules, preserve the contract.
Apply these rules to all free text in that output.

## Rewrite audit

When the operator requests an explicit rewrite audit:

1. Identify each rule violation.
2. Preserve the original meaning.
3. Rewrite only the text that violates a rule.
4. Show the original and revised text.
5. Name each required term or condition that you did not simplify.

If the input follows the rules, say so and do not force a change.

## Pre-send gate

1. Read only the first line. It must give the answer, action, or result.
2. Read only the last line. It must give the result or required next action.
3. Remove each sentence that adds no fact, decision, action, reason, risk, or evidence.
4. Check sentence length, active voice, stable terms, list grouping, and noun clusters.
5. Check that the revision preserves every required fact and condition.

## Sources

- ASD Simplified Technical English Maintenance Group,
  [ASD-STE100 Issue 9](https://www.asd-ste100.org/), January 2025.
- Dustin Yuchen Teng,
  [asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill), MIT.
- ayghri,
  [i-have-adhd](https://github.com/ayghri/i-have-adhd), MIT.
