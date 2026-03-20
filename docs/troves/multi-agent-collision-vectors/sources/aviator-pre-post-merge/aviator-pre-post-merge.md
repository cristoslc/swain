---
source-id: aviator-pre-post-merge
type: web-page
title: "Pre and Post-Merge Tests Using a Merge Queue"
url: "https://www.aviator.co/blog/pre-and-post-merge-tests-using-a-merge-queue/"
fetched: 2026-03-20
content-hash: "--"
---

# Pre and Post-Merge Tests Using a Merge Queue

## Core Distinction

Pre-merge tests prioritize speed for rapid developer feedback. Post-merge tests emphasize stability, validating system health after integration.

### Pre-Merge Tests

Execute during pull request review. Categories:
- Code linting (catches bugs early, cheap and fast)
- Unit tests (validates individual components)
- Integration testing (verifies module interactions)

### Post-Merge Tests

Run after code integration. Categories:
- Automated regression testing (identifies broken functionality)
- Performance testing (detects degradation over time)
- User Acceptance Testing (manual QA, inherently slow)

## The "Post-Queue is Post-Merge" Insight

A conceptual shift: queued PRs occupy a "staging" branch before mainline integration. This enables running traditionally post-merge tests within the queue, allowing automated rollback if validation fails.

The developer workflow becomes:
1. Submit PR with passing pre-merge checks
2. Enqueue (rather than merge) after approval
3. Queue validates all tests on staging branch
4. Mainline fast-forwards only if all checks pass

This approach maintains a consistently green mainline while automating failure recovery — eliminating manual coordination between developers and release teams.
