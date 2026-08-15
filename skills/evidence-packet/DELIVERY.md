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

Use the repository-approved attachment interface. Images and videos normally
use the repository's private or public attachment store. Do not copy private
evidence to another host.

If no approved upload interface is available, report the local artifact path and
an evidence delivery gap. Do not invent a durable URL. Do not place a local path
in a PR as if a reviewer can open it.

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

## Finish without a PR

Give the inspected local artifact paths and checks. State that the files are not
published and cannot be opened by a remote reviewer.

Always include an `Evidence gaps` section when a gap exists. Name each unproved
claim and the strongest substitute.
