---
id: swa-1qiw
status: closed
deps: []
links: []
created: 2026-03-17T18:21:46Z
type: task
priority: 1
assignee: cristos
parent: swa-gm1z
tags: [spec:SPEC-064]
---
# RED: Write tests for finding-to-ticket filing

Test that findings are filed as new tk issues with security-finding tag, linked to originating task. Test no issues filed when clean.


## Notes

**2026-03-17T18:24:55Z**

RED complete: 11 tests for file_finding_as_ticket (correct fields, security-finding tag, linking, priority mapping, error handling) and 3 tests for run_gate filing integration (clean scan, None filtering, originating task passthrough). All fail with ModuleNotFoundError.
