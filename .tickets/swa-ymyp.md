---
id: swa-ymyp
status: open
deps: []
links: []
created: 2026-03-13T04:26:27Z
type: feature
priority: 2
assignee: Cristos L-C
---
# Normalize artifact frontmatter: linked-artifacts and depends-on-artifacts

Current state: artifact types use inconsistent per-type link fields (linked-research, linked-adrs, linked-epics, linked-specs) alongside a generic depends-on field. Spikes have depends-on in their template but it is always empty — spikes have no blocking dependencies, only informational relationships.

Proposed normalization:
- Replace all per-type linked-* fields (linked-research, linked-adrs, linked-epics, linked-specs) with a single linked-artifacts list
- Rename depends-on to depends-on-artifacts for clarity
- Remove depends-on from the spike template entirely (spikes only have linked-artifacts)
- Update all templates and existing artifact frontmatter to match

Scope: spike-template.md.template, spec-template.md.template, adr-template.md.template, epic-template.md.template, all existing artifact .md files in docs/, specgraph.sh (reads these fields), specwatch.sh (validates them)


## Notes

**2026-03-13T04:29:00Z**

Linked to SPEC-009: Normalize Artifact Frontmatter Relationships
