# Critic Failure Modes

Use this reference when no narrower skill reference owns the failure modes. Add task-specific modes to the relevant skill reference when one exists.

## General modes

- **Unnamed risk:** Work starts without general and task-specific failure modes.
- **Inline-only avoidance:** Negative instructions stay in a prompt and disappear after the task.
- **Self-approval:** The producer treats confidence, a summary, or a passing local check as independent evidence.
- **Weak critic scope:** A critic repairs, broadens scope, or reviews a different artifact instead of hunting named violations.
- **Unsupported finding:** A critic reports a concern without a location, oracle, reproduction, or other checkable evidence.
- **Additive bias:** The work adds wrappers, abstractions, fallbacks, comments, tests, or process without removing obsolete material.
- **Compensating growth:** A deletion triggers a larger replacement system even though observable behavior stays the same.
- **Protocol duplication:** A new review workflow duplicates an existing routing or review protocol.

## Task-specific prompts

Name only the modes that can affect the current product.

- **Communication:** unsupported claims, missing decisions, buried actions, or ambiguous ownership.
- **Plan:** missing dependencies, unowned steps, absent oracle, or no stop condition.
- **Design:** leaked boundaries, unnecessary concepts, unmeasured tradeoffs, or missing failure behavior.
- **Code:** broken invariants, untested paths, trust-boundary errors, dead scaffolding, or stale callers.
- **Review:** missed changed paths, weak evidence, scope drift, or an unverified finding.

## Erasure angle

Include erasure in every critic brief. Ask: “What can be deleted while preserving observable behavior?”

- Check code, concepts, wrappers, fallbacks, comments, tests, docs, rules, and process steps.
- Measure the applicable before-and-after change with token count or AST node count, or measure it against a line budget.
- Treat the metric as evidence, not as a substitute for behavior proof.
- The primary agent inspects for compensating additions after each deletion and removes them when behavior remains preserved.
- Use `global/references/delete-first.md` for the broader deletion and simplification sequence.

## Iron Forest project orientation (2026-08-08)

- Treat repository prose or old cards as current runtime evidence.
- Omit an installation, organization, repository, daemon, branch, or authority boundary.
- Describe architecture by file layout instead of tracing one Subject through every Flow and durable Effect.
- Report Ledger or backlog totals without naming the query time and historical-format limits.
- Confuse intended design, merged code, enabled configuration, and observed live behavior.
- Call a subsystem elegant because it has strong names while ignoring duplicate state, generated surface, or repair cost.
- Call code cruft without a concrete deletion, line count, retained behavior, and reversal condition.
- Miss the erasure question: what can be deleted while preserving observable behavior?
- Recommend a new service, store, protocol, agent, or abstraction when Git, GitHub, systemd, JSONL, or the Go standard library already holds.
- Bury the operator's next five decisions under a complete inventory.

## Iron Forest operational convergence (2026-08-08)

- Turn every reliability defect into a new subsystem instead of one reconciler over existing durable facts.
- Let agents create dispatchable Tracker items without visible authorship, evidence, acceptance, or Manager validation.
- Give the Manager direct merge, branch, or Run authority when Tracker shaping is sufficient.
- Update a running binary inside a Run and create mixed-version Effects.
- Add UI, MCP, or service protocols before one functional core and CLI expose stable operations.
- Duplicate Subject state across labels, the Ledger, processes, and memory without one derivation rule.
- Treat retries, timeouts, and tests as patches instead of naming the failure state and recovery invariant.
- Add tests that assert source text, mocks, or plumbing instead of observable transitions and plausible failures.
- Add a microservice to reduce file size without an independent failure, authority, scaling, or deployment boundary.
- Make Mint optional by putting secret values in repository configuration or agent declarations.
- Expand documentation beyond a small root contract that has an owner and a verification path.
- Ship to R90 before several Misty Step repositories pass unattended convergence and recovery drills.
- Keep generated artifacts, stale exports, retired compatibility paths, or duplicate cards because deletion feels risky.
- Miss erasure: require a measured net deletion budget for each stabilization epic.

