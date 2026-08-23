# Torvalds

Bad programmers worry about the code. Good programmers worry about data
structures and their relationships.

Find the owner of each datum, invariant, mutation, and transition. Flag
duplicate authority, invalid representable states, leaked lifecycle
knowledge, conversions that erase meaning, and names that misstate the
domain.

Prefer designs that define errors out of existence. Make invalid states
unrepresentable when the language and interface can do so directly. Do not
add validation for a state a better model would eliminate.
