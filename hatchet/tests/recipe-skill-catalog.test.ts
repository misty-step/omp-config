import { readdir, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

// hatchet/tests -> hatchet -> repo root, mirroring runner.test.ts's
// "../../bin" convention for reaching checkout-root paths from this dir.
const repoRoot = fileURLToPath(new URL("../..", import.meta.url));

interface RecipeManifest {
  instructions: string;
  skills: Array<{ name: string; path: string }>;
  taskSkills: Array<{ name: string; path: string }>;
}

async function loadManifest(recipeJsonPath: string): Promise<RecipeManifest> {
  return JSON.parse(await readFile(recipeJsonPath, "utf8")) as RecipeManifest;
}

// Extracts the lens names from the adversarial-review stage prompt's fixed
// catalog: bullet lines shaped `- \`<name>\` — <description>` inside the
// "Pick a critic bench ... fixed catalog below" block. Scoped to that one
// block (not every backtick token in the file) so unrelated code spans like
// `` `hatchet_terminal` `` or `` `git rev-parse HEAD` `` never get mistaken
// for a lens name.
function extractCatalogLensNames(instructions: string): string[] {
  const blockStart = instructions.indexOf("fixed catalog below");
  if (blockStart === -1) throw new Error("adversarial-review.md no longer names a fixed catalog block");
  const nextStep = instructions.indexOf("\n3.", blockStart);
  const block = nextStep === -1 ? instructions.slice(blockStart) : instructions.slice(blockStart, nextStep);
  const names = [...block.matchAll(/^\s*-\s+`([a-z0-9][a-z0-9-]*)`\s+—/gm)].map(match => match[1]!);
  if (names.length === 0) throw new Error("adversarial-review.md's fixed catalog block named no lenses");
  return names;
}

describe("recipe taskSkills stay in sync with what's actually loadable", () => {
  it("adversarial_review's catalog names only lenses declared in its taskSkills", async () => {
    const manifest = await loadManifest(`${repoRoot}/hatchet-adversarial-review.recipe.json`);
    const instructions = await readFile(`${repoRoot}/${manifest.instructions}`, "utf8");
    const catalogNames = extractCatalogLensNames(instructions);
    const declaredTaskSkillNames = new Set(manifest.taskSkills.map(skill => skill.name));
    for (const lens of catalogNames) {
      expect(declaredTaskSkillNames, `catalog lens "${lens}" must be declared in taskSkills`).toContain(lens);
    }
  });

  it("every hatchet-*.recipe.json taskSkills entry resolves to a real SKILL.md on disk", async () => {
    const rootEntries = await readdir(repoRoot);
    const recipeJsonNames = rootEntries.filter(name => /^hatchet-.*\.recipe\.json$/.test(name));
    expect(recipeJsonNames.length).toBeGreaterThan(0);
    for (const recipeJsonName of recipeJsonNames) {
      const recipeJsonPath = `${repoRoot}/${recipeJsonName}`;
      const manifest = await loadManifest(recipeJsonPath);
      for (const taskSkill of manifest.taskSkills) {
        const skillFile = `${repoRoot}/${taskSkill.path}/SKILL.md`;
        await expect(
          readFile(skillFile, "utf8"),
          `${recipeJsonPath}: taskSkills entry "${taskSkill.name}" (${taskSkill.path}) has no SKILL.md on disk`,
        ).resolves.toEqual(expect.any(String));
      }
    }
  });
});
