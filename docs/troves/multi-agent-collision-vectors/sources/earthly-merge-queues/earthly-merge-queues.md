---
source-id: earthly-merge-queues
type: web-page
title: "Merge Queues: What You Need to Know - Earthly Blog"
url: "https://earthly.dev/blog/merge-queues/"
fetched: 2026-03-20
content-hash: "--"
---

# Merge Queues: What You Need to Know

## The Merge Skew Problem

Semantic conflicts that CI misses: when developers A and B both pass individual tests against main but their combined changes are incompatible, the main branch breaks despite all checks passing.

The traditional solution — requiring developers to stay up to date with latest main — creates a race condition: "if several developers try to do this, it becomes a race to rebase and merge before further changes occur."

## How Merge Queues Solve It

Rather than shifting responsibility to developers, merge queues automate the process. The system "binds several pull requests into a PR group" and runs the full test suite against the combined changes against a fresh main branch copy.

If any PRs in the group fail CI checks, they are removed from the group and the rest continue with the merge process.

## Merge Methods Comparison

- **Merge**: preserves complete history but creates cluttered commit logs
- **Rebase**: produces linear history but rewrites commits (problematic with shared code)
- **Squash**: easiest to follow but loses granular history for debugging

## Optimistic vs Pessimistic Strategies

- **Pessimistic**: run tests after every merge (current standard)
- **Optimistic**: batch PRs, test groups, remove failures incrementally (merge queue approach)

The batching strategy reduces developer overhead while maintaining stability.

## Practical Tradeoffs

Key configuration decisions:
- Minimum/maximum PRs per batch
- Timeout windows (preventing indefinite waits)
- Concurrency limits for high-traffic repos
- Failure response policies (remove vs override)

Merge queues particularly benefit organizations with high-traffic repositories where merge conflicts occur frequently.
