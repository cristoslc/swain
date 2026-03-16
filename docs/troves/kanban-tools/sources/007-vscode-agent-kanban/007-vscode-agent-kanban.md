---
source-id: "007"
title: "VS Code Agent Kanban — Task management for AI-assisted developers"
type: web
url: "https://www.appsoftware.com/products/developer-tools/agent-kanban"
fetched: 2026-03-15T02:40:00Z
hash: "pending"
---

# VS Code Agent Kanban

VS Code extension providing a kanban board for managing AI coding agent tasks with GitHub Copilot integration.

## Key characteristics

- **Each task is a .md file** with YAML frontmatter in `.agentkanban/tasks/` directories per lane
- **Lane determined by directory**: `tasks/todo/`, `tasks/doing/`, `tasks/done/` — not by frontmatter field
- **Structured conversation log**: Task body uses `[user]` and `[agent]` markers for plan/implement history
- **Plan → Todo → Implement workflow**: `@kanban /task`, `@kanban /plan`, `@kanban /todo`, `@kanban /implement`
- **GitHub Copilot integration**: `@kanban` chat participant works with Copilot's native agent mode
- **Board config in board.yaml**: Lane definitions (slug list), base prompt, memory file

## How it differs from daymark

- **Task tracker, not document visualizer**: Creates and manages its own task files — doesn't read existing artifacts
- **Agent workflow tool**: Designed for Copilot Chat integration, not filesystem visualization
- **Directory-based lanes**: Fixed directory structure, not frontmatter-field-driven columns
- **VS Code + Copilot only**: Tight coupling to VS Code and GitHub Copilot ecosystem

## Relevance to swain

Agent Kanban is a task management tool for AI coding workflows, not a document lifecycle visualizer. It creates its own files in its own directory structure. It cannot read swain's existing artifact tree. Different problem space entirely.
