---
name: swain-push
description: "Stage all changes, generate a descriptive commit message from the diff, commit, and push to the current branch's upstream."
user-invocable: true
allowed-tools: Bash, Read, Edit
metadata:
  short-description: Stage, commit, and push (deprecated alias for swain-sync)
  version: 2.0.0
  author: cristos
  license: MIT
  source: swain
---
<!-- swain-model-hint: sonnet, effort: low -->

**Deprecation notice:** `swain-push` is now an alias for `swain-sync`. Use `/swain sync` or `/swain-sync` instead.

Emit the deprecation warning to the user, then invoke the `swain-sync` skill with all arguments forwarded.
