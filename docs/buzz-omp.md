# Buzz OMP adapter

The Buzz OMP adapter starts one isolated OMP ACP runtime for each compiled OMP recipe. Each recipe fixes the instructions, skills, MCP servers, primary model, fallback models, and reasoning levels.

The reusable recipe compiler and runtime preparation use `omp.recipe.v1`. Buzz adds only the ACP transport policy.

## Files

- `bin/omp_recipe.py`: recipe schema, compiler, and runtime preparation.
- `bin/buzz_omp.py`: thin Buzz ACP adapter.
- `bin/buzz-omp`: command wrapper.
- `bin/install-buzz-omp`: local installer.
- `tests/test_omp_recipe.py`: recipe compiler and runtime tests.
- `tests/test_buzz_omp.py`: ACP adapter tests.

## Recipe

A recipe uses schema `omp.recipe.v1`.

```json
{
  "schemaVersion": "omp.recipe.v1",
  "instructions": "instructions.md",
  "models": [
    {
      "provider": "openrouter",
      "model": "openai/gpt-5.6-luna",
      "reasoning": "high"
    },
    {
      "provider": "openrouter",
      "model": "anthropic/claude-sonnet-5",
      "reasoning": "high"
    }
  ],
  "skills": [
    {
      "name": "alpha-sigil",
      "path": "skills/alpha-sigil"
    }
  ],
  "mcpServers": [
    {
      "name": "powder",
      "url": "http://127.0.0.1:8105/mcp"
    }
  ]
}
```

The first model is the primary model. Later entries form the ordered fallback chain. Providers are not restricted to OpenRouter. The current runtime supplies the Mint placeholder configuration when a recipe selects OpenRouter; other provider names use OMP's provider configuration.

Paths are relative to the recipe file's directory. `instructions` names one file. Each skill `path` names a complete directory whose root contains `SKILL.md`; the compiler packages every nested file and directory. It rejects path traversal, symbolic links at any depth, duplicate skill names, duplicate skill source paths, duplicate model entries, unknown keys, and malformed MCP entries.

## Compile and install

```sh
bin/install-buzz-omp
buzz-omp compile /path/to/recipe.json ~/.local/share/buzz-omp/bundles/omp-alpha
```

Compilation stages and validates the complete recipe before replacing an existing output. It replaces only outputs marked as owned by `omp.recipe.v1`, refuses unrelated directories, and leaves the previous compiled recipe intact after any validation or copy failure. Successful recompilation preserves only the allowlisted OMP session/history state.

## Connect Buzz

Set `BUZZ_OMP_BUNDLE` to one compiled bundle. Start `buzz-acp` with the installed adapter and an explicit empty agent argument string.

```sh
export BUZZ_OMP_BUNDLE="$HOME/.local/share/buzz-omp/bundles/omp-alpha"
buzz-acp \
  --agent-command "$HOME/.local/bin/buzz-omp" \
  --agent-args "" \
  --channels CHANNEL_UUID \
  --subscribe all
```

`buzz-acp` defaults `--agent-args` to `acp`. The explicit empty value is required because `buzz-omp` uses the bundle from `BUZZ_OMP_BUNDLE`.

Buzz identity keys must remain in the Buzz-managed credential store. Do not put a private key in a manifest, repository file, shell profile, fixture, or log. The current Buzz CLI requires a signing key for workflow mutations. A production integration needs a safe signing path that does not export the key to an agent process.

## Workflow examples

A schedule can dispatch a channel message:

```yaml
name: OMP Alpha schedule
trigger:
  on: schedule
  interval: 60s
steps:
  - id: dispatch_alpha
    action: send_message
    text: '@OmpAlpha Run the assigned check and report the result.'
```

A webhook can dispatch the same agent:

```yaml
name: OMP Alpha webhook
trigger:
  on: webhook
steps:
  - id: dispatch_alpha
    action: send_message
    text: '@OmpAlpha Run the assigned webhook check and report the result.'
```

Use `buzz workflows create --channel CHANNEL_UUID --yaml FILE` through an approved Buzz signing surface. Use `buzz workflows trigger --workflow WORKFLOW_UUID --inputs '{"source":"prototype"}'` for a webhook trigger.

The prototype created and accepted a webhook run on the hosted Misty Step relay. The relay also returned sustained HTTP 429 responses during repeated tests. Therefore, the workflow acceptance proves registration and trigger intake, but not reliable hosted delivery under rate pressure.

## Isolation rules

The adapter enforces these boundaries:

- It replaces the ACP client `cwd` and `mcpServers` on `session/new`, `session/load`, `session/resume`, and `session/fork`.
- It runs OMP with `--no-extensions` and disables project, user, Claude, Codex, and OpenCode discovery.
- It rebuilds the runtime discovery tree from compiled recipe inputs on every launch, while retaining only known session/history state.
- It exposes only the assigned primary model and thinking level through ACP configuration options.
- It rejects unassigned model and thinking values on every session lifecycle request and configuration change before OMP receives them.
- It does not pass host proxy credential variables to OMP.
- It rejects symbolic links in recipe inputs, compiled output, runtime directories, and packaged skill descendants.
- It preserves non-session ACP NDJSON byte-for-byte.

The recipe runtime accepts its workspace cwd as a separate caller-supplied argument. Buzz supplies a stable, isolated `runtime/cwd` and clears it before each launch. OMP state lives in `runtime/agent`; each launch atomically rebuilds that discovery directory from the compiled instructions and complete skill directories while retaining the allowlisted session/history files.

## Verify

Run the focused contract suite:

```sh
python3 -m unittest tests/test_omp_recipe.py tests/test_buzz_omp.py
python3 -m py_compile bin/omp_recipe.py bin/buzz_omp.py
sh -n bin/buzz-omp bin/install-buzz-omp
```

Run a direct ACP smoke test against a compiled bundle. Verify the response marker, tool list, model option list, and MCP result.

The prototype used two bundles:

- `~/.local/share/buzz-omp/bundles/omp-alpha`: Alpha skill, Powder MCP, Luna primary model.
- `~/.local/share/buzz-omp/bundles/omp-beta`: Beta skill, no MCP server, Sonnet primary model.

The direct ACP proof showed that Alpha could read only the Alpha marker and call Powder. Beta could read only the Beta marker and had no MCP server. A saved Alpha session loaded after an adapter restart and retained its marker.
