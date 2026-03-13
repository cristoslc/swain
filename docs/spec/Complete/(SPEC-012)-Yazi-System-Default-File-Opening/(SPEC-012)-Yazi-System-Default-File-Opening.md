---
title: "Yazi System Default File Opening"
artifact: SPEC-012
status: Complete
type: bug
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic:
addresses: []
evidence-pool: ""
source-issue: "github:cristoslc/swain#15"
swain-do: required
linked-artifacts: []
depends-on-artifacts: []
---

# Yazi System Default File Opening

## Problem Statement

swain-stage sets `XDG_CONFIG_HOME` to its own references directory when launching yazi, and the environment inherits `EDITOR=micro` (the resolved swain editor). This causes all file opens in yazi to launch micro, even for non-text files like PDFs and images that should open with the system default application.

## External Behavior

After this fix, opening any file in yazi uses the system default application (`open` on macOS, `xdg-open` on Linux). This applies to all file types — text files open in the OS default text editor, PDFs in Preview/Evince, images in Preview/Eye of GNOME, etc.

### Implementation approach

1. Add an OS-aware open script at `skills/swain-stage/references/yazi/open.sh` that dispatches to `open` (macOS) or `xdg-open` (Linux)
2. Configure yazi's `opener` rules in the swain yazi config to use this script as the default opener for all file types
3. Stop exporting/overriding `EDITOR` in the yazi launch environment

## Acceptance Criteria

- **Given** yazi is launched via swain-stage, **when** a user opens any file, **then** it opens with the system default application
- **Given** the system is macOS, **when** the open script runs, **then** it uses `open`
- **Given** the system is Linux, **when** the open script runs, **then** it uses `xdg-open`
- **Given** `xdg-open` is not available on Linux, **when** the open script runs, **then** it falls back gracefully with an error message

## Scope & Constraints

- Fix is scoped to `skills/swain-stage/references/yazi/` config and `skills/swain-stage/scripts/swain-stage.sh`
- Must not break yazi's built-in text editing capabilities (`:` command mode)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | 0304590 | Initial creation from GitHub #15 |
| Implemented | 2026-03-13 | 9015bf1 | Transitioned — catch-all opener rule in yazi.toml |
