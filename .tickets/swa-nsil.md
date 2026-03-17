---
id: swa-nsil
status: closed
deps: []
links: []
created: 2026-03-17T17:11:14Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-j8jz
tags: [spec:SPEC-062]
---
# RED: Write tests for file-path-based detection and false positive rate

Test that file paths matching auth/, crypto/, .env, etc. trigger detection. Verify non-security tasks like 'Update README' are not flagged.


## Notes

**2026-03-17T18:10:41Z**

Complete: implementation merged from worktree-agent-ae45acba. 66 tests passing.
