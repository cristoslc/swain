---
id: swa-gyrv
status: closed
deps: [swa-fwou]
links: []
created: 2026-03-18T03:37:18Z
type: task
priority: 2
assignee: cristos
parent: swa-u7jl
tags: [spike:SPIKE-027, spec:SPEC-067]
---
# Thread 5: selective subdir mounts

Test mounting individual ~/.claude/ subdirs independently (e.g. ~/.claude/skills:ro, ~/.claude/CLAUDE.md:ro, no ~/.claude/projects/). Does the result produce a coherent dir structure inside the sandbox? Does Claude Code see skills and global CLAUDE.md without the memory/projects dir?


## Notes

**2026-03-18T03:54:00Z**

No -e/--env flags on docker sandbox run — env vars injected via proxy only. Sandbox home = /home/agent (not /Users/cristos) so host ~/.claude/:ro lands at wrong path. ~/.claude/projects/ has 60+ project memories — major exposure risk. Sandbox creates /home/agent/.claude/ automatically with proxy auth. Wholesale ~/.claude/:ro mount is wrong approach.
