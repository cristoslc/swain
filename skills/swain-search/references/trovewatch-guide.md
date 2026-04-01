# trovewatch Guide

Monitor troves for size, freshness, and consistency.

## Usage

```bash
# Check all troves for issues
bash scripts/trovewatch.sh scan

# Summary of all troves
bash scripts/trovewatch.sh status
```

## What it checks

### scan

| Check | What triggers a warning |
|-------|------------------------|
| **Source count** | Trove has more sources than `max_sources_per_trove` (default: 20) |
| **Trove size** | Trove directory exceeds `max_trove_size_mb` (default: 5MB) |
| **Freshness** | Source age exceeds its TTL * `freshness_multiplier` (default: 1.5x) |
| **Missing files** | Manifest references a source file that doesn't exist |
| **Orphaned files** | Source file exists but isn't listed in manifest |
| **Missing synthesis** | Trove has no synthesis.md |

Exit code 0 = all healthy, 1 = warnings found.

Output goes to stdout (summary) and `.agents/trovewatch.log` (details).

### status

One-line summary per trove: source count, size, last refreshed date, tags.

## Configuration

Create `.agents/trovewatch.vars.json` to override defaults:

```json
{
  "max_sources_per_trove": 30,
  "max_trove_size_mb": 10,
  "freshness_multiplier": 2.0
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `max_sources_per_trove` | 20 | Warn when trove exceeds this many sources |
| `max_trove_size_mb` | 5 | Warn when trove directory exceeds this size |
| `freshness_multiplier` | 1.5 | Source is flagged stale when age > TTL * multiplier |

## Integration with swain-search

After extending or refreshing a trove, run `trovewatch.sh scan` to verify the trove is healthy. The swain-search skill can invoke this automatically after collection.
