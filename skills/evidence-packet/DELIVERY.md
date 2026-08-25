# Evidence Delivery

The evidence record is the source of truth. Do not maintain a second evidence
list with different claims, scenarios, or artifact identities.

## Check

Before delivery, confirm each artifact against its record:

- the source revision and dirty-state note are accurate;
- the runtime identity is marked observed, inferred, or unavailable;
- the scenario and fixture match the claim;
- the artifact opens and shows the stated observation;
- the artifact contains no secret or unrelated operator data.

Calculate and record an artifact SHA-256 digest when the available interface can
do so. A digest proves file identity. It does not prove the claim or the runtime
revision.

## Deliver to a PR

An observable pull request is incomplete until every required artifact is
reviewer-accessible from the pull request. Upload through the repository-approved
PR attachment interface:

- embed before/after images in the Evidence section;
- attach a short video or GIF for temporal interaction claims;
- attach the evidence record or a downloadable packet bundle;
- keep hashes in the record as identity checks, never as media substitutes.

Local paths are capture locations, not delivery. A hash proves file identity,
not behavior, and does not let a reviewer inspect the artifact. Never present
either as completed PR evidence.

Add one PR section:

```markdown
## Evidence

### Claim
<observable claim>

### Scenario
<fixture, start state, and exact actions>

### Before
<artifact link, observation, source revision, and runtime identity>

### After
<artifact link, observation, source revision, and runtime identity>

### Checks
<commands, results, and state readback>

### Evidence gaps
<exact blocker, attempted capture or delivery, substitute, and unproved claim>
```

Update the existing Evidence section when the change or proof changes. Do not
add duplicate sections.

Before PR delivery completes, open every attachment from the rendered pull
request and confirm that it resolves for a reviewer with repository access,
shows the declared scenario, and matches the recorded digest. Replace local
artifact references in the PR with those openable attachments.

An unavailable or failed attachment interface is a delivery blocker. Preserve
the local packet, record the attempted interface and failure, and stop PR
readiness until an approved route works or the operator explicitly waives that
artifact. An evidence-gap paragraph does not make a local-only packet complete.

## Finish without a PR

Give the inspected local artifact paths and checks. State that the files are not
published and cannot be opened by a remote reviewer.

Always include an `Evidence gaps` section when a gap exists. Name each unproved
claim and the strongest substitute.
