---
id: swa-rh19
status: open
deps: [swa-sc1g]
links: []
created: 2026-03-20T00:42:37Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 11: Verify adr-check.sh handles TRAIN artifacts

**Files:**
- Verify: `.claude/skills/swain-design/scripts/adr-check.sh`

`adr-check.sh` accepts an artifact path as its `$1` argument — it doesn't maintain its own list of artifact directories. Any artifact file can be passed to it. The gating of which directories trigger ADR checks lives in `swain-sync/SKILL.md` (the ADR compliance path list updated in Task 12). No code changes needed in `adr-check.sh` itself.

- [ ] **Step 1: Verify adr-check.sh works with a TRAIN path**

```bash
# Create a minimal test file
mkdir -p docs/train/Active/test-train
echo -e "---\ntitle: test\nartifact: TRAIN-999\n---\n# Test" > docs/train/Active/test-train/TRAIN-999.md
bash .claude/skills/swain-design/scripts/adr-check.sh docs/train/Active/test-train/TRAIN-999.md
rm -rf docs/train/Active/test-train
```

Expected: `OK TRAIN-999: no ADR compliance findings`

