---
disable-model-invocation: true
name: mint
description: |
  Use when an agent needs an outbound HTTP call to a vendor API (OpenAI, GitHub,
  Stripe, or any third-party service) and would otherwise need an API key, token,
  or other secret. mint is the fleet's credential broker: route calls through
  its egress proxy with a credential placeholder. Your tailnet identity is the
  auth. Never request, embed, or expect real credential bytes in agent context.
  Trigger phrases: "mint", "credential broker", "egress proxy", "call the API
  through mint", "I need an API key", "OpenRouter key", "secret placeholder",
  "__mint.", "proxy call".
argument-hint: "[proxy|serve|policy-check|audit-tail|alias-list]"
---

# mint

mint is the fleet's agent credential broker. Use this principle: **agents cause
authorized effects; they never possess authority.** Credential bytes never enter
an agent runtime. mint owns *use*, not storage; a backing *secret store* keeps
custody. mint is not a secret store and never hands agents secret values through
any surface.

One execution mode ships: the **egress credential proxy**. Send to mint the
request that you would send directly to the vendor. mint authenticates it, checks
policy/budget/circuit-breaker, and resolves credential placeholders against the
real secret after the request leaves the sandbox. It forwards the call, scrubs
the response, writes an audit event, and returns the result. Read
`references/errors-and-scope.md` for the honest scope of what is and is not built.

## Call mint (the agent path)

You hold NOTHING: no token, no key, and no auth header for mint itself
(mint-924: your identity is your machine's tailnet peer address, resolved
server-side through `tailscale whois`). A header that you send cannot change who
mint identifies you as. Send the exact request that you would send to the vendor
to mint's proxy route. Fold the vendor scheme, host, and path into the URL, and
put a placeholder where the credential would sit:
```
{METHOD} {MINT_BASE_URL}/proxy/{scheme}/{host}/{*rest}
<any forwarded header that would carry a real credential>: ...__mint.<service>.<name>__...
```

Concrete — calling OpenRouter through the `openrouter.default` alias:

```sh
curl -H "$(printf '%s: Bearer %s' Authorization __mint.openrouter.default__)" \
     -X POST "${MINT_BASE_URL:?Set MINT_BASE_URL in the private runtime environment}/proxy/https/openrouter.ai/api/v1/chat/completions" \
     -d '{"model": "...", "messages": [...]}'
```

- **`MINT_BASE_URL`** — Get it from the private runtime environment. Local
  `mint serve` commonly uses `http://127.0.0.1:4949`. Put deployed hostnames in
  operator configuration, not this public skill. A deployed caller must use the
  private network path that preserves its peer identity.
- **`__mint.<service>.<name>__`** goes anywhere a real credential value would sit
  inside a *forwarded header*. mint swaps in the real secret after the request
  leaves your sandbox, so you never hold the value. This placeholder resolves
  from the operator-facing alias `secret://<service>/<name>`.
- **Live placeholders** are policy-gated per caller identity. The selected mint
  deployment's policy and `mint alias list` are the source of truth. Do not copy
  a production alias inventory, caller identities, or deployment topology into a
  public primitive.
- **`X-Mint-Capability`** is dev/loopback-only since mint-924 (`mint serve` smoke).
  It is not the deployed agent path. mint refuses it from anywhere but 127.0.0.1.
- If no placeholder exists for the service you need, ask the operator to declare
  the alias and a matching policy rule. Never fall back to an inline key "just
  this once."

Non-2xx status codes each mean something specific. Read the code; do not retry
blind. Read `references/errors-and-scope.md`. Use the operator CLI and the
read-only MCP face for operator work, not the agent call path:
`references/operator-surfaces.md`.

## Red lines

- Never accept, request, or echo a real credential value. If one reaches your
  context from any source, treat it as a mint-bypass bug. Stop and flag it. Do
  not route around mint to "fix" the call.
- Require `MINT_BASE_URL` from the environment. Never bake a deployed hostname
  into committed code.
- The dev-only capability token (loopback `mint serve`) remains sensitive. Treat
  it as a secret reference. Never log it or paste it into code, commits, or
  reports.

## Verification

In the mint repo, `scripts/mint-probe.sh` defines done. It proves that an
agent-shaped caller never sees the real secret, that the audit log never contains
it, and that a policy-denied call reaches the vendor zero times. Trust that
script and its CI job over this skill's prose if they disagree.
