---
title: "swain-stage Interaction Design"
artifact: DESIGN-004
track: standing
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-initiative: INITIATIVE-015
superseded-by: ""
linked-artifacts:
  - INITIATIVE-015
  - EPIC-034
  - SPEC-093
  - SPEC-091
depends-on-artifacts: []
---

# swain-stage Interaction Design

## Interaction Surface

Browser-based project control surface invoked via the `/swain-stage` skill. Replaces the tmux-based swain-stage entirely. The design covers the full multi-panel vision even though only the documentation viewer panel ships first.

## Technology

**Docsify** with a custom swain theme. Zero-build architecture — markdown is rendered client-side with no static site generation step. This matches swain's philosophy of artifacts-on-disk as the source of truth.

## Navigation Architecture

### Global navigation (tab bar)

A persistent top-level tab bar provides access to all panels. At launch, only the Docs tab is active; future tabs are visible but greyed out to communicate the roadmap.

| Tab | Status | Description |
|-----|--------|-------------|
| **Docs** | Active | Documentation viewer — browsable TRAINs |
| **Status** | Greyed out | Status dashboard (future EPIC) |
| **Graph** | Greyed out | Artifact graph visualization (future EPIC) |
| **Diff** | Greyed out | Worktree-aware branch diffing (future EPIC) |

Greyed-out tabs are clickable. They navigate to placeholder pages — not 404s — that describe the planned feature and link to the relevant EPIC or Initiative for tracking.

### Docs panel navigation (sidebar)

Within the Docs tab, a sidebar organizes TRAINs in a Vision-first hierarchy, then by train-type within each vision:

```
VISION-001: Swain
├── How-to
│   ├── How to Create a SPEC
│   └── How to Run a Security Scan
├── Reference
│   └── Artifact Type Reference
└── Quickstart
    └── Your First Swain Project

VISION-002: Safe Autonomy
├── How-to
│   └── How to Configure Credential Scoping
└── Reference
    └── swain-box Runtime Options
```

TRAINs without Vision ancestry appear in an "Uncategorized" section at the bottom.

The sidebar is generated dynamically by scanning `docs/train/` and reading frontmatter to determine vision ancestry and train-type. No manual sidebar configuration required.

## Screen States

### Docs panel — normal state

- Sidebar with Vision-first hierarchy
- Main content area renders the selected TRAIN's markdown
- Breadcrumb trail: Vision > train-type > TRAIN title

### Docs panel — stale TRAIN

When `train-check.sh` detects drift, a warning banner appears at the top of the stale TRAIN's content:

```
⚠ This document may be out of date.
SPEC-067 has changed since this document was last verified (3 commits behind).
Last verified: 2026-03-15 | Current: 2026-03-19
```

The banner links to the relevant artifact's diff for quick review.

### Placeholder page (greyed-out tab)

When an operator clicks a greyed-out tab, they see:

```
Status Dashboard — Coming Soon

This panel will show real-time project status, scope progress,
and decision points requiring operator attention.

Track progress: INITIATIVE-015 > [future EPIC link]
```

No broken pages. No empty states. Every click leads somewhere meaningful.

### Empty docs state

If no TRAINs exist yet (e.g., right after SPEC-091 ships but before any TRAINs are authored):

```
No documentation yet.

TRAINs are swain's documentation artifacts. Create your first one
with swain-design:

  "Create a quickstart TRAIN for [feature]"

See: SPEC-091 (TRAIN Artifact Type) for the full specification.
```

## Responsive Layout

- **Desktop (>1024px):** Sidebar + main content side-by-side
- **Tablet (768-1024px):** Collapsible sidebar, full-width content
- **Mobile (<768px):** Hamburger menu for sidebar, stacked layout

The primary use case is desktop (operators working alongside their terminal), but responsive support ensures the docs are readable on any device.

## Invocation

The `/swain-stage` skill:
1. Scans `docs/train/` for TRAIN artifacts
2. Generates the Docsify sidebar configuration from frontmatter
3. Runs `train-check.sh` to detect stale TRAINs
4. Starts a local Docsify server
5. Opens the browser (or prints the URL if in a headless environment)

## Scope Boundary

One branch, current working directory. The docs viewer shows TRAINs from the checked-out branch only. No worktree awareness, no multi-branch diffing, no cross-worktree content merging. Those capabilities are future panels under the same Initiative.

## Design Decisions

1. **Docsify over static site generators** — Zero-build means no compilation step. Markdown files on disk are the single source of truth. Adding a TRAIN and refreshing the browser is the authoring workflow. No Gatsby/Hugo/Jekyll build pipeline to maintain.

2. **Greyed-out tabs over hidden tabs** — Operators should see the product direction. Hiding future panels makes the docs viewer look like a standalone tool. Greyed-out tabs communicate "this is a multi-panel control surface, and more is coming."

3. **Placeholder pages over 404s** — Every navigation target resolves to meaningful content. Placeholder pages describe the planned feature and link to the relevant tracking artifact. This is an information surface — dead ends are unacceptable.

4. **Vision-first navigation over flat lists** — As the number of TRAINs grows, a flat alphabetical list becomes unusable. Grouping by Vision, then by train-type, mirrors the artifact hierarchy that operators already understand.

5. **Dynamic sidebar generation over manual configuration** — The sidebar is generated from frontmatter, not maintained by hand. This eliminates sidebar-vs-reality drift and means the docs viewer always reflects what's actually on disk.

## Assets

No wireframes at this stage — the screen states above and the Docsify theme will serve as the visual specification. The custom swain theme will be developed as part of SPEC-093 implementation.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Initial creation from approved design doc |
