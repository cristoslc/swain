---
title: "MOTD Textual TUI Animation Fixes"
artifact: SPEC-040
track: implementable
status: Complete
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: enhancement
parent-epic: EPIC-011
linked-artifacts:
  - EPIC-011
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: "github:cristoslc/swain#16"
swain-do: required
---

# MOTD Textual TUI Animation Fixes

## Problem Statement

The Textual TUI MOTD border animation rotates counter-clockwise, which is visually incorrect. Additionally, there is no way for users to change the animation style or disable it entirely — animation style is hardcoded. This was reported in GitHub #16.

## External Behavior

The Textual TUI MOTD panel's border animation:
- Rotates **clockwise** by default (fixes the current counter-clockwise direction)
- Supports selectable animation styles configurable via `swain.settings.json` (e.g., `motd.animationStyle`)
- Supports disabling animation entirely via settings (e.g., `motd.animationStyle: "none"`)

Settings key: `motd.animationStyle` — valid values include at least: `"clockwise"` (default), `"none"`, and optionally additional styles (e.g., `"pulse"`, `"bounce"`). Unknown values fall back to `"clockwise"`.

## Acceptance Criteria

- **Given** the MOTD Textual TUI is running with default settings, **When** the border animation plays, **Then** it rotates clockwise.
- **Given** `motd.animationStyle` is set to `"none"` in settings, **When** the MOTD starts, **Then** no animation plays and the border is static.
- **Given** `motd.animationStyle` is set to a valid non-default style, **When** the MOTD starts, **Then** the animation uses that style.
- **Given** `motd.animationStyle` is set to an unknown value, **When** the MOTD starts, **Then** it falls back to clockwise animation without error.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Default settings → clockwise animation | Braille frames reversed to `["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]`; `ANIMATION_STYLE` defaults to `"clockwise"` | Pass |
| `animationStyle: "none"` → no animation | `_tick_spinner` returns early; `_render_agent` uses static `●` symbol | Pass |
| Valid non-default style → uses that style | `_STYLE_MAP` maps `"dots"` and `"bar"` to their frame sets | Pass |
| Unknown value → clockwise fallback | `FRAMES = _STYLE_MAP.get(ANIMATION_STYLE, SPINNER_STYLES["braille"])` | Pass |

## Scope & Constraints

- Only affects the Textual TUI path — the bash MOTD fallback is out of scope.
- Settings are read from `swain.settings.json` (project) or `~/.config/swain/settings.json` (user override).
- Animation implementation lives in `skills/swain-stage/` (MOTD Textual app).

## Implementation Approach

1. Locate the animation loop in the Textual MOTD app.
2. Reverse the frame sequence (or direction parameter) to achieve clockwise rotation.
3. Add a settings read for `motd.animationStyle` on startup.
4. Branch on the value to select the animation routine (or skip it for `"none"`).
5. Document the setting in `swain.settings.json` schema comments.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | ca755446db4a68c7429812fa6b8f2837856e7050 | Initial creation from EPIC-011 decomposition; linked to GitHub #16 |
| Ready | 2026-03-14 | 51c037cc8fcc36538b69a893865fc63c06b459cb | Approved by operator |
| Complete | 2026-03-14 | ec401e5 | Braille frames reversed to clockwise; animationStyle setting added |
