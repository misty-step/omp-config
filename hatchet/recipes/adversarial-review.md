# Hatchet adversarial review stage

Review the current HEAD for the `omp-config-tools-wildcard-resolution` card. You are read-only.

1. Confirm the required HEAD and record `git status --porcelain` before review.
2. Inspect the current commit and its focused tests against all card criteria. Look specifically for a second full-tool representation, wildcard compatibility, drift between agent declarations and the built-in registry, a gate that only scans source text, or live Task behavior left unproved.
3. Run only narrow read-only checks needed to validate high-conviction findings. Do not edit, commit, merge, push, format, lint, or run broad suites.
4. Confirm HEAD and worktree status are unchanged.
5. Return exactly one JSON object and no other JSON object. Use outcome `accepted` only when no blocker remains; otherwise use `blocked`. Set `headSha` to the unchanged full HEAD. Put each concrete finding or exact passing command in `artifactRefs`, including `worktree:unchanged`.
