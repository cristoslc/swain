# Plan Ingestion (superpowers integration)

When a superpowers plan file exists (produced by the `writing-plans` skill), use the ingestion script instead of manually decomposing tasks. The script parses the plan's `### Task N:` blocks and registers them in tk with full spec lineage.

The ingest helper lives at `skills/swain-do/scripts/ingest-plan.py`.

## When to use

- A superpowers plan file exists at `docs/plans/YYYY-MM-DD-<name>.md`
- The plan follows the `writing-plans` format (header + `### Task N:` blocks)
- You have an origin-ref artifact ID to link the plan to

## Usage

```bash
# Parse and register in tk
uv run python3 skills/swain-do/scripts/ingest-plan.py <plan-file> <origin-ref>

# Parse only (preview without creating tk tasks)
uv run python3 skills/swain-do/scripts/ingest-plan.py <plan-file> <origin-ref> --dry-run

# With additional tags
uv run python3 skills/swain-do/scripts/ingest-plan.py <plan-file> <origin-ref> --tags epic:EPIC-009
```

## What it does

1. Parses the plan header (title, goal, architecture, tech stack)
2. Splits on `### Task N:` boundaries
3. Creates a tk epic with `--external-ref <origin-ref>`
4. Creates child tasks with `--tags spec:<origin-ref>` and full task body as description
5. Wires sequential dependencies (Task N+1 depends on Task N)

## When NOT to use

- The plan file doesn't follow superpowers format — fall back to manual task breakdown
- You need non-sequential dependencies — use the script, then adjust deps manually with `tk dep`
- The plan is very short (1-2 tasks) — manual creation is faster
