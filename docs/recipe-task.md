# Recipe task

`recipe_task` is a temporary OMP extension for running one task in a fresh process prepared from a compiled `omp.recipe.v1` bundle. It uses OMP RPC. It does not use ACP, replace native `task`, or claim Task feature parity.

## Surfaces

- `bin/omp_recipe.py` owns recipe validation, compilation, runtime preparation, and the machine launch descriptor.
- `global/lib/recipe-task-runner.ts` owns the shared RPC process runner and nested `recipe_task` host tool.
- `global/extensions/recipe-task.ts` registers the OMP extension tool named `recipe_task`.
- `bin/recipe-task.ts` is the thin command-line client for the same runner.
- `bin/install-recipe-task` installs the command-line client and its runtime sources.
- `tests/recipe-task-runner.test.ts` and `tests/fixtures/recipe-task/` cover fresh roots, environment replacement, steering, cancellation, nesting, and recipe isolation.

## Install

Project the extension and runner into the OMP agent directory:

```sh
bin/install
```

Install the optional command-line client:

```sh
bin/install-recipe-task
```

The CLI defaults to `~/.local/bin/recipe-task`. Its sources default to `${XDG_DATA_HOME:-$HOME/.local/share}/omp-recipe-task`.

## OMP source selection

The replacement-environment option is provided by the local upstream `RpcClient`, not by the currently installed OMP client library. The runner defaults `OMP_RECIPE_OMP_SOURCE` to `~/Development/oh-my-pi` and derives these source paths:

```text
packages/coding-agent/src/modes/rpc/rpc-client.ts
packages/coding-agent/src/cli.ts
```

Each path can be selected independently:

```sh
export OMP_RECIPE_RPC_CLIENT_MODULE="$HOME/Development/oh-my-pi/packages/coding-agent/src/modes/rpc/rpc-client.ts"
export OMP_RECIPE_CLI_PATH="$HOME/.bun/bin/omp"
```

Using the local source `RpcClient` with the installed CLI is valid: process environment replacement happens in the client before it starts the CLI. A source CLI checkout must contain its generated runtime assets. Other controls are:

```text
OMP_RECIPE_OMP_SOURCE
OMP_RECIPE_RPC_CLIENT_MODULE
OMP_RECIPE_CLI_PATH
OMP_RECIPE_COMPILER
OMP_RECIPE_PYTHON
```

## Machine preparation boundary

The runner calls one machine-only command. `--runtime-root` is required, so this path cannot accidentally use Buzz's stable runtime:

```sh
python3 bin/omp_recipe.py prepare-runtime \
  --bundle /absolute/compiled-recipe \
  --cwd /absolute/caller-workspace \
  --runtime-root /absolute/nonexistent-runtime-root
```

Successful stdout is one `omp.recipe.launch.v1` JSON object. It contains the canonical bundle and caller cwd, fresh runtime/config/home/session paths, the primary model, and the compiler's allowlisted environment. The command rejects a relative or pre-existing runtime root.

Calling `prepare_runtime(bundle, cwd)` without `runtime_root` retains the existing stable `bundle/runtime` behavior. Buzz uses that default for restart persistence. `recipe_task` always supplies a new UUID runtime root.

## Environment boundary

The compiler copies only these optional parent keys into the descriptor:

```text
PATH TMPDIR LANG LC_ALL TERM SSL_CERT_FILE SSL_CERT_DIR NO_PROXY
```

It then sets isolated `HOME`, XDG, Codex, Claude, OMP agent, and OMP config values. The runner passes that exact descriptor to public `RpcClient` with `envMode: "replace"`. Ambient credentials and caller-only markers are not merged into a recipe process.

## Extension and nesting

The extension wire input is exactly:

```json
{"recipe":"path/to/compiled-bundle","task":"work to perform"}
```

A relative recipe path resolves against the active session cwd. The cwd is also passed separately to the compiler and the child process. Progress events stream through the tool update callback. The extension maps its abort signal to `handle.stop()`.

Every recipe process receives one explicit host custom tool named `recipe_task`. A nested call starts another fresh RPC process as a sibling under the runner host, with its own config and session roots. The host custom-tool list contains only `recipe_task`; it does not copy custom primitives from the parent process. The nested recipe controls its own instructions and skills.

The extension never registers `task`. Native OMP `task` remains a separate built-in tool.

## Shared runner and CLI

The programmatic handle exposes three operations:

```ts
const handle = await startRecipeTask({ recipe, task, cwd, signal, onEvent });
await handle.send("steering update");
const result = await handle.wait();
await handle.stop();
```

`send` uses RPC steering. `wait` returns the final assistant text and the fresh runtime/session paths after the child is reaped. `stop` sends RPC abort when the child is ready and then waits for process-tree shutdown. Cancellation during startup still forces process-tree shutdown.

Run a compiled bundle from the CLI:

```sh
recipe-task ./compiled-recipe "perform the requested task"
```

The CLI streams assistant and tool progress. `SIGINT` and `SIGTERM` stop and reap the child.

## Deliberate parity gaps

This temporary tool does not provide a typed output schema, Task agent discovery or composition, Task lifecycle/HUB integration, background handles, persisted parent-child transcript lineage, or Task output-contract enforcement. It returns final text only. These are named gaps, not implied compatibility.
