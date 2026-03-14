---
id: swa-na4r
status: open
deps: [swa-fkfl]
links: []
created: 2026-03-14T06:07:57Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-ymk2
tags: [spec:SPIKE-008]
---
# Design filesystem binding strategy for agent state dirs

Map host paths to container/sandbox paths for: project dir, .claude/, .agents/, .tickets/, ~/.claude/ global config. Which dirs must be writable vs. read-only? Exclude sensitive host files.

