# OMP launch contracts

`omp.launch-contract.v1` compiles one repository-local agent composition into a deterministic, inspectable launch bundle. It is a thin preflight boundary around stock OMP 17.0.7, not a scheduler, workflow engine, daemon, database, or replacement harness.

## What it proves

A successful compile resolves and materializes one exact launch configuration:

- repository instructions plus a digest and file count for the Git-visible repository tree and every `.omp/agents/*.md` declaration, including ignored files;
- primary agent, provider/model selector, and thinking level;
- explicit root tool, skill, MCP-server, subagent, and child-tool allowlists;
- inherited subagent isolation, runtime disabled-agent denylist, and concurrency limit;
- host execution boundary, approval mode, ephemeral session, and wall-clock limit;
- a generated OMP config that disables project MCP discovery and undeclared provider imports;
- file hashes, byte sizes, a canonical manifest, and one deterministic bundle digest.

Compilation fails on duplicate or unresolved composition sources, undeclared repository agents, any discoverable ancestor `.omp/agents` declaration outside the sealed source tree, path escapes, symlinks, environment files, transient build files, unsupported tools, and controls that stock OMP cannot enforce. A child agent's declared tools must fit inside `composition.subagents.tools`; wildcard child tools are rejected. The compiler does not pretend OMP 17.0.7 provides process, network, filesystem, or per-child subagent sandboxes: version 1 accepts only `host` sandbox values and inherited child isolation.

## Contract

The contract uses the JSON subset of YAML so its digest is portable and reviewable.

```json
{
  "schema_version": "omp.launch-contract.v1",
  "name": "compiled-dispatch-proof",
  "repository": {
    "root": "repository",
    "instructions": "CONTRACT.md"
  },
  "composition": {
    "agent": "conductor",
    "profile": null,
    "model": "openai-codex/gpt-5.6-luna",
    "thinking": "low",
    "tools": ["task"],
    "skills": [],
    "mcp_servers": [],
    "subagents": {
      "allowed": ["pico"],
      "tools": ["read"],
      "isolation": "inherit",
      "max_concurrency": 1
    }
  },
  "sandbox": {
    "filesystem": "host",
    "network": "host",
    "process": "host"
  },
  "execution": {
    "mode": "print",
    "session": "ephemeral",
    "max_time_seconds": 60,
    "approval_mode": "yolo"
  }
}
```

Composition sources resolve from repository-local declarations first and the live `omp-config` authority second. More than one matching source is an error; the compiler never silently picks a winner. The generated runtime agent directory contains only selected sources. OMP walks upward for the nearest `.omp/agents` directory, so compilation and `run` reject ancestor agent declarations whenever the contract repository has no local agent directory to shadow them. The repository itself is not copied: `run` recomputes its receipt, re-enumerates the same discoverable agent surface, and refuses tracked/unignored-file drift or any ignored undeclared agent before starting OMP.

## Commands

```bash
python3 bin/launch_contract.py compile path/to/contract.json --out /tmp/my-launch
python3 bin/launch_contract.py verify /tmp/my-launch
python3 bin/launch_contract.py run /tmp/my-launch --prompt 'Perform the bounded task.'
```

The Python entrypoint in `bin/launch_contract.py` dispatches these commands; the implementation lives in focused modules:

- `bin/launch_compile.py`: `resolve_contract` and `compile_bundle`;
- `bin/launch_verify.py`: `verify_bundle`;
- `bin/launch_run.py`: `run_bundle` and auth-broker lifecycle;
- `bin/contract_utils.py`: shared strict JSON and digest primitives.

`run` verifies every bundle receipt, the canonical manifest digest, the current repository receipt, and the nearest project-agent directory before launch. It creates a temporary `PI_CODING_AGENT_DIR`, exposes only the compiled agent configuration, starts or reuses the OMP auth broker without copying credential bytes into the bundle, invokes stock OMP in print/no-session mode, passes the declared timeout to OMP, enforces a parent-side timeout with a ten-second shutdown grace, and removes the temporary runtime directory afterward.

The permanent fixture is `tests/fixtures/launch-contract`. Its live acceptance path is:

```bash
python3 bin/launch_contract.py compile tests/fixtures/launch-contract/contract.json \
  --out /tmp/omp-launch-proof --force
python3 bin/launch_contract.py run /tmp/omp-launch-proof --mode json \
  --prompt 'Use the task tool exactly once with agent pico. Tell pico to read marker.txt and return it exactly. Then print only pico output.'
```

The expected final assistant text is `OMP_COMPOSITION_PROOF_OK`. This proves a clean OMP process loaded the compiled model/root-tool/agent boundary and dispatched the selected project agent, whose `read` tool declaration was checked against the child-tool allowlist. `bin/check` runs the deterministic compiler and negative preflight tests; it does not invoke a paid model.

## Deliberate limits

Version 1 does not guarantee that a model obeys prose, provide a security sandbox, isolate child agents differently from the parent, authorize external effects, or make a workflow durable. It pins the current Git-visible repository byte set and every project-agent declaration by receipt rather than copying a worktree; later source drift requires recompilation. Ignored files outside `.omp/agents` remain outside the receipt because OMP project rules/extensions/MCP discovery are disabled and selected launch sources are copied into the bundle. The child-tool allowlist is enforced at compile time against selected agent declarations, while OMP remains the runtime tool enforcer. Repository revision/worktree lineage, Mint service policy, Issue claims, Bitterblossom recovery, and Crucible verdicts remain separate authority-owned layers. Those systems should consume the launch and repository digests rather than move their policy into this compiler.
