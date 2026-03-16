---
id: swa-b7c9
status: closed
deps: [swa-sikr]
links: []
created: 2026-03-16T19:17:41Z
type: task
priority: 1
assignee: cristos
parent: swa-1fd2
tags: [spec:SPIKE-025, spec:SPIKE-025]
---
# Task 5: Write integration sketch and close spike

**Files:**
- Modify: `docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md`

Show how the recommended mechanism plugs into EPIC-024's filter chain.

- [ ] **Step 1: Write the integration sketch**

Append a `## Integration Sketch` section showing:
- Where in the filter chain (step 3 of EPIC-024) the auth check runs
- What the config shape looks like for the recommended mechanism (extending the `intake.authMethod` field in `swain.settings.json`)
- Pseudocode for the auth validation function (deterministic, no LLM)
- How the operator submits an authenticated issue (step-by-step)
- How a failed auth check routes to the slow path (not rejection)

- [ ] **Step 2: Update spike status and lifecycle**

Update the spike frontmatter:
- `status: Proposed` → `status: Active` (or `Complete` if all findings are documented)
- Add lifecycle entry for research completion

- [ ] **Step 3: Commit**

```bash
git add "docs/research/Proposed/(SPIKE-025)-Authentication-For-Public-Intake-Channels/(SPIKE-025)-Authentication-For-Public-Intake-Channels.md"
git commit -m "research(SPIKE-025): integration sketch and spike completion"
```

- [ ] **Step 4: Verify all expected outputs are present**

Check the spike artifact contains all four expected outputs:
1. GO/NO-GO on TOTP-in-the-clear for public repos
2. Recommended auth mechanism with rationale
3. Threat model summary for the chosen mechanism
4. Integration sketch showing how the auth check fits into the filter chain

If any are missing, fill gaps before closing.


## Notes

**2026-03-16T19:36:10Z**

Completed: integration sketch with filter chain placement, config shape, validation pseudocode, operator workflow, and fallback routing. Spike moved to Complete.
