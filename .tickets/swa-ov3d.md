---
id: swa-ov3d
status: closed
deps: [swa-5hyu, swa-i9rn, swa-31se, swa-r37l, swa-ebgy]
links: []
created: 2026-03-13T02:06:43Z
type: task
priority: 1
assignee: cristos
parent: swa-rosx
tags: [spec:SPIKE-009]
---
# Analyze cross-platform parity across mechanisms

For each mechanism researched: document macOS vs Linux behavior differences. Identify which have identical or near-identical behavior on both. Where must we accept platform-specific divergence? Map the decision space: single mechanism vs per-platform mechanism with shared launcher interface.


## Notes

**2026-03-13T02:28:11Z**

Completed: Cross-platform parity analysis. No single mechanism provides identical behavior on both platforms. Proven pattern (used by Anthropic sandbox-runtime and OpenAI Codex CLI): unified config layer that compiles to sandbox-exec on macOS + Landlock/bubblewrap on Linux. Docker provides near-identical API but different isolation models per platform. Docker Sandboxes have divergent guarantees (microVM on macOS, container on Linux).
