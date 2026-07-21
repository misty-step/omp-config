---
disable-model-invocation: true
name: yew-draft-persistence
description: Fix composer/input draft loss on remount in Yew WASM apps by persisting to localStorage and keying the component by entity id
---

# Yew draft/input persistence

Use when a Yew (0.21) WASM app loses in-progress text from a controlled input/textarea — symptoms like "my text got blown away with a loading message."

## Root cause
Component-local `use_state` for a draft dies on ANY remount: page reload, iOS PWA suspend/restore, residual service-worker `client.navigate`, or route change. The accompanying "loading…" message is the same remount reinitializing fetch state to `Loading` — a symptom, not the cause. Do NOT chase the loading flash as the data-loss fix; a re-render with an unchanged controlled `value` prop does not rewrite the DOM value in Yew.

## Reproduce first
Prove the vulnerability: type into the field, navigate to another route and back, assert the value is now empty. If it is, drafts are component-local and lossy on unmount.

## Fix (all four)
1. **localStorage, keyed by entity id** — NOT sessionStorage (doesn't survive WebKit/PWA termination). Helpers: `load(id)`, `save(id, val)`, `clear(id)`. Hydrate via `use_state(|| load(&entity_id))`; call `save` inside `oninput`; call `clear` only on confirmed send success.
2. **Key the component by entity id** — `<View key={id} id={id} />` so A→B remounts synchronously and `use_state` re-runs its initializer for B immediately. Do NOT use a post-render `use_effect_with(id)` to reload the draft — it leaves a one-frame wrong-entity race where a fast send dispatches A's text to B.
3. **Send safety** — disable the field while `sending`; retain the draft until the API resolves; clear persisted text only on `Ok`. On `Err`, nothing was discarded and nothing needs restoring.
4. **Loading flash (separate UX)** — in the fetch effect, skip `state.set(Loading)` when `matches!(*state, Ready(_))` (keying guarantees Ready belongs to the current entity); on fetch error, only set Error if currently Loading/Error so a transient failure doesn't clobber a good transcript.

## Check for other remount triggers
Any kill-switch `sw.js` that calls `client.navigate(client.url)` on activate is a forced reload — a remount trigger. Unregister without navigating; a worker with no fetch handler lets open clients shed control on their next natural navigation.

## Cargo
`web-sys` needs the `Storage` feature to call `window().local_storage()`.

## Verify live
Type → reload → assert value survives; type in A → go to B → assert B has its own draft and A's persisted value is untouched; assert `loading` stays false during SSE traffic but shows correctly on a genuine first load. Confirm `sha256` of the on-disk WASM equals what the bridge actually serves (a `KELPIE_STATIC`/cwd mismatch or stale module cache mimics "the fix didn't take").
