# Legacy Skill Cleanup

Clean up skill directories that have been superseded by renames or retired entirely. Read the legacy mapping from `references/legacy-skills.json`.

## Renamed skills

For each entry in the `renamed` map, check both `.claude/skills/` and `.agents/skills/`:

1. Check whether `<skills-root>/<old-name>/` exists.
2. If it does NOT exist, skip (nothing to clean).
3. If it exists, check whether `<skills-root>/<new-name>/` also exists. If the replacement is missing, **skip and warn** — the update may not have completed:
   > Skipping cleanup of `<old-name>` — its replacement `<new-name>` is not installed.
4. If both exist, **fingerprint check**: read `<skills-root>/<old-name>/SKILL.md` and check whether its content matches ANY of the fingerprints listed in `legacy-skills.json`. Specifically, grep the file for each fingerprint string — if at least one matches, the skill is confirmed to be a swain skill.
5. If no fingerprint matches, **skip and warn** — this may be a third-party skill with the same name:
   > Skipping cleanup of `<skills-root>/<old-name>/` — it does not appear to be a swain skill (no fingerprint match). If this is a stale swain skill, delete it manually.
6. If fingerprint matches and replacement exists, **delete the old directory**:
   ```bash
   rm -rf <skills-root>/<old-name>
   ```
   Tell the user:
   > Removed legacy skill `<skills-root>/<old-name>/` (replaced by `<new-name>`).

## Retired skills

For each entry in the `retired` map (pre-swain skills absorbed into the ecosystem), check both `.claude/skills/` and `.agents/skills/`:

1. Check whether `<skills-root>/<old-name>/` exists.
2. If it does NOT exist, skip (nothing to clean).
3. If it exists, **fingerprint check**: same as for renamed skills — read `<skills-root>/<old-name>/SKILL.md` and check whether its content matches ANY fingerprint in `legacy-skills.json`.
4. If no fingerprint matches, **skip and warn**:
   > Skipping cleanup of `<skills-root>/<old-name>/` — it does not appear to be a known pre-swain skill (no fingerprint match). Delete manually if stale.
5. If fingerprint matches, **delete the old directory**:
   ```bash
   rm -rf <skills-root>/<old-name>
   ```
   Tell the user:
   > Removed retired pre-swain skill `<skills-root>/<old-name>/` (functionality now in `<absorbed-by>`).

After processing all entries, check whether the governance block in the context file references old skill names. If the governance block (between `<!-- swain governance -->` and `<!-- end swain governance -->`) contains any old-name from the `renamed` map, delete the entire block (inclusive of markers) and proceed to Governance injection to re-inject a fresh copy with current names.
