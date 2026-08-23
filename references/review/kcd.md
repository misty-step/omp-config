# Kent C. Dodds

Tests defend intent and behavior.

Flag tests that assert source text, call counts, private helpers, mocks of
the unit under test, or incidental defaults. Prefer the real boundary. A
test must fail on a plausible defect.

Readability of the contract matters more than coverage counts. If a
maintainer cannot tell what is guaranteed, the test is wrong even if it
passes.
