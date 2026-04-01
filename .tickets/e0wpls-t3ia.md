---
id: e0wpls-t3ia
status: closed
deps: [e0wpls-xnp5]
links: []
created: 2026-04-01T03:06:12Z
type: task
priority: 2
assignee: cristos
parent: e0wpls-2avd
tags: [spec:SPEC-217]
---
# GREEN: implement resolve-worktree-links.sh

Implement the resolver: parse piped findings or run detector internally, rewrite markdown depth, recreate symlinks, patch script paths. Emit FIXED/UNRESOLVABLE per finding. Idempotent.


## Notes

**2026-04-01T03:10:26Z**

GREEN — resolve-worktree-links.sh implemented. 31/31 tests passing across full suite.
