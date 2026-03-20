---
source-id: infinyon-bors-experience
type: web-page
title: "Increasing our development confidence and productivity with Bors"
url: "https://www.infinyon.com/blog/2021/05/bors-confident-merges/"
fetched: 2026-03-20
content-hash: "--"
---

# Increasing Our Development Confidence and Productivity with Bors

## How Bors Prevents Semantic Conflicts

Standard GitHub CI workflows run tests before merging into master, missing conflicts that arise when multiple PRs interact. "Two separate PRs each make changes that work in isolation, but which cause failures when they are merged together."

Bors addresses this by creating a `staging` branch at master's head, merging PR branches into it, running CI on the merged state, then fast-forwarding master only if tests pass. This ensures "the exact code that lands in master is the code that has been tested by your CI workflow."

## Practical Workflow

1. Open a PR and pass initial CI
2. Get team approvals
3. Comment `bors r+` to queue for merge
4. Move on to next tasks — no babysitting required

This eliminated a painful cycle where developers had to keep branches up-to-date with master before merging, often rebasing multiple times as other PRs landed first.

## Operational Lessons

Key configurations:
- Squash merges kept commit history clean
- Disabling GitHub's merge button prevented accidentally bypassing Bors
- Setting `required_approvals` in `bors.toml` prevented API errors

Failure handling: when semantic conflicts occur, "Bors simply does not update master" and notifies developers, allowing them to rebase — better than failures reaching production.

## Relevance

This is a first-party account of bors in production use. The experience confirms that the test-then-merge approach works reliably for catching semantic conflicts. The key operational insight is that bors eliminated manual rebasing races — the exact same problem swain faces with parallel worktree agents competing to merge into main.
