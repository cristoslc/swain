---
source-id: "015"
title: "Git hooks as an alternative trigger mechanism for lifecycle events"
type: web
url: "https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks"
fetched: 2026-03-15T03:05:00Z
hash: "pending"
---

# Git Hooks as Trigger Mechanism

Git hooks are scripts that execute automatically at specific points in the Git workflow. Relevant hooks for lifecycle event detection:

## Candidate hooks

- **post-commit**: Runs after a commit is created. Can diff HEAD vs HEAD~1 to detect frontmatter changes. Reliable (one event per commit), but delayed (only fires on commit, not on save).
- **post-checkout**: Runs after `git checkout`. Useful for detecting branch switches that change artifact state.
- **post-merge**: Runs after a merge completes. Can detect frontmatter changes from merged branches.
- **post-rewrite**: Runs after `git commit --amend` or `git rebase`. Catches rewritten history.

## Advantages over filesystem watching

- **No duplicate events**: One commit = one hook invocation.
- **Atomic state changes**: The diff between HEAD and HEAD~1 gives you exactly what changed, not a stream of intermediate saves.
- **Git-native diffing**: `git diff HEAD~1 -- docs/` gives you the exact frontmatter changes.
- **No debouncing needed**: The commit boundary is the natural debounce.

## Disadvantages

- **Delayed**: The operator must commit before the hook fires. Dragging a card in daymark and seeing swain react requires a commit step in between (unless daymark auto-commits, which introduces its own complexity).
- **Not tool-agnostic for real-time**: If the operator edits frontmatter in vim and saves but doesn't commit, nothing happens until they commit.
- **Hook distribution**: Git hooks aren't committed to the repo by default (they live in `.git/hooks/`). Swain would need a setup step (e.g., `core.hooksPath` pointing to a committed directory, or swain-doctor installing hooks).

## Hybrid approach

Use filesystem watching for **real-time reactivity** (daymark drag-and-drop triggers immediately) and git hooks for **reliability** (post-commit validates that the frontmatter state on disk matches what was committed, catches any missed events).

## Relevance to reactive loop

Git hooks are a viable **secondary** trigger mechanism but insufficient as the sole trigger for the daymark → swain-status → swain-do loop. The real-time requirement (drag a card, see swain react) demands filesystem watching. Git hooks add a reliability backstop.
