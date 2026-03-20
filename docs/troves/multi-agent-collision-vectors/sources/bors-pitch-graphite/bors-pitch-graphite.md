---
source-id: bors-pitch-graphite
type: web-page
title: "Not Rocket Science - How Bors and Google's TAP inspired modern merge queues"
url: "https://graphite.com/blog/bors-google-tap-merge-queue"
fetched: 2026-03-20
content-hash: "--"
---

# Not Rocket Science - How Bors and Google's TAP Inspired Modern Merge Queues

## The Not Rocket Science Rule

Graydon Hoare's foundational principle, established in the early 2000s at Cygnus/RedHat: "automatically maintain a repository of code that always passes all the tests." This elegantly simple goal has proven remarkably difficult to achieve at scale.

## The Merge Skew Problem

The core challenge emerges when code testing occurs in isolation from current trunk state. If a PR passes CI based on commit (a), but teammates merge changes creating commit (a') during testing, the PR's validation becomes stale. This merge skew creates semantic conflicts — changes that don't syntactically conflict but break functionality together.

The impact scales with team size:
- 5 merges/day: minimal disruption
- 20+ merges/day: noticeable collisions
- 50+ merges/day: severe productivity hits
- GitHub experienced major conflicts at 60 PRs daily

## Bors: The First Automated Queue

Graydon's Bors system introduced the first practical solution — engineers tagged PRs with comments to queue them. Bors ran CI sequentially, ensuring zero merge skew before landing changes. However, sequential processing created bottlenecks: a 15-minute CI on 40 daily merges yielded only 4 changes hourly.

## Google's TAP: Parallel Batching at Scale

Google's approach diverged fundamentally. With 95% of engineers in one monorepo averaging commits per second, sequential queuing became impossible. Their system:

- Maintains two trunk pointers: latest commits and latest verified-passing commits ("green-main")
- Batches unverified commits into related groups
- Runs parallelized tests across batches
- Automatically bisects and reverts failing changes
- Allows engineers to merge after short pretests, with verification happening post-merge

This optimistic-then-verify model prioritizes developer experience while maintaining correctness through delayed comprehensive validation.

## Modern Evolution

By 2023, GitHub and GitLab implemented native merge queue features incorporating lessons from both approaches: parallel CI execution, batching, automated failure handling, and virtual queuing based on dependencies.

The fundamental insight: merge queues address a mathematical problem requiring parallelization, batching, and intelligent failure recovery — not merely sequential automation.
