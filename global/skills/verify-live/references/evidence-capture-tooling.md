# Evidence capture tooling (this machine)

Machine-specific mechanics for capturing window screen evidence with `evcap`.
The universal capture doctrine lives in
`global/references/verification-system-first.md`. This file holds the local
toolchain facts. Read it on demand.

## Tool

`evcap` is installed at `~/.local/bin/evcap`. Run `evcap doctor` first. It
reports each dependency and the X display state.

## Display facts

Pop!_OS 24.04 runs COSMIC (smithay) on Wayland with rootless XWayland on `:1`,
PipeWire, and no passwordless sudo. COSMIC exposes the
`ext-image-copy-capture-v1` protocol family, not `zwlr_screencopy`.
`grim`, `slurp`, `wf-recorder`, and `wayshot` do not work here. Rootless
XWayland means a root window grab shows a black frame. Target one window id.

## Choose a surface

| Need | Command | Consent |
|---|---|---|
| App video or stills | `evcap rec/shot -w <id|title>` | no |
| Whole Wayland desktop still | `evcap shot --desktop` | no |
| Whole Wayland desktop video | `evcap rec --portal` | yes, human must click Share |

Prefer the window-targeted path. It is unattended and deterministic. The
desktop never leaks into reviewer artifacts.

## Throttling trap

Chromium and Electron mark a window on `:1` as occluded and throttle
rendering. Captures then look correct but stay frozen. Launch the app with:

```bash
app $(evcap launch-flags --shell)
```

Verify motion with frames, not by eye:

```bash
evcap frames out.mp4 --at 0.3 1.8 3.4 -o frames/
md5sum frames/*.png
```

Identical hashes mean you captured a frozen window.

## Typical run

```bash
evcap windows                                     # find the target
evcap rec -w "Time Tracker" -s 12 -o out/flow.mp4 # record the flow
evcap frames out/flow.mp4 --at 1 5 10 -o out/     # pull key moments
evcap gif out/flow.mp4 -o out/flow.gif --width 900
evcap pack out --title "TI-123" --claim "One sentence the artifacts prove."
```

`pack` writes `index.md` with the size and sha256 of every artifact.

## Electron specifics

Electron needs the same anti-throttle flags. A dev build whose main bundle
points at a Vite dev server renders blank if the server is down. Start the
renderer first. Check the port the bundle expects. Native modal dialogs are
separate top-level windows. List windows again once the dialog is open, and
capture it by its own id.

## Toolchain

Installed under `~/.local/` without root: ffmpeg and ffprobe (BtbN static
build), ImageMagick AppImage, `pipewiresrc` extracted from the distro deb,
and `cosmic-screenshot`. To add an apt package without root, use
`apt-get download` plus `dpkg -x` into `~/.local/opt`. Synthetic Wayland
input needs root. Use `python3-Xlib` XTEST for X windows, or drive the app
through its own automation.
