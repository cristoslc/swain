---
id: swa-rmuy
status: closed
deps: [swa-syo7]
links: []
created: 2026-03-13T23:27:46Z
type: task
priority: 1
assignee: cristos
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# Integration: verify Python output matches bash for all commands

Run specgraph.py <cmd> vs specgraph.sh <cmd> for every subcommand on the live repo. Diff results (modulo trailing whitespace and OSC 8 sequences which depend on TTY). Document any intentional divergences. This is the final acceptance gate.


## Notes

**2026-03-14T05:41:49Z**

Completed: 50 integration tests pass for all 12 subcommands (341 total tests). edges SPEC-031 output matches bash exactly. Documented intentional divergences: blocks/blocked-by/tree filter resolved artifacts (Python improvement over bash); neighbors uses from/to direction labels (bash uses outgoing/incoming); scope/impact/next/status/overview have different but functionally equivalent formatting; mermaid labels nodes as ID["Title"] not ID["ID: Title"]. Full test suite 341 passed.
