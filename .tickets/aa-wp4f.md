---
id: aa-wp4f
status: closed
deps: []
links: []
created: 2026-03-17T17:13:05Z
type: task
priority: 1
assignee: cristos
tags: [spec:SPEC-062, tdd:red]
---
# RED — Write tests for file-path-based detection and false positive rate

Write failing tests for file path patterns (auth/, crypto/, middleware/auth, .env, *credentials*, *secret*) and validate false positive rate < 20% on non-security tasks. Test that package.json modification returns true with category dependency-change.


## Notes

**2026-03-17T17:15:40Z**

RED confirmed: 15 file-path tests fail against stub, 8 pass (non-security paths, empty/none, return type checks, false positive rate trivially passes on stub). Covers auth/, crypto/, middleware/auth, .env*, credentials*, secret*, package.json, requirements.txt, pyproject.toml, go.mod, nested paths, description keywords, and 20-item FP rate corpus.
