# Trove Redesign: Rename Evidence Pools & Add Hierarchical Source Support

**Date:** 2026-03-15
**Status:** Draft
**Addresses:** GitHub #61 (rename "evidence pool"), GitHub #63 (evidence pools need depth)
**Approach:** Single coherent redesign with backward-compatible migration (Approach C)

## Summary

Rename "evidence pool" to "trove" across the swain skill ecosystem and restructure
source storage from flat numbered files to source-id-grouped directories that support
hierarchical content mirroring. Existing pools migrate via rename and directory
restructure without forced content reorganization.

## Motivation

"Evidence pool" no longer describes the full scope of what swain-search produces.
When ingesting a repository tree or documentation site, the agent is building a
reference library, not gathering evidence for analysis. The term misleads about
both purpose (evidence implies adversarial hypothesis-testing) and structure (pool
implies a flat, undifferentiated container).

Separately, swain-search flattens all sources to `001-slug.md`, `002-slug.md`
regardless of whether the source material has meaningful hierarchy. Repo trees,
documentation sites with sections, and multi-file projects lose their navigational
structure, making the ingested content harder to browse and understand in context.

## Terminology

| Old | New |
|-----|-----|
| evidence pool | trove |
| evidence-pool (frontmatter key) | trove |
| `docs/evidence-pools/<id>/` | `docs/troves/<id>/` |
| `evidence-pool: <id>@<hash>` | `trove: <id>@<hash>` |

The skill name stays `swain-search` — the skill does the searching, the trove is
what it produces.

## Directory Structure

```
docs/troves/<trove-id>/
  manifest.yaml
  synthesis.md
  sources/
    <source-id>/                         # hierarchical source (repo, doc site)
      original/tree/structure/
        file.md
    <source-id>/                         # flat source (web page, transcript)
      <source-id>.md
```

### Source ID Rules

- Must be a slug: lowercase, hyphenated, human-readable
- Descriptive enough that the source is meaningful when copied out of context
- When a slug collides within a trove, append a wordlist-pair disambiguator with
  a double-underscore separator: `cognee-meta-skill-repo__amber-finch`
- For flat sources, the file is `<source-id>/<source-id>.md`
- For hierarchical sources, the directory is `<source-id>/` with the original
  tree mirrored inside

### Portability

Every source is a self-contained directory named by its slug. Sources can be
copied, symlinked, or moved outside the trove and remain identifiable without
their manifest.

### Hierarchical Mirroring

- Default: mirror the full source tree
- When the source is large (agent judgment — thousands of files in a monorepo),
  ingest selectively based on research purpose
- The manifest records what was included; the `highlights` array marks key files
- Selective ingestion sets `selective: true` in the manifest entry so that
  tooling (evidencewatch) does not flag missing files as errors

### Source Grouping

Each source gets its own namespace under `sources/<source-id>/`. A trove may
contain sources from multiple origins — repos, web articles, media transcripts.
Repos get their tree mirrored inside their source-id directory; web articles and
transcripts get a single `<source-id>.md`. The source-id ties back to the
manifest entry.

## Manifest Schema

### Trove-level fields

| Field | Type | Description |
|-------|------|-------------|
| `trove` | string | The trove ID (renamed from `pool`) |
| `created` | ISO 8601 | When the trove was created |
| `refreshed` | ISO 8601 | Last refresh timestamp |
| `tags` | string[] | Discovery tags |
| `referenced-by` | object[] | Artifacts that reference this trove |

### Per-source fields

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `source-id` | renamed from `id` | string | Slug matching the directory name under `sources/` |
| `slug` | removed | — | Redundant with `source-id` |
| `type` | expanded | string | `web`, `forum`, `document`, `media`, `local`, `repository`, `documentation-site` |
| `url` | unchanged | string | Source URL or path |
| `fetched` | unchanged | ISO 8601 | When the source was fetched |
| `hash` | standardized | string | Bare hex SHA-256 digest (no `sha256:` prefix) |
| `freshness-ttl` | unchanged | string | Optional TTL override |
| `highlights` | **new** | string[] | Paths relative to the source-id directory marking key files identified during ingestion |
| `selective` | **new** | boolean | Default false. When true, the source was selectively ingested |

## Wordlist Disambiguator

- Curated wordlist of ~2000 short (3-7 char), thematically neutral words
- Shipped as `skills/swain-search/references/wordlist.txt`, one word per line
- When a source-id slug collides within a trove, two words are drawn at random,
  hyphen-joined, and appended after a double-underscore: `<slug>__word1-word2`
- Collision probability with 2000-word pairs: ~4 million combinations
- The wordlist is curated during implementation (minimum 1000 entries)
- **Fallback:** If the wordlist file is missing or empty, fall back to a random
  4-character hex suffix (e.g., `<slug>__a3f8`)

## Migration

### Migration script

Shipped with swain-search, invokable by swain-doctor. Steps:

