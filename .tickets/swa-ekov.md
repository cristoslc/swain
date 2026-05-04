---
id: swa-ekov
status: open
deps: [swa-js3s]
links: []
created: 2026-04-14T01:31:23Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-qc20
tags: [spec:SPEC-305]
---
# Generalize swain-doctor symlink repair

Iterate the full dir list across all linked worktrees. Test: broken or missing symlinks get repaired. Healthy worktrees produce no changes. New data-file entries flow through without code edits. Silent repair with summary.

