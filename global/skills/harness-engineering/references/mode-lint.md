# /harness-engineering lint

Validate a skill against quality gates.

## Quality gates

| Gate | Check | Fix |
|------|-------|-----|
| **Invocation choice** | Is model invocation explicitly enabled by trigger language or disabled with `disable-model-invocation: true`? | Make the branch deliberate; hand-only skills do not advertise autonomous triggers. |
| **Description branches** | Does each distinct use case have one concrete trigger phrase and one shared leading word with the body? | Remove synonym piles and body identity; add only the phrases that distinguish branches. |
| **Trigger alias** | Does description include `Trigger:` aliases where model invocation is enabled? | Add the actual slash commands; `roster check` enforces frontmatter shape. |
| **Clean category** | Does the skill own one clear judgment category? | Split or compose instead of letting one skill straddle unrelated workflows. |
| **Information hierarchy** | Do always-needed instructions precede branch-gated references, with strong context pointers? | Move universal intent/oracle into the body; disclose details only where the branch needs them. |
| **Size/no-op** | Does every inline sentence change behavior, and is the body roughly under 900 words? | Delete no-ops first; extract branch detail to `references/`. |
| **Gotchas** | Does it name only bespoke failure modes the model would otherwise miss? | Delete generic SWE advice; pair each trap with the target behavior. |
| **Judgment test** | Does it encode judgment the model lacks? | If not, delete the skill. |
| **Oracle** | Can a falsifiable result prove the skill helped? | Add success criteria or route to `/skill-eval`. |
| **Folder utility** | Would a script, reference, example, template, asset, or eval prevent repeated reconstruction? | Put that reusable mechanism under the skill folder. |
| **Railroading check** | Does it over-prescribe steps when the situation should choose the path? | Replace micromanagement with intent, boundaries, oracles, and stop rules. |
| **Freshness** | Do instructions match current model capabilities? | Strip non-load-bearing scaffold |
| **Mode bloat** | >4 modes with inline content, or any single mode >60 lines inline? | Extract mode content to references/mode-*.md; use router pattern (see /diagnose) |
| **Reference integrity** | Do all referenced local files in routing tables, gotchas, and examples exist? | Create the missing file, fix the path, or delete the stale reference |
| **Self-containment** | Do scripts source only paths under `primitives/skills/<name>/`? Do they resolve `SCRIPT_DIR` via `readlink -f` and `STATE_ROOT` from the invoking project? | Move shared libs into the skill tree; rewrite source paths to use `$SCRIPT_DIR/lib/…`; decouple state root from script dir. |
| **Delegation guidance** | Where a skill delegates, does it point at the Shared Operating Spine instead of restating it? | Point to `../../../shared/AGENTS.md` (Act); delete restated doctrine. |

## Self-containment check

The skill must survive being symlinked into a foreign project. Two greps
catch most violations:

```bash
# Scripts that source files outside their own skill tree
rg -n 'source.*\$REPO_ROOT|source.*/scripts/lib/' primitives/skills/*/scripts/

# Scripts that walk up past primitives/skills/<name>/ via $SCRIPT_DIR/../..
rg -n 'SCRIPT_DIR/\.\./\.\.' primitives/skills/*/scripts/
```

Either match is a lint failure. The fix is structural, not a suppression.

Every scripted skill should also ship a distribution smoke test at
`primitives/skills/<name>/scripts/distribution_test.sh` that symlinks the skill into
a throwaway project and verifies `--help` works from there.

## Batch lint

Run on all skills: `for s in primitives/skills/*/SKILL.md; do /harness-engineering lint "$s"; done`

For duplicate skills, long descriptions, unused candidates, and prompt-budget
pressure, use harness-native invocation logs, the registry, and the
first-party route graph; lint checks one skill's shape, not catalog tax.

For skill-design upgrades across the catalog, load
`references/skill-design-principles.md` and apply the gates there before
changing the skill surface.
