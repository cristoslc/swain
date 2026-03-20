---
source-id: graphite-merge-skew
type: web-page
title: "Merge Skew - Graphite Guide"
url: "https://graphite.com/guides/merge-skew"
fetched: 2026-03-20
content-hash: "--"
---

# Merge Skew

## Definition

Merge skew is "the number of commits on a trunk branch, ahead of the merge base of a merging code change." It measures how many other changes have been integrated since a pull request was created or last updated.

## Two Types of Conflicts

**Merge Conflicts** are detectable inconsistencies that occur when multiple developers modify the same code sections. Git prevents these automatically, requiring manual rebasing and resolution.

**Semantic Conflicts** are more insidious. They occur when independent changes work individually but break functionality when combined. For example, one change might rename a function while another calls it — no textual conflict exists, yet the code fails.

## Illustrative Example

A Python discount calculation scenario:
- Alice caps discount rates at 100%
- Bob adds tax calculations
- When merged without synchronization, Bob's changes override Alice's safeguard, creating a semantic conflict despite no textual collision

## Real-World Consequences

After merging code that passed CI testing, the build breaks unexpectedly. Engineering teams waste time determining if the main branch is genuinely broken, eventually bisecting to find and revert the problematic commit. This disrupts all repository contributors.

## Prevention Strategy

The fundamental solution involves maintaining low merge skew by keeping pull requests synchronized with the trunk through frequent rebasing and continuous integration testing that validates merged combinations, not just isolated changes.
