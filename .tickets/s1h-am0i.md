---
id: s1h-am0i
status: closed
deps: [s1h-z0l5, s1h-k6ok]
links: []
created: 2026-03-20T15:11:03Z
type: task
priority: 2
assignee: cristos
parent: s1h-wrgp
tags: [spec:SPEC-103]
---
# Build relink.sh command

Iterate all BROKEN_LINK findings from specwatch, extract the artifact ID from the link text, call resolve-artifact-link.sh to get the current path, and patch the markdown link in place. Support single-file and whole-tree modes.


## Notes

**2026-03-20T15:21:44Z**

relink.sh built with 14/14 tests passing. Supports single-file and full-tree modes. Handles body-text links and frontmatter rel-path fields. Skips code fences. Reports RELINKED for each fix.
