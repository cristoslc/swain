---
id: swa-8mpk
status: closed
deps: []
links: []
created: 2026-03-13T21:33:00Z
type: task
priority: 1
assignee: cristos
parent: swa-9tg7
tags: [spec:SPEC-030]
---
# Scaffold module structure and integration test

Create specgraph/ package (parser.py, graph.py, resolved.py, cli.py, __init__.py), specgraph.py entry point, tests/ dir. Write a failing integration test that runs specgraph.py build and asserts cache output matches bash.


## Notes

**2026-03-13T21:36:12Z**

Scaffolded specgraph/ package (parser.py, graph.py, resolved.py, cli.py), specgraph.py entry point, tests/. Integration test: 6/6 pass — Python build matches bash (72 nodes, 132 edges, all node metadata and edges identical).