1. **Rename directory:** `docs/evidence-pools/` to `docs/troves/`
2. **Restructure sources:** For each existing pool, move `sources/NNN-slug.md`
   to `sources/NNN-slug/NNN-slug.md`. The full old filename stem (e.g.,
   `001-mdn-websocket-api`) becomes the `source-id`. Old numbered prefixes are
   preserved as-is — no forced renaming, but the agent can rename to a cleaner
   slug on the next `extend` or `refresh`.
3. **Update manifest:** Rename `pool` to `trove`. For each source entry, set
   `source-id` to the old `slug` field value prefixed with the old `id` (e.g.,
   `id: "001"` + `slug: "mdn-websocket-api"` becomes
   `source-id: "001-mdn-websocket-api"`). Remove the old `id` and `slug` fields.
   Set `highlights: []`, set `selective: false`.
4. **Update artifact frontmatter:** `evidence-pool: <id>@<hash>` to
   `trove: <id>@<hash>` across all artifact files.
5. **Update skill references:** swain-search SKILL.md, swain-design integration
   hook, evidencewatch script.

### Non-destructive and idempotent

The migration script moves, never deletes. Git tracks renames. Recovery via
`git checkout` if anything goes wrong. The script is idempotent: if
`docs/troves/` already exists and `docs/evidence-pools/` does not, it skips
the directory rename. If source directories are already restructured, it skips
those too. Each step checks current state before acting.

### swain-doctor detection

- `docs/evidence-pools/` exists: warn and offer migration
- Any artifact frontmatter contains `evidence-pool:`: warn and offer migration
- Both `docs/troves/` and `docs/evidence-pools/` exist: warn about incomplete
  migration

## Skill Changes

### swain-search SKILL.md

- All "evidence pool" references become "trove"
- Update SKILL.md frontmatter: `description` and `short-description` fields
- Update path references: report template (`docs/evidence-pools/<pool-id>/` to
  `docs/troves/<trove-id>/`), discover-mode scan glob
  (`docs/evidence-pools/*/manifest.yaml` to `docs/troves/*/manifest.yaml`),
  and `evidence-pool:` frontmatter format strings
- Source creation: slug-based IDs, `<source-id>/<source-id>.md` for flat,
  mirrored tree for hierarchical
- Wordlist pair disambiguator with `__` separator on slug collision
- New source types: `repository`, `documentation-site` with hierarchy-mirroring
- Selective ingestion: mirror full tree by default, be selective for large
  sources, set `selective: true`
- `highlights` populated during ingestion

### swain-search references

- `normalization-formats.md`: update all frontmatter examples from sequential
  IDs (`source-id: "001"`) to slug-based IDs; update `type` enum to include
  `local`, `repository`, `documentation-site`
- `manifest-schema.md`: update schema to reflect new fields and removed fields

### swain-design integration

- `evidence-pool-integration.md` renamed to `trove-integration.md`
- All internal references updated: path globs (`docs/evidence-pools/*/manifest.yaml`
  to `docs/troves/*/manifest.yaml`), frontmatter field name (`evidence-pool` to
  `trove`), and user-facing strings ("evidence pool" to "trove")
- Tag-based discovery searches `docs/troves/*/manifest.yaml`

### evidencewatch

- Scans `docs/troves/` instead of `docs/evidence-pools/`
- **Structural change:** File-discovery logic must walk `sources/<source-id>/`
  directories instead of looking for `NNN-slug.md` flat files. Orphan detection
  and missing-file checks must understand the new directory-per-source layout.
- Sources with `selective: true` skip missing-file warnings
- Existing checks (size, freshness, missing synthesis) unchanged in logic

### swain-doctor

- New migration detection (see Migration section)
- Runs migration script on user confirmation

### No changes needed

swain-status, swain-do, swain-sync, swain-session, and all other skills. Troves
are consumed through swain-search and swain-design only.

## Acceptance Criteria

1. `docs/troves/` is the canonical storage path for all troves
2. New troves created by swain-search use slug-based source IDs with the
   hierarchical directory structure
3. Repository and documentation-site sources mirror the original tree under
   their source-id directory
4. Flat sources (web, forum, media, document) use `<source-id>/<source-id>.md`
5. Manifest schema includes `source-id`, `highlights`, and `selective` fields
6. Wordlist disambiguator appends `__word1-word2` on slug collision
7. Wordlist contains at least 1000 entries; hex fallback when wordlist is missing
8. Migration script converts existing evidence pools to troves non-destructively
9. Migration script is idempotent — running it when already migrated is a no-op
10. swain-doctor detects unmigrated evidence pools and offers migration
11. All skill references updated: swain-search SKILL.md, normalization-formats.md,
    manifest-schema.md, trove-integration.md, evidencewatch
12. Existing troves with flat structure (migrated from evidence pools) remain
    valid and functional — extend mode works alongside old-format sources
