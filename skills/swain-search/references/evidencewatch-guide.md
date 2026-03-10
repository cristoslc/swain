# evidencewatch Guide

Monitor evidence pools for size, freshness, and consistency.

## Usage

```bash
# Check all pools for issues
bash skills/swain-search/scripts/evidencewatch.sh scan

# Summary of all pools
bash skills/swain-search/scripts/evidencewatch.sh status
```

## What it checks

### scan

| Check | What triggers a warning |
|-------|------------------------|
| **Source count** | Pool has more sources than `max_sources_per_pool` (default: 20) |
| **Pool size** | Pool directory exceeds `max_pool_size_mb` (default: 5MB) |
| **Freshness** | Source age exceeds its TTL * `freshness_multiplier` (default: 1.5x) |
| **Missing files** | Manifest references a source file that doesn't exist |
| **Orphaned files** | Source file exists but isn't listed in manifest |
| **Missing synthesis** | Pool has no synthesis.md |

Exit code 0 = all healthy, 1 = warnings found.

Output goes to stdout (summary) and `.agents/evidencewatch.log` (details).

### status

One-line summary per pool: source count, size, last refreshed date, tags.

## Configuration

Create `.agents/evidencewatch.vars.json` to override defaults:

```json
{
  "max_sources_per_pool": 30,
  "max_pool_size_mb": 10,
  "freshness_multiplier": 2.0
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `max_sources_per_pool` | 20 | Warn when pool exceeds this many sources |
| `max_pool_size_mb` | 5 | Warn when pool directory exceeds this size |
| `freshness_multiplier` | 1.5 | Source is flagged stale when age > TTL * multiplier |

## Integration with swain-search

After extending or refreshing a pool, run `evidencewatch.sh scan` to verify the pool is healthy. The swain-search skill can invoke this automatically after collection.