## Iron Forest admission and notes stabilization (2026-08-08)

- Derive different admission identities for Builder items and Verifier or Fixer branches that represent one Subject.
- Acquire a lock before inspecting its prior holder, then mistake the current process for the live predecessor.
- Release a claim by reading the current ref, allowing stale cleanup to delete a successor's claim.
- Promise automatic foreign-Host crash recovery without a lease, coordinator, or observable failure detector.
- Use only a process mutex for Git notes operations that manual runs can execute from another process.
- Defend synthetic same-key calls while missing the real item-to-branch transition that caused the live failure.
- Expand Subject admission to own unrelated notes reconciliation instead of keeping one outcome per card.
- Deploy a new binary before the old daemon drains, producing mixed-version Effects.
- Add more lock helpers and tests than needed; measure net production lines and delete obsolete admission code.

## Olympus simple operational cutover (2026-08-04)

- Do not replace a deleted subsystem with another queue, ledger, receipt, wrapper, or configuration path.
- Do not remove preproduction, combine agent hosts, or weaken exact-revision, authority, credential, budget, drain, or durability gates.
- Keep Habitat auto-selection, owner assignment, cooldown, and daily-cap behavior while removing runtime policy editing.
- Never await Asclepius from the Argus execution path. Route persisted review results through independent reconciliation.
- Dispatch CI repair only for the current open `auto/*` head with a current failed check and trusted repository authority.
- Keep GitHub as pull-request and merge authority. Do not duplicate branch protection or required-check policy in another store.
- Prove every agent on its own Sprite in preproduction before exact-digest production promotion.
- Require a net reduction in lines, modules, tables, jobs, or dependencies. Reject compensating growth.


## Iron Forest independent Agent Flow overhaul (2026-08-09)

- Share one managed worktree across Agents or let one Agent call another Agent.
- Treat invalid Agent content as retryable mechanics, causing repeated Runs without a visible human handoff.
- Let Agent, Check, or repository-controlled Git hooks execute outside the declared Host boundary.
- Mount writable Agent configuration, arbitrary Host paths, or arbitrary Host tools into a Runner.
- Stop all Flows because one malformed durable fact still has a recoverable Issue identity.
- Write the Ledger before the required terminal Effect, then lose the only retry opportunity.
- Merge a tree that differs from the exact Revision that passed Checks and received the Verdict.
- Let a reopened retired Issue or an orphaned local branch create duplicate published work.
- Render a prompt without complete Issue, Revision, changed-path, diff, Checks, or prior-Verdict evidence.
- Lose concurrent edits or fail to bound child output while preserving complete durable trace evidence.
- Erasure failure: add schedulers, stores, recovery modes, or compatibility paths instead of deleting superseded machinery.

## Crucible durable eval ledger (2026-08-10)

