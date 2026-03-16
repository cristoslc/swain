---
source-id: "017"
title: "Near-miss alternatives — Front Matter CMS, headless CMS tools, Datasette, knowledge bases"
type: web
url: "https://frontmatter.codes/docs/dashboard/content-view"
fetched: 2026-03-15T03:15:00Z
hash: "pending"
---

# Near-Miss Alternatives

Tools that aren't kanban boards but could theoretically serve as a visual surface for markdown files with frontmatter.

## Front Matter CMS (VS Code extension) — CLOSEST NEAR-MISS

A headless CMS running inside VS Code. Has a dashboard that shows markdown files as cards in a grid.

**What it can do:**
- Groups content by custom frontmatter fields (including `status`)
- Filters by any frontmatter field
- Card grid view with configurable displayed fields
- Manages frontmatter editing via a panel UI

**What it can't do:**
- No kanban/board layout — only a card grid, no columns per status value
- No drag-and-drop between statuses — you edit the field in a form
- No multi-track lifecycle awareness — single flat collection view
- No phase ordering or forward-only enforcement
- No filesystem watching for external changes (it IS the editor)
- VS Code only — not standalone

**Verdict:** Front Matter CMS is the closest near-miss. It reads markdown files, understands frontmatter, and can group by a status field. But it renders a filterable grid, not a kanban board. You'd need to mentally reconstruct the lifecycle from filtered views. No drag-and-drop transitions. And it's locked to VS Code.

## Git-based headless CMS tools (Decap/TinaCMS/Sveltia)

These read markdown files with frontmatter and provide editing UIs. All are designed for static site content management (blog posts, pages), not project lifecycle management.

- **Decap CMS**: Browser-based, reads from git repo. List/editorial view. No kanban. Designed for non-technical editors.
- **TinaCMS**: Visual editing overlaid on your site. No board view. Cloud-dependent.
- **Sveltia CMS**: Decap successor. Same editorial model, no board view.

None of these provide lifecycle visualization or kanban boards.

## Datasette + markdown-to-sqlite

Datasette can ingest markdown frontmatter into SQLite (via `markdown-to-sqlite`), then query and visualize it. Theoretically you could build a kanban view as a Datasette plugin.

**Why not:** You'd be building the same thing as daymark but with an extra SQLite intermediary, losing real-time file watching, and requiring custom plugin development. More complexity for no benefit.

## Knowledge base tools (Foam, Dendron)

VS Code extensions for personal knowledge management with markdown. They provide graph visualization, backlinks, and note organization — but no kanban/lifecycle board views. Foam and Dendron are note-taking tools, not project management tools.

## Markdown++ (browser-based content panel)

Framework-agnostic browser-based tool for managing markdown files with frontmatter. Table view with sorting/filtering, but no board layout, no grouping by status columns, no kanban. Designed for static site content management.
