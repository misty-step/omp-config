# UI Evidence

Use real-surface media for every observable UI change.

## Select the media

- Static appearance or responsive layout: use before and after screenshots.
- Interaction, transition, loading, focus, resize, animation, or other temporal
  state: use a short video.
- Accessibility behavior: add keyboard interaction evidence and the applicable
  accessibility-tree or diagnostic result.

A new surface does not require a false baseline. Set `baselineRequired: false`
unless the claim compares the new surface with an earlier state.

## Prepare

Use an isolated application state and sanitized fixture. Set the same viewport,
fixture, account state, and starting route for comparative captures.

Assert the start state before recording. Wait for observed UI states. Do not use
arbitrary delays.

## Capture

Record only the changed path. Keep a video short. Show the triggering action and
the resulting state.

For a temporal claim, retain the driver assertions or event log with the video.
Create a contact sheet when the recording tool supports it.

For a screenshot comparison, keep the viewport and crop equal. Capture all
responsive widths named by the claim.

## Inspect

Open the saved artifact. Confirm that the changed state is legible and that the
capture contains no credentials, personal data, unrelated tabs, notifications,
or operator state.

Set `sanitized: true` and `inspected: true` only after this inspection.
