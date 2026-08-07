# The Application Floor

Operator standing directive (2026-07-05). Every Misty Step application must ship with all items below.
Apply these items in all circumstances.
This is the floor, not the ceiling.
Grooming sessions treat a missing item as a backlog gap.
`/shape` packets for new products include each floor item or name an explicit waiver per item.

## The floor

1. **Marketing site.** Branded, deployed publicly. Misty Step aesthetic via
   the shared site kit, per-repo `DESIGN.md` brand identity, strong pitch,
   real screenshots/GIF walkthroughs, user-facing release notes (Landmark),
   footer link contract (GitHub repo when public, mistystep.io always,
   Weave for weave-family products). Program epic: powder `misty-step-910`;
   kit: `aesthetic-907`. Evidence bar per `/showcase`: no public claim
   without a screenshot, command, or demo path behind it.
2. **The five faces.** Functional core behind one robust API. Required faces
   over that core: **API + CLI + MCP + shipped skill + UI**. Add an SDK only
   when external consumers exist. A face passes only when it covers core verbs.
   Prefer no MCP over a stub MCP — a read-only or incomplete MCP is a gap, not
   a pass. Name a waiver per missing face. Never omit a required face silently.
   (Ratified 2026-07-04; weave-013 matrix epic abandoned — doctrine lives here.)
3. **Documentation.** Let an operator go from the repo to productive use alone.
   Provide a README quickstart, an operator walkthrough for any UI or serve mode, and honest help text.
4. **CI and quality gates.** Run the repo gate in CI and gate the diff.
   Never weaken it to pass (`quality-gates.md`).
5. **Relative infrastructure agnosticism.** Avoid load-bearing coupling to one host.
   Treat Fly/Sanctum/Pages as deploy targets, not architecture.
6. **Deep modularity.** Ousterhout: interfaces far simpler than
   implementations; no shallow pass-throughs or speculative abstraction.
7. **Test coverage approaching 100%, spanning unit, integration, and end-to-end.**
   Use behavior-asserting tests (`verification-system-first.md`), not implementation mirrors.
   For any surface that ships HTML/JS/CSS, "end-to-end" means a real engine executes the artifact.
   Use three mandatory tiers:
   (a) Syntax-validate every embedded or generated artifact in the gate.
       Extract inline scripts and parse them.
       Make templates fail closed on empty interpolation or missing assets.
       Treat each build error as a failure, never a placeholder.
   (b) Smoke-load each major page in a headless browser and assert zero console errors.
   (c) the few golden user paths are exercised behaviorally (click → visible state change) at desktop and ~390px widths.
   Substring assertions against rendered HTML do not cover the code inside it.
   They test the transcript, not the program.
8. **Rust — or the strongest static typing the platform boundary allows.**
   Maximize compile-time correctness guarantees. Every non-Rust surface
   names its constraint.
9. **Frictionless onboarding.** Use one click-to-copy command from zero to fully working wherever possible.
   Include daemons, agents, and indicators that run, not only install.
   When self-hosting is the design, such as Canary, containerize it, document it, and ship agent-ready setup prompts.
   A `doctor` command that fails loudly when the deployment is dead is part of onboarding, not polish.

## Case studies that established this floor

Counterspell, 2026-07-05: The tool existed, was installed, configured, and passed checks.
It still failed for the operator because `setup` installed only the annotation agent.
The annotation agent had no daemon, the installed binary was two days stale, and the menu-bar indicator's host app was not installed.
Three "done" claims provided no live protection.
Floor items 9 and 3 prevent "installed" from meaning "running".
Onboarding ends at verified-live, and doctor is the proof.

Sanctum artifacts, 2026-07-05: one Rust raw-string escaping error (`main.rs`, a `\"` shipped verbatim into inline JS) made the page's script throw a SyntaxError on load.
The star toggle, search, and pagination were dead for every user.
The 84 tests passed because each test matched substrings in rendered HTML and none parsed or executed JavaScript.
Two independent verification lanes confirmed server behavior but missed the page issue.
Both stopped at the layer boundary they owned.
Floor item 7's real-engine tiers exist so that a page that cannot even parse can never again ship green: syntax-gate the embedded artifact, smoke-load for console errors, and click the golden
path in a real browser — one verifier always stands at the user boundary.