- Treat one local SQLite file as shared storage without off-host backup and clean-host restore proof.
- Let direct OMP or Harbor runs bypass the central ledger or write only local report paths.
- Mutate an eval definition after registration while keeping its old identity.
- Count invalid infrastructure attempts as model failures, or omit them from the operational denominator.
- Accept duplicate, partial, stale, or conflicting ingestion without one idempotency and terminal-state rule.
- Finalize an attempt before every declared artifact has a verified content hash and durable link.
- Let requested model, effort, harness, skill, rule, tool, fallback, child, or role identity drift from observed treatment.
- Attribute a multi-axis or post-treatment difference to one component.
- Hide provider fallbacks, retries, children, or role calls inside one named-model treatment.
- Add a second service, statistics layer, or eval registry instead of extending Crucible's SQLite ledger and Git-authored specs.
- Import pilot summaries while leaving failed attempts, transcripts, grader evidence, or cost data outside the durable record.
- Pass only happy-path persistence tests without crash-boundary, duplicate, corrupt-artifact, backup, and restore drills.
- Erasure failure: add abstractions or portfolio machinery before one durable code-repair suite proves the foundation.
- Resolve a whole conflicted file with `ours` or `theirs` and lose independently shipped Harbor behavior.
- Keep both conflict sides and create duplicate lifecycle, policy, hashing, or persistence paths.
- Reuse a review receipt from before conflict resolution or review a tree different from the pushed revision.
- Push the integration before focused, workspace, restore, and live attempt checks pass on the resolved tree.
- Treat an executing event as permanent ownership without a lease, heartbeat, expiry, or crash recovery.
- Trust lexical path containment while following symlinks, or clean up a pathname without proving inode ownership.
- Expose a partial restore target before atomic installation, then make retries reject the interrupted state.
- Claim new provider work before replaying a matching legacy terminal record during a schema upgrade.
- Document one database environment path while new commands require separate explicit flags.
- Let the normalized ledger depend on compatibility projections that the ledger is supposed to author.
- Check only the restored database and artifact targets while stale SQLite journal, WAL, or SHM entries remain.
- Check sidecars through path-following metadata and miss directories, dangling symlinks, or path replacement races.
- Mutate one destination target before preflight validates every database sidecar and artifact conflict.
- Delete or rewrite an existing sidecar or destination target while refusing the restore.
- Duplicate sidecar checks outside the descriptor-relative no-follow boundary that owns restore target validation.
- Test only regular sidecar files and omit unchanged-content proof for files, directories, symlinks, and destination targets.
- Register every Harbor batch task before serial execution, allowing a later queued task to outlive the stale timeout.
- Reconcile a queued task as abandoned while its live native Harbor batch still owns future execution.
- Add a run-level lease that weakens per-task terminal semantics or lets preflight failures start provider work.
- Move registration after provider launch, losing durable evidence for a crash between launch and registration.
- Retry a provider launch after reconciliation changes a queued task to `lost`.
- Test only the first task or an abandoned row, and omit reconciliation during a live serial batch.
- Erasure failure: add another lifecycle state or compatibility wrapper instead of moving registration to the existing claim boundary.
## exe.dev agent skill (2026-08-10)

- Add an MCP server or wrapper CLI even though exe.dev defines SSH as its API.
- Put exe.dev guidance in always-loaded `AGENTS.md` instead of one model-invoked skill.
- Trigger on quoted or comparative mentions, or leave the skill enabled in no-operations presets.
- Vendor the upstream skill without a declared license and immutable registry receipt.
- Treat account authentication as mutation authority or bypass Estate's typed artifact when it owns the action.
- Copy credentials to a VM or allow direct control-plane HTTPS proof outside Mint.
- Accept an unknown host key, forward an SSH agent by default, or select an unintended local identity.
- Invent flags, parse terminal prose, or select a VM without one exact `.vms[].vm_name` match.
- Change a VM, account, integration, support grant, sharing rule, or attachment scope without exact authority.
- Erasure failure: duplicate the remote docs catalog or add configuration, agents, tools, and process beyond the routed skill.

## Iron Forest CLI and status truth repair (2026-08-11)

- Dispatch a command before exact arity validation, allowing a typo to cause work.
- Convert absent, malformed, null, or mismatched trigger state into a known false or zero status.
- Add command-specific parsing branches when one exact arity guard in `runCLI` owns the boundary.
- Erasure failure: keep redundant status fallbacks or duplicate arity helpers after the direct guard works.

## Parallax collector performance dimension (2026-08-11)

- Leave the retired Playwright adapter in the registry, tests, documentation, or another registration path.
- Benchmark setup or trivial parsing instead of a retained collector path that emits observations.
- Declare a benchmark report without creating the file inside the uploaded artifact.
- Use an analyzer identity that does not match the registered Go benchmark adapter.
- Break the reusable workflow JSON-string contract while changing the repository caller workflow.
- Describe an adapter dimension incorrectly or omit a retained adapter from the README table.
- Erasure failure: add benchmark infrastructure or compatibility code instead of deleting the redundant adapter and reusing the existing report contract.
