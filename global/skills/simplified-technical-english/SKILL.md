---
disable-model-invocation: true
name: simplified-technical-english
description: Apply ASD-STE100 writing rules to explicitly requested text.
---

# Simplified Technical English (ASD-STE100)

Apply these ASD-STE100 writing rules to the text named by the operator.

## Writing rules

### Sentences
- Use a maximum of 20 words in an instruction (procedural sentence).
- Use a maximum of 25 words in a description (descriptive sentence).
- Give one instruction in one sentence. Two actions in one sentence are
  permitted only when they occur at the same time.
- Do not omit words to make a sentence shorter ("telegraphic style").
  Keep articles ("the", "a") and verbs.

### Verbs
- Use the active voice. Make the agent of the action the subject.
- Use the imperative for instructions: "Run the build."
- Use only these tenses: past simple, present simple, future simple.
- Do not use the verb "to be" plus a past participle as a passive
  instruction: write "Remove the file", not "The file should be removed".
- Do not use "-ing" forms of verbs as nouns or adjectives when a simpler
  structure is available.

### Words
- Use one approved meaning for each word. Example: "follow" means only
  "come after", not "obey".
- Prefer these approved verbs: start, stop, do, make, use, show, remove,
  install, set, get, apply, examine, make sure, find, keep, give.
- Do not use idioms, metaphors, humor-dependent phrasing, or decorative
  language in technical statements.
- Do not use different words for the same thing. Choose one term and
  keep it.
- Do not use clusters of more than three nouns. Break the cluster with
  a preposition: "the calibration of the sensor circuit", not "the
  sensor circuit calibration procedure record".

### Paragraphs
- Give each paragraph one topic. Start with the topic sentence.
- Use a maximum of six sentences in one paragraph.
- Do not write one-sentence paragraphs more than necessary.

### Warnings, cautions, notes
- Put the command first: "WARNING: Do not touch the terminal before you
  disconnect the power."
- A note gives information, not a command.

## Boundaries

- Verbatim material is exempt: code identifiers, commands, quoted
  output, error text, mathematics, file paths, citations, and proper
  names. Do not change them.
- Tables, lists, and headings follow the word rules but not the
  sentence-length rules.
- Internal reasoning and subagent briefs are not operator-facing.
  Clarity there outranks STE compliance.
- When the exact STE dictionary word is unknown, use the simplest
  common word with one clear meaning.

## Quick self-check before you send

1. Is each sentence at or under the length limit?
2. Is each instruction imperative and active?
3. Does each word keep one meaning through the text?
4. Are there noun clusters of four or more nouns? Break them.
5. Are there idioms or metaphors? Remove them.
