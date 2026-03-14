# Lifecycle Tracks

Three-track lifecycle model from ADR-003. Each artifact type belongs to exactly one track. The track determines what phases the artifact passes through, what its terminal states are, and when it is considered **resolved** (no longer requiring action).

## Track Definitions

| Track | Artifact Types | Phases (ordered) | Terminal Phases | Resolution Rule |
|-------|---------------|-----------------|-----------------|-----------------|
| `implementable` | SPEC | Proposed → Ready → Active → Complete | Complete, Abandoned, Retired, Superseded | Status equals a terminal phase |
| `container` | EPIC, SPIKE | Proposed → Active → Complete | Complete, Abandoned, Retired, Superseded | Status equals a terminal phase |
| `standing` | VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN | Proposed → Active → (Retired \| Superseded) | Retired, Superseded | Active OR status equals a terminal phase |

Universal terminal states applicable to all tracks: `Abandoned`, `Retired`, `Superseded`.

## Resolution Rules

An artifact is **resolved** (treated as done by specgraph, excluded from ready/next output) when:

- `implementable` track: `status` is `Complete`, `Abandoned`, `Retired`, or `Superseded`
- `container` track: `status` is `Complete`, `Abandoned`, `Retired`, or `Superseded`
- `standing` track: `status` is `Active`, `Retired`, or `Superseded` (Active is the live/adopted state — it is not "work to do")

## Track Field in Artifacts

Every artifact's YAML frontmatter includes a `track` field:

```yaml
track: implementable   # SPEC
track: container       # EPIC, SPIKE
track: standing        # VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN
```

When the `track` field is absent (legacy artifacts), specgraph infers the track from the artifact type using the table above and emits a `TRACK_MISSING` warning.

## Relationship to ADR-003

This file is a machine-readable companion to ADR-003. It should change only when ADR-003 is superseded. Do not edit the track definitions here independently — raise an ADR update first.
