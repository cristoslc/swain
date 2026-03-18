---
id: swa-c7w1
status: closed
deps: [swa-8t7a]
links: []
created: 2026-03-18T11:54:33Z
type: task
priority: 2
assignee: cristos
parent: swa-62fm
tags: [spec:SPEC-067]
---
# Document swain-box shell function in setup docs

Add swain-box shell function definition to README or setup guide so operators can copy-paste it into ~/.zshrc. Include: swain-box() { docker sandbox run claude "${1:-$PWD}"; }. Also document Docker Desktop 4.58+ requirement and CLAUDE_CODE_OAUTH_TOKEN for Max sub. AC-12.


## Notes

**2026-03-18T11:59:43Z**

Added 'Isolated execution with swain-box' section to README.md with shell function, requirements, usage examples, sandbox management, and credential paths for both API key and Max sub users.
