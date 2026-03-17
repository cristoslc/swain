---
id: aa-miu5
status: closed
deps: [aa-f4ey]
links: []
created: 2026-03-17T17:12:46Z
type: task
priority: 1
assignee: cristos
tags: [spec:SPEC-058]
---
# GREEN — Implement file discovery for agentic runtime context files

Add file discovery logic to scan directories recursively for agentic context files (CLAUDE.md, AGENTS.md, .cursorrules, SKILL.md, etc). SPEC-058.


## Notes

**2026-03-17T17:20:28Z**

GREEN complete: File discovery implemented in scanner core. Discovers CLAUDE.md, AGENTS.md, .cursorrules, .clinerules, .windsurfrules, SKILL.md, mcp.json, copilot-instructions.md, .mdc rules, and more. 11 file discovery tests pass including negative test for random files.
