# Trove Integration

When research-heavy artifacts enter their active/research phase, check for existing troves and offer to create or reuse one.

## Research phase hook

This hook fires during phase transitions for these artifact types:

| Artifact | Trigger phase | When to check |
|----------|--------------|---------------|
| **Spike** | Proposed -> Active | Investigation is starting — research sources are most valuable here |
| **ADR** | At creation or Proposed -> Active | Decision needs supporting research |
| **Vision** | At creation | Market research and landscape analysis |
| **Epic** | At creation or Proposed -> Active | Scoping benefits from prior research |

When the trigger fires:

1. Scan `docs/troves/*/manifest.yaml` for troves whose tags overlap with the artifact's topic (infer tags from the artifact title, keywords, and linked artifacts).
2. If matching troves exist, present them:
   > Found N trove(s) that may be relevant:
   > - `websocket-vs-sse` (5 sources, refreshed 2026-03-01) — tags: real-time, websocket, sse
   >
   > Link an existing trove, create a new one, or skip?
3. If no matches: "No existing troves match this topic. Want to create one with swain-search?"
4. If the user wants a trove, invoke the **swain-search** skill (via the Skill tool) to create or extend one.
5. After the trove is committed, update the artifact's `trove` frontmatter field with `<trove-id>@<commit-hash>`.

## Back-link maintenance

When an artifact's `trove` frontmatter is set or changed:

1. Read the trove's `manifest.yaml`
2. Add or update the `referenced-by` entry for this artifact:
   ```yaml
   referenced-by:
     - artifact: SPIKE-001
       commit: abc1234
   ```
3. Write the updated manifest

This keeps the trove's manifest in sync with which artifacts depend on it. Back-links enable trovewatch to detect when a trove is no longer referenced and can be archived.
