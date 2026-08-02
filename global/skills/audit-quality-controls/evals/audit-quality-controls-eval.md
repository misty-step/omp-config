# Audit quality controls eval

Evaluate against three temporary repositories containing different languages
and deliberately planted control gaps. At minimum plant an unwired checked-in
hook, fail-open secret scanner, mutable CI action pin, missing test gate, and
local/CI command drift.

The run passes only when the skill reports every planted gap with file evidence,
classifies every control-surface row, records effective rather than declared
hooks, respects the 2/5-second and 60/120-second budgets, recommends no
irrelevant tool, and leaves each repository byte-for-byte and status identical.
Compare against a no-skill baseline using the same fixtures and oracle.
