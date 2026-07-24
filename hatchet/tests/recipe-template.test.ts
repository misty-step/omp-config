import { describe, expect, it } from "vitest";
import type { CardFacts } from "../src/contracts.js";
import { renderRecipe, type RecipeContext } from "../src/recipe-template.js";

const baseCard: CardFacts = {
  title: "Fix the flaky retry loop",
  body: "The retry loop double-counts attempts under load.",
  criteria: ["Attempts are counted exactly once", "Existing retry tests stay green"],
  priority: "P1",
};

function context(overrides: Partial<RecipeContext> = {}): RecipeContext {
  return {
    card: baseCard,
    stage: "implement",
    round: 2,
    headSha: "a".repeat(40),
    task: "run the assigned recipe",
    ...overrides,
  };
}

describe("renderRecipe", () => {
  it("substitutes every supported placeholder", () => {
    const template = [
      "title: {{card.title}}",
      "body: {{card.body}}",
      "criteria:",
      "{{card.criteria}}",
      "priority: {{card.priority}}",
      "stage: {{stage}}",
      "round: {{round}}",
      "head_sha: {{head_sha}}",
      "task: {{task}}",
    ].join("\n");
    const rendered = renderRecipe(template, context());
    expect(rendered).toBe([
      "title: Fix the flaky retry loop",
      "body: The retry loop double-counts attempts under load.",
      "criteria:",
      "- Attempts are counted exactly once\n- Existing retry tests stay green",
      "priority: P1",
      "stage: implement",
      "round: 2",
      `head_sha: ${"a".repeat(40)}`,
      "task: run the assigned recipe",
    ].join("\n"));
  });

  it("renders the empty-criteria line when the card has no acceptance criteria", () => {
    const rendered = renderRecipe("{{card.criteria}}", context({ card: { ...baseCard, criteria: [] } }));
    expect(rendered).toBe("- (no acceptance criteria on the card)");
  });

  it("defaults an absent priority to 'unspecified'", () => {
    const cardWithoutPriority: CardFacts = { ...baseCard, priority: undefined };
    const rendered = renderRecipe("{{card.priority}}", context({ card: cardWithoutPriority }));
    expect(rendered).toBe("unspecified");
  });

  it("throws naming an unknown placeholder instead of emitting a blank", () => {
    expect(() => renderRecipe("{{card.unknown}}", context())).toThrow(
      "unknown recipe placeholder: {{card.unknown}}",
    );
  });

  it("throws on an unmatched opening delimiter left in the template", () => {
    expect(() => renderRecipe("prefix {{card.title", context())).toThrow(
      /unmatched \{\{ or \}\}/,
    );
  });

  it("throws on a stray closing delimiter with no matching opener", () => {
    expect(() => renderRecipe("prefix }} suffix", context())).toThrow(
      /unmatched \{\{ or \}\}/,
    );
  });

  it("does not re-scan substituted text: a card body containing a literal placeholder survives verbatim", () => {
    const cardWithLiteralPlaceholder: CardFacts = {
      ...baseCard,
      body: "Please keep the {{stage}} marker exactly as written.",
    };
    const rendered = renderRecipe(
      "body: {{card.body}}\nstage: {{stage}}",
      context({ card: cardWithLiteralPlaceholder, stage: "remediate" }),
    );
    expect(rendered).toBe("body: Please keep the {{stage}} marker exactly as written.\nstage: remediate");
  });

  it("is deterministic and total across repeated calls with the same input", () => {
    const template = "{{card.title}} / {{stage}} / round {{round}}";
    const first = renderRecipe(template, context());
    const second = renderRecipe(template, context());
    expect(first).toBe(second);
    expect(first).toBe("Fix the flaky retry loop / implement / round 2");
  });

  it("renders templates with no placeholders unchanged", () => {
    const template = "no placeholders here at all\njust plain instructions.\n";
    expect(renderRecipe(template, context())).toBe(template);
  });
});
