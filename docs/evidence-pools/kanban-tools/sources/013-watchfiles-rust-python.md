---
source-id: "013"
title: "watchfiles — Rust-backed async file watching for Python"
type: web
url: "https://github.com/samuelcolvin/watchfiles"
fetched: 2026-03-15T03:00:00Z
hash: "pending"
---

# watchfiles

Simple, modern, high-performance file watching and code reload for Python. Written in Rust (Notify library). Previously named "watchgod."

## Key characteristics

- **Rust core**: Uses the Notify Rust library for platform-native filesystem events (FSEvents on macOS, inotify on Linux, ReadDirectoryChangesW on Windows)
- **Async-first**: `awatch()` yields sets of `(change_type, path)` tuples via async generator
- **Sync API too**: `watch()` for synchronous use, `run_process()` for code reload
- **Debouncing built in**: Coalesces rapid changes before yielding
- **Pre-built binaries**: Available for most architectures on Linux, macOS, Windows
- **Lightweight**: Minimal Python wrapper over Rust — fast, low resource usage

## Comparison to watchdog

| | watchfiles | watchdog |
|---|---|---|
| Language | Rust + Python | Pure Python |
| Async | Native `awatch()` | Threaded observer |
| Debounce | Built-in | Manual |
| API style | Generator (yields change sets) | Event handler callbacks |
| Maturity | Newer, growing | Established, widely used |
| Cross-platform | Yes (Notify) | Yes (platform-specific backends) |

## Relevance to reactive loop

watchfiles is a strong candidate for the swain watcher component. Its async generator API fits naturally into an event loop that processes frontmatter changes. Built-in debouncing solves the "duplicate events on save" problem that plagues raw filesystem watchers. Daymark's architecture doc already references watchfiles as one option.
