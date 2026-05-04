---
title: File Explorer
url: https://www.getagentcraft.com/docs/features/file-explorer
fetched: 2026-05-04
type: documentation
---

# File Explorer

Browse project files from the side panel.

The Files tab in the Side Panel provides a project file explorer with search filtering and a recursive directory tree.

## Features

- Recursive directory tree — Expandable directories with colored file type badges
- Search filtering — Real-time substring search with automatic ancestor expansion
- IDE integration — Click any file to open it in VS Code or another configured editor
- Inline diff access — View file diffs directly from the tree

## File Type Icons

Files are tagged with colored badges by extension:

| Badge | Extensions |
| --- | --- |
| TS (blue) | .ts, .tsx |
| JS (yellow) | .js, .jsx |
| CSS (purple) | .css, .scss, .less |
| JSON (gold) | .json, .yaml, .yml, .toml |
| MD (green) | .md, .mdx, .txt |
| PY (blue) | .py |
| RS (copper) | .rs |
| GO (cyan) | .go |
| SH (green) | .sh, .bash, .zsh |
| HTML (orange) | .html, .svg |
| IMG (pink) | .png, .jpg, .jpeg, .gif, .webp |

## Search

Type in the search box to filter files by name. The tree automatically expands directories containing matching files. When you clear the search, the previous expansion state is restored.

## Opening Files

Click any file in the tree to open it. The default action opens the file in VS Code. The Git tab provides an IDE picker button for choosing alternative editors.

## Refresh

The directory structure is fetched when the Files tab is opened. Click the refresh button to reload the tree manually.