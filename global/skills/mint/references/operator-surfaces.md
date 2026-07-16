# mint — operator surfaces (not the agent call path)

An agent making a vendor call always goes through the HTTP proxy in `SKILL.md`.
The surfaces below are operator-facing: running and inspecting the broker.

## Operator CLI

```sh
mint serve                # start the broker
mint policy check <file>  # validate a policy YAML file, report rule count or the exact error
mint audit tail [-n N]    # print the last N audit events, oldest first (default 20)
mint alias list           # list declared aliases and descriptions — never values
```

## MCP (shipped — read-only inspection only)

`mint-mcp` is a stdio MCP server exposing **read-only** verbs for operator-facing
inspection: `alias_list`, `policy_check`, `audit_tail`, and `mint_usage`
(returns the proxy contract, so the server is self-documenting). It **never**
exposes a tool that resolves or returns a secret value — that would defeat the
broker's premise. Agents making vendor calls always use the HTTP proxy, not an
MCP tool. Registered in `primitives/mcps/registry.yaml` with
`status: available`; run locally with `cargo run -q -p mint-mcp` in the mint
repo.
