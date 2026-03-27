---
title: "Documentation Viewer"
artifact: SPEC-093
track: implementable
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
type: feature
parent-epic: EPIC-034
parent-initiative: INITIATIVE-015
parent-vision: VISION-001
linked-artifacts:
  - DESIGN-004
  - SPEC-091
  - INITIATIVE-015
  - EPIC-034
depends-on-artifacts:
  - SPEC-091
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Documentation Viewer

## Problem Statement

swain-stage currently launches a tmux layout for session management. This served early development but has become a liability: the tmux code is fragile, the pane layout does not scale, and it conflates "development environment" with "project information surface." Meanwhile, swain is gaining a TRAIN artifact type (SPEC-091) for structured documentation, but there is no way for operators to browse that documentation outside of reading raw markdown files.

Operators need a browsable, always-accessible documentation site that renders TRAINs in a structured hierarchy — organized by Vision and train-type — with inline staleness warnings when documentation drifts from its source artifacts.

## External Behavior

### Invocation

The `/swain-stage` skill is rewritten from scratch. On invocation:

1. Scans `docs/train/` for all TRAIN artifacts in Active phase
2. Reads frontmatter to determine Vision ancestry and train-type for each TRAIN
3. Generates the Docsify sidebar configuration dynamically
4. Runs `train-check.sh` to detect stale TRAINs
5. Starts a local Docsify server (zero-build, client-side rendering)
6. Opens the default browser to the local URL (or prints the URL in headless environments)

### Technology

**Docsify** with a custom swain theme. No static site generation — markdown files on disk are the source of truth. Refreshing the browser shows the latest content.

### Navigation

A persistent tab bar at the top provides the multi-panel structure defined in DESIGN-004:

| Tab | State | Behavior |
|-----|-------|----------|
| **Docs** | Active | Documentation viewer (this spec) |
| **Status** | Greyed out | Placeholder page describing future status dashboard |
| **Graph** | Greyed out | Placeholder page describing future artifact graph |
| **Diff** | Greyed out | Placeholder page describing future branch diff viewer |

The Docs tab sidebar organizes TRAINs in a Vision-first hierarchy:

```
VISION-001: Swain
├── How-to
│   └── [TRAIN titles...]
├── Reference
│   └── [TRAIN titles...]
└── Quickstart
    └── [TRAIN titles...]
```

TRAINs without Vision ancestry appear in an "Uncategorized" section.

### Staleness warnings

When `train-check.sh` detects that a TRAIN's commit-pinned dependencies have drifted, the viewer renders an inline warning banner at the top of that TRAIN's content. The banner shows:
- Which linked artifact changed
- How many commits behind the pin is
- When the TRAIN was last verified
- A link to the relevant artifact for review

### Placeholder pages

Greyed-out tabs navigate to placeholder pages that:
- Name the planned feature
- Describe what it will do in 1-2 sentences
- Link to the relevant EPIC or Initiative for tracking
- Never return a 404 or blank page

### Empty state

If no TRAINs exist yet, the Docs panel shows a helpful message explaining what TRAINs are and how to create the first one, with a reference to SPEC-091.

### Responsive layout

- Desktop (>1024px): sidebar + main content side-by-side
- Tablet (768-1024px): collapsible sidebar
- Mobile (<768px): hamburger menu, stacked layout

### What gets deleted

The entire existing swain-stage tmux codebase is removed:
- All tmux layout configuration
- All tmux pane management scripts
- The tmux-based SKILL.md for swain-stage
- Any session hooks that reference the tmux layout

The `/swain-stage` skill is rebuilt as a documentation viewer launcher.

## Acceptance Criteria

- **Given** an operator invokes `/swain-stage`, **When** TRAIN artifacts exist in `docs/train/Active/`, **Then** a Docsify-based documentation site opens in the browser with TRAINs organized by Vision and train-type
- **Given** the docs viewer is running, **When** an operator clicks a TRAIN in the sidebar, **Then** the TRAIN's markdown content renders in the main content area with a breadcrumb trail (Vision > train-type > title)
- **Given** a TRAIN has stale commit-pinned dependencies, **When** the docs viewer renders that TRAIN, **Then** an inline warning banner shows which artifacts drifted and by how many commits
- **Given** the docs viewer is running, **When** an operator clicks the greyed-out Status tab, **Then** a placeholder page renders describing the planned feature and linking to the tracking artifact (not a 404)
- **Given** no TRAIN artifacts exist, **When** an operator invokes `/swain-stage`, **Then** the docs viewer shows an empty state with instructions for creating the first TRAIN
- **Given** the previous tmux-based swain-stage, **When** SPEC-093 is implemented, **Then** all tmux layout code, pane management scripts, and tmux-based SKILL.md content for swain-stage are removed
- **Given** the docs viewer is rendered on a viewport <768px wide, **When** the operator views the page, **Then** the layout is responsive with a hamburger menu replacing the sidebar
- **Given** an operator invokes `/swain-stage` in a headless environment (no browser available), **Then** the skill prints the local URL to stdout instead of attempting to open a browser

## Scope & Constraints

- **Single branch, current working directory only.** The viewer shows TRAINs from the checked-out branch. No worktree awareness, no cross-branch content merging. Multi-branch support is a future panel under INITIATIVE-015.
- **Active TRAINs only.** Retired, Superseded, and Abandoned TRAINs are excluded from the sidebar navigation (though they remain in the filesystem).
- **No editing.** The viewer is read-only. TRAINs are authored via swain-design, not through the browser.
- **No authentication.** The local Docsify server runs on localhost. No auth layer, no remote access.
- **Depends on SPEC-091.** The TRAIN artifact type, template, and train-check.sh script must exist before this spec can be implemented.

## Implementation Approach

1. **Scaffold Docsify project (TDD: criteria 1, 6):**
   - Initialize Docsify configuration in a swain-stage skill directory
   - Create custom swain theme (CSS/JS)
   - Remove all existing tmux-based swain-stage code
   - Test: skill invocation starts a local server

2. **Dynamic sidebar generation (TDD: criteria 1, 2):**
   - Write a script/plugin that scans `docs/train/Active/` for TRAIN artifacts
   - Parse frontmatter to extract Vision ancestry and train-type
   - Generate Docsify sidebar configuration grouped by Vision > train-type
   - Test: sidebar reflects actual TRAIN artifacts on disk

3. **Tab bar and placeholder pages (TDD: criteria 4):**
   - Implement persistent top navigation with Docs/Status/Graph/Diff tabs
   - Grey out non-Docs tabs with CSS
   - Create placeholder pages for each future panel
   - Test: clicking greyed-out tab navigates to placeholder, not 404

4. **Staleness integration (TDD: criteria 3):**
   - Call `train-check.sh` during sidebar generation
   - Inject warning banner markup into stale TRAIN content
   - Test: stale TRAIN shows drift banner, current TRAIN does not

5. **Empty state and edge cases (TDD: criteria 5, 7, 8):**
   - Implement empty state when no TRAINs exist
   - Add responsive CSS breakpoints
   - Handle headless invocation (print URL, don't open browser)
   - Test: empty state renders; responsive layout collapses sidebar; headless prints URL

6. **Skill rewrite (TDD: criteria 1, 6):**
   - Rewrite swain-stage SKILL.md as documentation viewer launcher
   - Update skill description, triggers, and instructions
   - Test: `/swain-stage` launches docs viewer end-to-end

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Initial creation from approved design doc |
