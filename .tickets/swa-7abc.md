---
id: swa-7abc
status: open
deps: [swa-9wuc, swa-sujx]
links: []
created: 2026-03-20T15:09:56Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-f0pa
tags: [spec:SPEC-103]
---
# Build relink.sh command

Iterate all BROKEN_LINK findings from specwatch, extract the artifact ID from the link text, call resolve-artifact-link.sh to get the current path, and patch the markdown link in place. Support single-file and whole-tree modes.

