---
source-id: github-merge-queue-docs
type: documentation
title: "Managing a merge queue - GitHub Docs"
url: "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue"
fetched: 2026-03-20
content-hash: "--"
---

# Managing a Merge Queue - GitHub Docs

## How Merge Groups Work

Merge queues process pull requests in FIFO order by creating temporary branches with the prefix `gh-readonly-queue/{base_branch}`. When a PR is added, the system groups it into a `merge_group` with the latest version of the `base_branch` as well as changes from pull requests ahead of it in the queue.

The queue validates that combined changes pass all required status checks before merging to the target branch.

## Conflict and Failure Detection

The system automatically removes PRs when:
- CI reports test failures for the merge group
- Awaiting CI results exceeds the configured timeout
- Branch protection failures occur that cannot be automatically resolved
- Users manually request removal

When failures occur mid-queue, the system rebuilds subsequent temporary branches containing only the remaining PRs and their cumulative changes.

## Configuration Options

- **Merge method**: merge, rebase, or squash
- **Build concurrency**: webhook dispatch limits (1-100) to throttle CI builds
- **Check requirements**: whether only passing PRs form groups, or if intermittent failures can proceed
- **Status check timeout**: wait duration before assuming failure
- **Merge limits**: minimum/maximum PRs per merge (1-100) and timeout for reaching minimums

## Key Limitations

1. **FIFO ordering only** — no ability to reorder PRs in the queue
2. **Queue removal and re-entry** — a PR with no conflicts with trunk but conflicts with the queue gets kicked out; even after fixing, it is not automatically re-added
3. **CI integration challenges** — workflows must explicitly include the `merge_group` event trigger
4. **No optimization modes** — no batching; the only way to make the queue faster is faster CI
5. **Wildcard branch patterns** — merge queue cannot be enabled with branch protection rules using wildcards
