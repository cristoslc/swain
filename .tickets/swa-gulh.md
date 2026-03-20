---
id: swa-gulh
status: open
deps: [swa-czla]
links: []
created: 2026-03-20T00:42:37Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-kd71
tags: [spec:SPEC-091]
---
# Task 14: Create a test TRAIN artifact and verify full pipeline

**Files:**
- Create: `docs/train/Active/(TRAIN-001)-Test-TRAIN/` (temporary, for verification)

- [ ] **Step 1: Create a test TRAIN artifact with enriched linked-artifacts**

Create `docs/train/Active/(TRAIN-001)-Test-TRAIN/(TRAIN-001)-Test-TRAIN.md` using the template. Link it to an existing SPEC with a stale commit pin (use an old commit hash).

- [ ] **Step 2: Verify chart.sh build includes TRAIN node**

```bash
bash .claude/skills/swain-design/scripts/chart.sh build
```

Expected: Node count increases by 1. TRAIN-001 appears in the graph.

- [ ] **Step 3: Verify train-check.sh detects staleness**

```bash
bash .claude/skills/swain-design/scripts/train-check.sh
```

Expected: `STALE: TRAIN-001 → SPEC-NNN (pinned: ..., current: ..., N commits behind)`

- [ ] **Step 4: Verify specwatch scan includes train-check**

```bash
bash .claude/skills/swain-design/scripts/specwatch.sh scan
```

Expected: Scan output includes train-check findings.

- [ ] **Step 5: Verify adr-check.sh processes the TRAIN**

```bash
bash .claude/skills/swain-design/scripts/adr-check.sh "docs/train/Active/(TRAIN-001)-Test-TRAIN/(TRAIN-001)-Test-TRAIN.md"
```

Expected: `OK TRAIN-001: no ADR compliance findings`

- [ ] **Step 6: Verify rebuild-index.sh handles train type**

```bash
bash .claude/skills/swain-design/scripts/rebuild-index.sh train
```

Expected: Creates `docs/train/list-train.md` with TRAIN-001 listed.

- [ ] **Step 7: Clean up test artifact**

```bash
rm -rf docs/train/Active/(TRAIN-001)-Test-TRAIN/
rm -f docs/train/list-train.md
```

- [ ] **Step 8: Final commit**

```bash
git add -A
git commit -m "feat(SPEC-091): TRAIN artifact type complete — definition, template, parser, staleness detection, tooling integration"
```

