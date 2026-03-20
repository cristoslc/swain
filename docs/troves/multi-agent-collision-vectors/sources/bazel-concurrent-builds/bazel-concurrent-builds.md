---
source-id: bazel-concurrent-builds
type: documentation
title: "Bazel Remote Execution and Concurrent Builds"
url: "https://bazel.build/remote/rbe"
fetched: 2026-03-20
content-hash: "--"
---

# Bazel Remote Execution and Concurrent Builds

## Action Isolation

Build actions in Bazel are isolated — build tools do not retain state and dependencies cannot leak between them. If a build tool can access dependencies across build actions, those actions will fail when remotely executed because each remote build action is executed separately.

## Content-Addressed Cache

Each artifact in the cache is keyed on both its target and a hash of its inputs. Different engineers can make different modifications to the same target at the same time, and the remote cache stores all resulting artifacts and serves them appropriately without conflict.

This is a form of optimistic concurrency: concurrent modifications are not prevented, but the content-addressing scheme ensures that each unique input set produces a unique cache entry.

## Atomicity in Multiplex Workers

Because different threads could complete and write to the stream at the same time, the worker process needs to make sure responses are written atomically (messages don't overlap). Anything sent to stderr goes into a single log file shared among all WorkerProxys of the same type, randomly interleaved between concurrent requests.

## Concurrent Changes Protection

The `--experimental_guard_against_concurrent_changes` flag helps protect the external cache from being poisoned by changes to input files that happen during a build. This is a direct TOCTOU mitigation: the flag detects when input files change between the time Bazel reads them and the time the build action completes.

## Relevance to Multi-Agent Coordination

Bazel's approach is instructive: content-addressed caching (a form of CAS) combined with action isolation prevents concurrent build conflicts without requiring locks. The pattern — isolate execution, content-address outputs, detect input changes during execution — maps to the multi-agent worktree problem: isolate agents in worktrees, content-address commits, detect base-branch changes during agent execution.
