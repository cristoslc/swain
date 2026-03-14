---
id: swa-rmuy
status: open
deps: [swa-syo7]
links: []
created: 2026-03-13T23:27:46Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# Integration: verify Python output matches bash for all commands

Run specgraph.py <cmd> vs specgraph.sh <cmd> for every subcommand on the live repo. Diff results (modulo trailing whitespace and OSC 8 sequences which depend on TTY). Document any intentional divergences. This is the final acceptance gate.

