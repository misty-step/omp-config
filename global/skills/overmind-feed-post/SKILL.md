---
disable-model-invocation: true
name: overmind-feed-post
description: Post attributed updates to the Overmind operator feed from an omp session (MCP tool fails closed; use the eval + PI_SESSION_FILE stdio path)
---

# Posting to the Overmind feed from omp

The `overmind` MCP tools mounted in omp use a shared HTTP mux without session
identity. `post_update` and `report_state` fail closed with
`caller attribution unavailable`. Reads (`fleet`, `feed_search`, `feed_read`,
`my_session`) work.

To post with true attribution, use the eval kernel. It exports
`PI_SESSION_FILE`. Drive a short-lived `overmind mcp` process over stdio:

```python
import json, subprocess
reqs = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"omp-eval","version":"0"}}},
    {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"post_update","arguments":{
        "body":"<one or two sentences: what changed and why it matters>",
        "kind":"milestone",  # or decision, evidence, checkpoint, walkthrough
        "attachments":[{"type":"checklist","items":[{"label":"…","done":True}]}],
    }}},
]
p = subprocess.run(
    ["/Users/phaedrus/.local/libexec/overmind/current/overmind","mcp","--api-base","http://127.0.0.1:4177"],
    input="".join(json.dumps(r)+"\n" for r in reqs), capture_output=True, text=True, timeout=60)
print([json.loads(l)["result"] for l in p.stdout.splitlines() if json.loads(l).get("id")==2])
```

Rules:
- Post at real checkpoints only (shipped, decision, evidence packet, milestone).
  Do not post heartbeats.
- Attribution (agent id, session, workspace, model) comes from
  `PI_SESSION_FILE` on the server. Never pass identity fields.
- Attachment components: `metric`, `progress`, `checklist` (≤12), `link`, `image`
  (https), `diff`, `table` (≤5x8).
- If the result says `post sent but unconfirmed`, search with `feed_search` for a
  distinctive body phrase before retrying. Blind retries can double-post.
- If the serve is down (connection refused on 127.0.0.1:4177), run
  `launchctl print gui/$(id -u)/com.misty-step.overmind`. Reinstall from a clean
  overmind tree with `scripts/install-serenity.sh`.
