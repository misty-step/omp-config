# Buzz OMP adapter

The Buzz OMP adapter starts one isolated OMP ACP runtime for each compiled agent bundle. Each bundle fixes the agent instructions, skills, MCP servers, primary model, fallback models, and reasoning levels.

This is a working prototype. It does not define the final Roster composition format.

## Files

- `bin/buzz_omp.py`: bundle compiler and ACP proxy.
- `bin/buzz-omp`: command wrapper.
- `bin/install-buzz-omp`: local installer.
- `tests/test_buzz_omp.py`: contract and isolation tests.

## Bundle manifest

A manifest uses schema `buzz-omp.bundle.v1`.

```json
{
  "schemaVersion": "buzz-omp.bundle.v1",
  "agent": {
    "name": "omp-alpha",
    "displayName": "OmpAlpha"
  },
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
  "agentsMd": "AGENTS.md",
  "skills": [
    {
      "name": "alpha-sigil",
      "path": "skills/alpha-sigil/SKILL.md"
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

The first model is the primary model. Later entries form the ordered fallback chain. Version 1 accepts only the `openrouter` provider because it uses the Mint OpenRouter proxy route.

Paths are relative to the manifest directory. The compiler rejects path traversal, symbolic links, duplicate skill names, duplicate skill source paths, duplicate model entries, unknown keys, and malformed MCP entries.

## Compile and install

```sh
bin/install-buzz-omp
buzz-omp compile /path/to/manifest.json ~/.local/share/buzz-omp/bundles/omp-alpha
```

The compiler copies the selected files into an immutable bundle shape. The runtime refreshes its copies from that bundle at each launch.

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
- It exposes only the assigned primary model and thinking level through ACP configuration options.
- It rejects unassigned model and thinking selections before OMP receives them.
- It does not pass host proxy credential variables to OMP.
- It rejects symbolic links in the bundle source, bundle output, runtime directories, and runtime files.
- It preserves non-session ACP NDJSON byte-for-byte.

Each bundle has a stable `runtime/agent` directory. OMP stores session state there. Each process launch clears `runtime/home` and `runtime/cwd`, then restores the assigned instructions, skills, model configuration, and MCP configuration. This preserves ACP sessions while it removes workspace and home-directory drift.

## Verify

Run the focused contract suite:

```sh
python3 -m unittest tests/test_buzz_omp.py
python3 -m py_compile bin/buzz_omp.py
sh -n bin/buzz-omp bin/install-buzz-omp
```

Run a direct ACP smoke test against a compiled bundle. Verify the response marker, tool list, model option list, and MCP result.

The prototype used two bundles:

- `~/.local/share/buzz-omp/bundles/omp-alpha`: Alpha skill, Powder MCP, Luna primary model.
- `~/.local/share/buzz-omp/bundles/omp-beta`: Beta skill, no MCP server, Sonnet primary model.

The direct ACP proof showed that Alpha could read only the Alpha marker and call Powder. Beta could read only the Beta marker and had no MCP server. A saved Alpha session loaded after an adapter restart and retained its marker.
