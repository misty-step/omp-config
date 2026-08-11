# Misty Step Factory Fleet Integration Standard

This standard applies to active `misty-step` organization projects.
This repo owns the routing doctrine.
Product repos own their actual Canary, Powder, and Landmark integration surfaces.

## Required Evidence

Add a Powder representation to every active project:

- Forbid repository-local ticket and Kanban ledgers.
  Put Misty Step work in Powder under the full repo label, such as
  `misty-step/canary`. Put R90 work in Habitat.
- Give a repo without an existing Powder card a seed card titled
  `Adopt Canary, Powder, and Landmark factory stack`.
- Import or mirror open GitHub issues as Powder cards.
  Then agents can find durable work without searching GitHub alone.

Give runtime projects Canary evidence:

- Set a stable Canary service name.
  If it differs from the repo name, record the mapping in
  `.canary/integration.json`.
- Expose or identify one production health URL for each HTTP runtime.
  Add live Canary target readback.
- Use Canary check-in monitors for worker, scheduler, CLI, or event-plane
  runtimes.
- Report application error paths to Canary, or add an explicit gap card in
  Powder. External error tracking alone is not enough for Factory operation.

Give release-managed projects Landmark evidence:

- Keep Landmark in manifest-only or synthesis-only mode for repos with release
  tooling or an existing release surface, unless the Landmark fleet plan
  recommends full release ownership.
- Start a repo without release automation with a `.landmark.yml` manifest and a
  backfill-first plan. Do not add release mutation before an operator approves
  the initial version/tag policy.
- When `fleet plan` reports missing secret metadata, do not add a broken
  workflow. Track the secret gap in Powder.
  Use manifest-only adoption until the secret policy is fixed.

## Service Names

Use the Canary service name from live readback.
Do not guess it from the repo path:

| Repo | Canary service |
|---|---|
| `misty-step/brainrot` | `brainrot-publishing-house` |
| `misty-step/chrondle` | `chrondle` |
| `misty-step/linejam` | `linejam` |
| `misty-step/scry` | `memory-engine-api` |
| `misty-step/misty-step` | `misty-step` |
| `misty-step/powder` | `powder` |
| `misty-step/sploot` | `sploot-web` |
| `misty-step/vibe-machine` | `vibe-machine` |

## Verification Commands

Run these commands from local checkouts.
For credentialed API calls, use the Mint broker with a value-free placeholder:

```sh
canary integrate status /path/to/repo \
  --service <canary-service> \
  --production-url <health-url> \
  --json

canary errors <canary-service> \
  --window 1h --json

landmark setup \
  --repo-root /path/to/repo \
  --dry-run --error-format json

curl -fsS -H "Authorization: Bearer __mint.powder.default__" \
  "http://mint.tail5f5eb4.ts.net:4949/proxy/https/${POWDER_API_HOST}/api/v1/cards?repo=misty-step%2F<repo>&limit=100"
```

Set `$POWDER_API_HOST` to the canonical deployed host.
Public doctrine names the provider host, not one operator's host.
Use the Mint route for every credentialed request.

## Waivers

Allow a waiver only when the project is not an active runtime or release
surface. Store the waiver in a Powder card or repo file.
State why Canary uptime, health, or error logging does not apply.
State where work state lives in Powder.
State how Landmark release intelligence is deferred or not applicable.

Do not call a project integrated because it has one of the three surfaces.
Call it integrated only when all applicable surfaces are present and queryable.
