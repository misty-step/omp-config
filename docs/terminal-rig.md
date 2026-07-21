# Terminal rig

This document records the durable terminal design and its repository authority.
The rig runs against stock OMP APIs. It does not patch the OMP package.

## Principles

- **Open, not boxed.** Keep the composer borderless. Use a padded, low-contrast input surface. Use whitespace to separate the prompt from the transcript.
- **Use ink and surface for hierarchy.** Make input the brightest element. Keep status metadata muted. Use interpunct separators, not powerline pills.
- **Keep the signal visible.** Use the live prompt marker for session accent, bash/python mode, thinking level, and focus state.
- **Degrade right to left.** Drop cost, context, Git, folder, and effort in that order. Keep provider/model identity.
- **Use semantic theme tokens.** Extensions name tokens. Themes own colors. Use userMessageBg for the input surface and one blank padding row above and below.

## Current layout

    <- 2 blank lines: transcript separation
    <- themed panel padding (userMessageBg)
    ❯ input text                        <- prompt gutter
    <- themed panel padding (userMessageBg)

      provider/model · effort · folder ·  git *n           ctx 42% · $cost
    <- 1 trailing blank line
    ^ 2-col indent aligns status under input text

- **Left group:** Show provider/model, non-off thinking level, folder, branch, and dirty count.
- **Right group:** Show context percentage and cost. Warn at 70 percent. Escalate at 90 percent.
- **Palette:** Keep identity and meters near-monochrome. Reserve color for the prompt marker, dirty count, context escalation, and cost.
- **Separator:** Use the interpunct separator from statusLineSep. Keep a minimum three-column gap before the right group.

## Repository surfaces

|Surface|Authority|Purpose|
|---|---|---|
|global/extensions/promptspace.ts|~/.omp/agent/extensions/promptspace.ts|Prompt spacing, the bare prompt marker, the padded input panel, and the status line.|
|global/extensions/agent-hub.ts|~/.omp/agent/extensions/agent-hub.ts|Read-only /agent-hub overlay with the subagent roster and live activity.|
|global/themes/*.json|~/.omp/agent/themes/|Theme library. Kanagawa is the active dark theme. Kanagawa Lotus is the active light theme.|
|global/presets/*.yml|~/.omp/agent/presets/|Launch overlays for lean, design, operations, and research work.|
|global/config.yml|~/.omp/agent/config.yml|The promptspace settings contract, including plain chrome, custom empty status segments, and active themes.|
|bin/install|Installation driver|Projects declared source surfaces and verifies links and digests.|

bin/install creates the live links. It may back up conflicting authority targets. It does not copy runtime state into this repository.

The extensions directory is co-tenanted. herdr-omp-agent-state.ts remains a real, Herdr-managed file at ~/.omp/agent/extensions/herdr-omp-agent-state.ts. Its header states that Herdr overwrites it during integration updates. The provenance contract records this cotenant with owner herdr. The two OMP extension files are separate file links. The installed audit rejects every other extension entry. This prevents an invisible writer from entering the projected home. It also prevents Herdr from writing into the repository and prevents Git operations from rolling back the integration.

The Herdr file was adopted as a runtime cotenant on 2026-07-21. It was not copied into this repository.

## Stock API boundaries

- Silence the built-in status line with statusLine.preset: custom and empty segment lists. Plain chrome otherwise mounts two status lines.
- Do not show rate-limit windows. The extension API does not expose the provider OAuth usage windows.
- Read the active theme through ctx.ui.theme. Do not import a second theme graph.
- Read ctx.ui.theme on every render. Do not capture a theme during session_start.
- Call setBorderVisible(false) on replacement editors.
- Keep Agent Hub extension-only. Use public lifecycle, progress, and agent-discovery channels. Do not patch core OMP payloads.

## Work map

- Change status content, order, colors, or drop priority in global/extensions/promptspace.ts (statusLine()).
- Change spacing, the prompt marker, or the input panel in PromptspaceEditor.render().
- Inspect subagents with /agent-hub. Keep the ambient Subagents HUD compact.
- Change colors in global/themes/*.json. Do not hardcode ANSI colors in extensions.
- Restart OMP after extension edits. Theme JSON edits may hot-reload. /reload does not remount the editor from session_start.

## Decision log

- **2026-07-16:** Keep this as a standalone terminal rig. Do not fold it into the public aesthetic web design system. Use stock OMP APIs. Keep live authority in repository surfaces projected by bin/install.
- **2026-07-16:** Use pure air. Remove full-width rules. Add two rows above the input and one row around status. Use near-monochrome identity with signals for dirty count, context, cost, and the prompt marker.
- **2026-07-16:** Show only the current folder. Use ctx N% · $cost on the right. Remove clock and session title. Use a cross-background model token for legibility.
- **2026-07-16:** Use userMessageBg for the input panel. Add one vertical padding row above and below it. Do not add borders or rules.
- **2026-07-16:** Read the live theme during each render. Theme changes must update the panel and status line without an editor remount.
- **2026-07-18:** Show routing identity next to the model as provider/model. Read provider identity from the active model object.
- **2026-07-18:** Degrade cost, context, Git, folder, and effort first. Keep routing identity last.
- **2026-07-18:** Add the read-only /agent-hub overlay. Use split panes at normal widths and a stacked layout below 90 columns.
- **2026-07-21:** Keep Herdr's integration file outside repository authority. Record extensions/herdr-omp-agent-state.ts as a runtime cotenant owned by Herdr.

## Backlog

- Rate-limit meter after upstream API exposure.
- Git ahead/behind arrows.
- Streaming state cue.
- Adaptive vertical air at tight terminal heights.
- Queued-message indicator.
- Contrast audit on real dark and light terminal backgrounds.
- Tool-call chrome opinion through the stock extension API.
- Multi-line input affordance.
