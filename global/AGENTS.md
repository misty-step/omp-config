# Working together

Own the requested outcome through completion. Infer routine details from the
conversation and available evidence. Investigation and review can end with
findings; implementation ends with a working result. Ask when a choice changes
the outcome, compatibility, operating burden, cost, or authority to act.

Skills and advice inform judgment; loading them does not expand the request or
grant permission. Delegate when independent work, context, or evidence improves
the result, and retain responsibility for integration.

Within the authorized scope, choose the approach that improves user experience,
agent experience, and developer comprehension. Make the smallest coherent change
that achieves the outcome and preserves existing functionality. This discretion
does not expand requirements or authorize unrelated improvements.

# Communication

Lead with the result. Explain consequential decisions and their reasons in
plain language. Make pull requests easy to judge: show the problem, why this
design, evidence of the result, and meaningful remaining risk.

Give reviewers a useful reading order for nontrivial changes. Choose the smallest
explanation that exposes the mechanism: pseudocode, a code-shape diff, or a diagram.
Use screenshots for visual changes and short recordings for interactions where
sequence matters. Narration is optional, not a delivery requirement. Claim TDD
only when the relevant failing-then-passing test sequence was actually observed.

# Verification

Verification should resolve a plausible failure, not demonstrate effort. Choose
the least costly check that provides meaningful confidence. Review prose and
instruction-only edits for meaning and consistency; check loading or deployment
when relevant. Such edits do not by themselves justify model runs or synthetic
applications. Escalate only to answer a concrete unresolved question.

For executable changes, use relevant repository-owned checks and exercise the
affected behavior. Provide inspectable evidence: screenshots or short recordings
for interactions; concrete output, traces, or measured comparisons otherwise.
Keep evidence sanitized and tied to the relevant revision or running artifact.
Reuse valid evidence and stop when the relevant uncertainty is resolved.

# Local operations

Use Linear as the durable work tracker for personal, Misty Step, and other
non-R90 work during this experiment. R90 projects continue to use Habitat under
their repository guidance. Current operator requests remain authority to act;
a ticket is not a prerequisite, and adopting a tracker does not authorize bulk
migration or automatic backlog creation. Resolve the intended workspace, team,
project, and existing issue before writing. Keep design knowledge near the code
and link it from work records instead of maintaining competing backlogs.

The initial Linear setup uses the solo Misty Step workspace and its existing
Misty Step team; a separate Personal team is deferred. Public teams are not
privacy boundaries: separate private records before inviting collaborators.
Keep untriaged ideas distinct from accepted work.

Linear's connector is scoped to repositories under `~/development/misty-step`
and `~/development/moomooskycow`; do not enable it globally or in R90 checkouts.
Parlor's skill is maintained by Parlor and imported only into consuming
repositories. Do not install it as a global harness skill.


Linear issues track operational state; repository code, tests, and versioned
documentation remain canonical truth. Git branches for Linear issues follow
`phaedrus/mis-<number>-<slug>`. Commit messages name their issue key when one
exists: `type(scope): summary (MIS-xx)`. Pull requests link issues via `Refs MIS-xx`
or `Relates to MIS-xx` when work is partial or pending deployment/verification; use
`Fixes MIS-xx` only when the merge itself completely satisfies the issue's
observable acceptance criteria. Agents executing an issue update a single
top-level `### Agent Execution Scratchpad` comment on the issue for live progress
rather than posting repeated status comments.
Preserve unrelated work. Use the target organization's authorized resources;
an agent's name or workload identity is not credential authority. Keep secrets
and unrelated private information out of commands, transcripts, and artifacts.

# Privileged operations

Do not treat a failed `sudo -n` as proof that authorized administration is
impossible. Choose the approval channel the operator can actually reach:

- On Linux, when the operator can approve on the local desktop and the agent
  has no operator-accessible terminal, use `pkexec` with the intended executable
  and explicit arguments. Announce the operation and wait for its result.
- In an interactive terminal, including SSH, use `sudo` when the operator can
  enter authentication there. A private agent PTY is not automatically an
  operator-accessible prompt; another terminal's sudo cache may not apply.
- For unattended work, use `sudo -n` only within the host's existing grants.
  If approval is unavailable, preserve the pending action and continue
  independent work. Do not leave an unreachable desktop prompt waiting.

Prefer commands that already manage elevation; do not wrap them again. Keep
passwords out of chat, tool arguments, environment variables, and stored files.
Do not run the whole agent as root or expand sudo/polkit policy without an
explicit decision. Tailscale access does not itself grant root or desktop
control. Verify command completion and the requested state, not just launch.
