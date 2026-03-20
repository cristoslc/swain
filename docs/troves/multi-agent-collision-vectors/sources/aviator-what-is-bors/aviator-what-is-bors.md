---
source-id: aviator-what-is-bors
type: web-page
title: "What's a bors, and Why (Don't) You Want It?"
url: "https://www.aviator.co/blog/what-is-bors/"
fetched: 2026-03-20
content-hash: "--"
---

# What's a bors, and Why (Don't) You Want It?

## What Bors Does

Bors-NG is a GitHub automation tool that solves merge skew — when code passes review but fails after merging because the main branch changed. The classic scenario: one patch renames a function while another calls it by its old name, both reviewed separately.

Bors follows the principle: "You test it first, then promote it, not the other way around."

## The Test-Then-Merge Approach

Major projects (Rust, Kubernetes) employ bots that:
1. Merge code into a staging branch
2. Run complete test suites
3. Promote validated merged code to the main branch

This prevents incompatible patches from reaching production.

## Batching and Bisection

If test suites exceed a couple hours, patches accumulate faster than merging. Batching helps: test multiple PRs together. When a batch fails, bisect to find the faulty PR — potentially consuming an entire day for long suites.

When test suites run quickly, batches are smaller and bisecting is faster.

## Key Limitations

- Security risks if the bot gets compromised
- Development halts if the bot malfunctions
- Pointless if test coverage is insufficient
- Slow queue processing with lengthy test suites

## When NOT to Use Bors

**Too small:** overhead exceeds benefits; manual testing before releases suffices.

**Too large:** all-day test execution makes bors impractical; Firefox-style "sheriffing" (human/AI reviewing failures) works better. Human sheriffs offer "more accurate than Bors-NG style bisecting" results.

## Best Practices

1. **Tiered testing**: reduced test suites during PR review; full batteries for the bors queue
2. **Speed optimization**: fast tests encourage local testing, faster queue clearance, quicker bisection
3. **Determinism**: eliminate flaky tests; conduct fuzz testing outside bors
