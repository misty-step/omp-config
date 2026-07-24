import type { CardFacts, StageName } from "./contracts.js";

// The card's own words, rendered into whatever stage recipe the runner is
// about to spawn. Previously every stage replayed one static operator
// string; this is the seam that lets `recipes/*.md` reference the card that
// actually triggered the run instead of a frozen prompt from a merged job.
export type RecipeContext = {
  card: CardFacts;
  stage: StageName;
  round: number;
  headSha: string;
  task: string;
};

const noAcceptanceCriteria = "- (no acceptance criteria on the card)";

function renderCriteria(criteria: readonly string[]): string {
  if (criteria.length === 0) return noAcceptanceCriteria;
  return criteria.map((item) => `- ${item}`).join("\n");
}

function placeholderValues(context: RecipeContext): Readonly<Record<string, string>> {
  return {
    "card.title": context.card.title,
    "card.body": context.card.body,
    "card.criteria": renderCriteria(context.card.criteria),
    "card.priority": context.card.priority ?? "unspecified",
    stage: context.stage,
    round: String(context.round),
    head_sha: context.headSha,
    task: context.task,
  };
}

// Only ASCII identifier characters (plus `.`) are ever a valid placeholder
// name, so this pattern can never accidentally swallow markdown the card
// body legitimately contains (e.g. a literal `{{` the card author typed).
const placeholderPattern = /\{\{([A-Za-z0-9_.]+)\}\}/g;

// Deterministic, total, and single-pass: every placeholder in `template` is
// replaced from `context` exactly once, in the order it appears, and
// substituted values are never re-scanned for further placeholders (a card
// body containing the literal text `{{stage}}` must survive verbatim in the
// output, not be expanded again). A stage prompt that quietly drops the
// card is worse than a crash, so this throws rather than emitting blanks:
// an unrecognized `{{name}}` names itself in the error, and any `{{`/`}}`
// left over in the template's own literal text (an unmatched delimiter, or
// one with invalid characters) is also a thrown error. Only the template's
// own literal spans are checked for leftover delimiters — text that came
// from a substituted value is opaque and never inspected a second time.
export function renderRecipe(template: string, context: RecipeContext): string {
  const values = placeholderValues(context);
  let rendered = "";
  let literalOnly = "";
  let cursor = 0;
  let match: RegExpExecArray | null;
  placeholderPattern.lastIndex = 0;
  while ((match = placeholderPattern.exec(template)) !== null) {
    const literal = template.slice(cursor, match.index);
    literalOnly += literal;
    rendered += literal;
    const name = match[1];
    if (name === undefined) {
      throw new Error(`recipe template has an unmatched {{ or }} delimiter: ${match[0]}`);
    }
    const value = values[name];
    if (value === undefined) {
      throw new Error(`unknown recipe placeholder: {{${name}}}`);
    }
    rendered += value;
    cursor = match.index + match[0].length;
  }
  const tail = template.slice(cursor);
  literalOnly += tail;
  rendered += tail;

  if (literalOnly.includes("{{") || literalOnly.includes("}}")) {
    throw new Error("recipe template has an unmatched {{ or }} delimiter");
  }
  return rendered;
}
