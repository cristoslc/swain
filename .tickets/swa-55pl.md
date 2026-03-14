---
id: swa-55pl
status: closed
deps: [swa-0slb, swa-mnln]
links: []
created: 2026-03-13T23:27:17Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# GREEN: Implement ready/next commands

Implement ready() and next() in queries.py. ready: filter unresolved nodes whose depends-on targets are all resolved. Format with OSC 8 links, status. next: compute ready set, then for each ready item find what completing it would unblock. Also compute blocked set with waiting-on list.


## Notes

**2026-03-14T05:25:25Z**

Completed: ready() and next_cmd() implemented and tested. 16 new tests added (TestReady x8, TestNext x7 + 1 fix). Full suite: 287 passed.
