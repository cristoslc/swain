---
id: swa-2yqm
status: closed
deps: [swa-3fbq, swa-qvui]
links: []
created: 2026-03-13T21:33:01Z
type: task
priority: 1
assignee: cristos
parent: swa-9tg7
tags: [spec:SPEC-030]
---
# GREEN: CLI dispatch and build command

Argparse-based CLI in cli.py. Wire up build subcommand. Entry point specgraph.py calls cli.main(). Parse --all and --all-edges flags. Auto-rebuild on stale cache.


## Notes

**2026-03-13T21:38:55Z**

cli.py with argparse dispatch, build command, auto-rebuild on stale cache. specgraph.py entry point works: 'Graph built: /tmp/agents-specgraph-043bb4889eec.json Nodes: 72 Edges: 132'
