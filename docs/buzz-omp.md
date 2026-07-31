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
  "taskSkills": [],
  "mcpServers": [
    {
      "name": "powder",
      "url": "http://127.0.0.1:8105/mcp"
    }
  ]
}
```

The first model is the primary model. Later entries form the ordered fallback chain. Providers are not restricted to OpenRouter. When a recipe selects OpenRouter, the runtime renders the official upstream URL and non-secret `__OPENROUTER_API_KEY__` sentinel; an operator-configured Agent Vault service rule replaces `Authorization` only when OMP runs inside an Agent Vault wrapper. Other provider names use OMP's generic provider configuration. This harness adds no Agent Vault skill or MCP.

Paths are relative to the recipe file's directory. `instructions` names one file. Each skill or task-skill `path` names a complete directory whose root contains `SKILL.md`; the compiler packages every nested file and directory. It rejects path traversal, symbolic links at any depth, hard-linked regular files at any depth, duplicate skill names, duplicate skill source paths, duplicate model entries, unknown keys, and malformed MCP entries.

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

- It rejects any top-level JSON-RPC batch array (`[...]`) in either direction with a JSON-RPC error (`-32600 Invalid Request`, `id: null`) instead of forwarding or filtering it element-by-element; the ACP transport here is one JSON object per line, and a batch is not a supported shape.
- It reconstructs `session/new`, `session/load`, `session/resume`, and `session/fork` params from an explicit per-method allowlist (`cwd`, `mcpServers`, `sessionId` where applicable, `model`, `thinking`) and drops every other client-supplied key, rather than mutating a client-controlled dict in place. `cwd` and `mcpServers` are always overwritten with the bundle's own values.
- It runs OMP with `--no-extensions` and disables project, user, Claude, Codex, and OpenCode discovery.
- It rebuilds the runtime discovery tree from compiled recipe inputs on every launch, while retaining only known session/history state.
- It exposes only the assigned primary model and thinking level through ACP configuration options.
- It rejects unassigned model and thinking values on every session lifecycle request and configuration change before OMP receives them.
- `session/set_config_option` is deny-by-default: only `configId` values of `model` and `thinking` are ever allowed; any other `configId` (for example `mode`) is rejected without inspecting its value.
- It does not pass host proxy credential variables to OMP.
- It rejects symbolic links in recipe inputs, compiled output, runtime directories, and packaged skill descendants.
- It rejects hard-linked regular files (`st_nlink > 1`) inside recipe source trees, so a file linked in from outside the tree cannot be compiled into a bundle under a second name.
- It preserves non-session ACP NDJSON byte-for-byte.

The recipe runtime accepts its workspace cwd as a separate caller-supplied argument. Buzz supplies a stable, isolated `runtime/cwd` and clears it before each launch. OMP state lives in `runtime/agent`; each launch atomically rebuilds that discovery directory from the compiled instructions and complete skill directories while retaining the allowlisted session/history files.

## Verify

Run the focused contract suite:

```sh
python3 -m unittest tests/test_omp_recipe.py tests/test_buzz_omp.py
python3 -m py_compile bin/omp_recipe.py bin/buzz_omp.py
sh -n bin/buzz-omp bin/install-buzz-omp
```

`tests/test_buzz_omp.py` covers the proxy's isolation boundary directly, including batch-array rejection in both directions, the session-param allowlist (and that extra client-supplied keys such as `env`, `configPath`, and `agentDir` are dropped), the `session/set_config_option` deny-by-default policy, and hard-link rejection in `bin/omp_recipe.py`. Run `python3 -m unittest tests/test_buzz_omp.py -v` to see each case by name.

Run a direct ACP smoke test against a compiled bundle. Verify the response marker, tool list, model option list, and MCP result.

The prototype used two bundles:

- `~/.local/share/buzz-omp/bundles/omp-alpha`: Alpha skill, Powder MCP, Luna primary model.
- `~/.local/share/buzz-omp/bundles/omp-beta`: Beta skill, no MCP server, Sonnet primary model.

The direct ACP proof showed that Alpha could read only the Alpha marker and call Powder. Beta could read only the Beta marker and had no MCP server. A saved Alpha session loaded after an adapter restart and retained its marker.
