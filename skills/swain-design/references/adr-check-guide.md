# ADR Compliance Check Guide

Reference for interpreting `adr-check.sh` output and performing content-level review.

## Interpreting output

The script outputs structured findings:

- **`RELEVANT`** — An Adopted ADR's scope overlaps the artifact. Read the ADR's Decision section and verify the artifact's content doesn't contradict it. Common violations: proposing an approach rejected in "Alternatives Considered," ignoring constraints from "Consequences," or (ADR-on-ADR) contradicting an Adopted decision without explicitly superseding it.
- **`DEAD_REF`** — The artifact references a Retired or Superseded ADR. If superseded, review against the replacement. If retired with no replacement, assess whether the artifact's design still holds.
- **`stale` flag on RELEVANT** — The ADR was adopted after the artifact was last updated. The artifact may need revision to align with the newer decision.

Content-level review (does the artifact actually comply?) requires reading both documents — the script identifies *which* ADRs to check, the agent applies judgment.

## Content-level review procedure

For each RELEVANT finding:

1. Read the ADR's **Decision** and **Consequences** sections.
2. Read the artifact's content (body, not just frontmatter).
3. Check for:
   - Approaches that were explicitly rejected in the ADR's "Alternatives Considered"
   - Constraints or trade-offs from "Consequences" that the artifact ignores
   - Scope duplication — artifact covers ground already decided by the ADR without referencing it
   - *(ADR-on-ADR)* Contradictions with an existing Adopted ADR that aren't framed as explicit supersession

## Updating linkage

If the script surfaces a relevant ADR not already cross-referenced, add it:
- `linked-adrs` for types that have it (SPEC, DESIGN)
- `depends-on` for ADR-on-ADR relationships
- A body mention ("per ADR-NNN") for types without a `linked-adrs` field (STORY, BUG, JOURNEY, PERSONA, RUNBOOK)
