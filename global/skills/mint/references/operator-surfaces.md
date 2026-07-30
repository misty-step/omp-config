# mint — operator surfaces (not the agent call path)

Agents always make vendor calls through the HTTP proxy in `SKILL.md`.
These surfaces let operators run and inspect the broker.

## Operator CLI

```sh
mint serve                # start the broker
mint policy check <file>  # validate a policy YAML file, report rule count or the exact error
mint audit tail [-n N]    # print the last N audit events, oldest first (default 20)
mint alias list           # list declared aliases and descriptions — never values
```

## MCP (shipped — read-only inspection only)

`mint-mcp` is a stdio MCP server. It exposes **read-only** verbs for operator
inspection: `alias_list`, `policy_check`, `audit_tail`, and `mint_usage`
(returns the proxy contract, so the server is self-documenting). It **never**
exposes a tool that resolves or returns a secret value; that would defeat the
broker's premise. Agents making vendor calls always use the HTTP proxy, not an
MCP tool. Registered in global/mcp.json with status: available. Run it locally
with `cargo run -q -p mint-mcp` in the mint repo.
