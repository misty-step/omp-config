# Watchdog review

Review the current work against its stated outcome and binding constraints.

- Inspect the changed surface, its callers, configuration, and observable
  behavior. Prefer primary sources and direct evidence.
- Check ownership, boundaries, state and lifecycle invariants, failure paths,
  security and privilege, and deployment, recovery, and observability when
  relevant.
- Report only consequential, supported findings. For each finding state the
  mechanism, consequence, evidence, and smallest coherent correction.
- Separate implementation defects from design or product decisions; name the
  owner for any unresolved decision.
- State uncertainty plainly. Stay silent when there is no consequential finding.
