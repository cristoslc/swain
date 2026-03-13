# Auditing Artifacts

Audits have two phases: a **pre-scan** that fixes structural problems, then **parallel audit agents** that inspect the corrected state.

## Phase 1: Pre-scan (run first, before agents)

Run `scripts/specwatch.sh scan` synchronously. This performs:
1. **Stale reference detection** — broken markdown links and unresolvable frontmatter refs
2. **Artifact/tk sync check** — mismatches between artifact status and tk item state (if tk is in use)

Fix any issues surfaced by the scan before proceeding. For stale refs, update links or frontmatter. For tk sync mismatches, invoke swain-do to reconcile (close stale tk items or transition artifacts). Run `specwatch.sh phase-fix` to move any artifacts whose phase directory doesn't match their frontmatter status.

Only proceed to Phase 2 once the pre-scan is clean (or all actionable issues are resolved).

## Phase 2: Parallel audit agents

Spawn seven agents in a single turn:

| Agent | Responsibility |
|-------|---------------|
| **Lifecycle auditor** | Check every artifact in `docs/` for valid status field, lifecycle table with hash stamps, and matching row in the appropriate `list-<type>.md` index. |
| **Cross-reference checker** | Verify all `parent-*`, `depends-on`, `linked-*`, and `addresses` frontmatter values resolve to existing artifact files. Flag dangling references. |
| **Naming & structure validator** | Confirm directory/file names follow `(TYPE-NNN)-Title` convention, templates have required frontmatter fields, and folder-type artifacts contain a primary `.md` file. |
| **Phase/folder alignment** | Confirm `specwatch.sh phase-fix` from the pre-scan left no remaining mismatches. Flag any artifacts that could not be auto-moved. |
| **Dependency coherence auditor** | Validate that `depends-on` edges are logically sound, not just syntactically valid. See checks below. |
| **ADR compliance auditor** | Run `scripts/adr-check.sh` against every non-ADR artifact in `docs/`. Collect all RELEVANT, DEAD_REF, and stale findings into a single table. For each RELEVANT finding, read both documents and assess content-level compliance (see [adr-check-guide.md](adr-check-guide.md)). |
| **Alignment auditor** | For each active Vision, run `specgraph.sh scope` on every descendant and check semantic alignment per [alignment-checking.md](alignment-checking.md). See checks below. |

### Dependency coherence auditor

The dependency coherence auditor catches cases where the graph *exists* but is *wrong*. The cross-reference checker confirms targets resolve to real files; this agent checks whether those edges still make sense. Specific checks:

1. **Dead-end dependencies** — `depends-on` targets an Abandoned or Rejected artifact. The dependency can never be satisfied; flag it for removal or replacement.
2. **Orphaned satisfied dependencies** — `depends-on` targets a Complete/Implemented artifact but the dependent is still in Draft/Proposed. The blocker is resolved — is the dependent actually stalled for a different reason, or should it advance?
3. **Phase-inversion** — A dependent artifact is in a *later* lifecycle phase than something it supposedly depends on (e.g., an Implemented spec that `depends-on` a Draft spike). This suggests the edge was never cleaned up or was added in error.
4. **Content-drift** — Read both artifacts and assess whether the dependency relationship still holds given what each artifact actually describes. Artifacts evolve; an edge that made sense at creation time may no longer reflect reality. Flag edges where the content of the two artifacts has no apparent logical connection.
5. **Missing implicit dependencies** — Scan artifact bodies for references to other artifact IDs (e.g., "as decided in ADR-001" or "builds on SPIKE-003") that are *not* declared in `depends-on` or `linked-*` frontmatter. These are shadow dependencies that should be formalized or explicitly noted as informational.

For checks 4 and 5, the agent must actually read artifact content — frontmatter alone is not sufficient. Present findings as a table with: source artifact, target artifact, check type, evidence (quote or summary), and recommended action (remove edge, add edge, update frontmatter, or investigate).

### Alignment auditor

The alignment auditor checks that artifacts are semantically oriented toward the same goal. It requires reading artifact content — frontmatter alone is not sufficient. Procedure:

1. Run `specgraph.sh overview --all` to identify all active Visions.
2. For each active Vision, use `specgraph.sh scope` on every non-terminal descendant (Epics, SPECs, Stories under that Vision).
3. For each artifact, assess alignment per [alignment-checking.md](alignment-checking.md):
   - Read the Vision's goal (the "North Star")
   - Read the artifact content
   - Check each relationship level (Vision↔Epic, Epic↔SPEC, etc.)
4. Report findings with severity (MISALIGNED, SCOPE_LEAK, GOAL_DRIFT, STALE_ALIGNMENT, IMPLICIT_CONFLICT).

Present findings as a table with: source artifact, related artifact, finding type, evidence (quote or summary), and recommended action. Apply the noise reduction rules from alignment-checking.md — only report findings that would change what a developer decides.

### Reporting

Each agent reports gaps as a structured table with file path, issue type, and missing/invalid field. Merge the tables into a single audit report. Always include a 1-2 sentence summary of each artifact (not just its title) in result tables.

**Enforce definitions, not current layout.** The artifact definition files (in `references/`) are the source of truth for folder structure. If the repo's current layout diverges from the definitions (e.g., epics in a flat directory instead of phase subdirectories), the audit should flag misplaced files and propose `git mv` commands to bring them into compliance. Do not silently adopt a non-standard layout just because it already exists.
