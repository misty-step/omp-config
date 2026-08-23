---
name: polish
description: Loop over one real interaction at a time, making it simpler, then faster.
disable-model-invocation: true
argument-hint: "[surface or interaction]"
---

# Polish

Find one interaction. Make it simpler.
Find one interaction. Make it faster.
Repeat. You are a design engineer.

One interaction per cycle. One move per cycle. Prove every move on the real
surface.

## 1. Pick

Run the named surface; with no argument, run the product's primary surface. If
no surface runs, stop and report the missing start path.

Exercise it as a user: pointer, keyboard, and the failure paths around it.
Pick the one live interaction with the most friction: extra steps, needless
choices, dead time, jank, unclear state.

Completion criterion: One interaction is named with its observed friction.

## 2. Move

Make exactly one move:

- **Simpler** — remove a step, a choice, an element, a state, or a mode. The
  interaction's job survives with less of it.
- **Faster** — cut real or perceived latency: fewer round trips, optimistic
  feedback, instant first paint of the changed state, tighter motion.

Prefer deletion. A move that adds machinery is not polish. A move that changes
the interaction's job is scope; route it to the operator instead.

Completion criterion: One reversible change is implemented and nothing else
moved.

## 3. Prove

Exercise the same interaction on the real surface. Capture before and after
evidence (`skill://evidence-packet`): step counts, timings, or recordings.
Keyboard path, visible focus, contrast, and reduced motion still hold.

Revert a move that fails proof and record the cycle as red.

Completion criterion: The interaction is observably simpler or faster and the
surrounding surface is unchanged.

## 4. Repeat

Return to Pick. Stop when a full pass over the surface yields no supported
move, or the operator's stated budget is spent.

Completion criterion: The stop condition is named and every cycle reports its
interaction, move, and proof.
