---
id: swa-x1hs
status: closed
deps: [swa-kfxm]
links: []
created: 2026-03-14T06:23:13Z
type: task
priority: 2
assignee: cristos
parent: swa-5aq2
tags: [spec:SPEC-038]
---
# Add track validation to swain-design audit

Add check to naming & structure validator: every artifact must have a track field matching implementable|container|standing. Flag missing or invalid track fields as errors


## Notes

**2026-03-14T06:33:00Z**

Completed: added track field validation to Naming & structure validator in auditing.md. Validator now checks every artifact has a track field set to implementable, container, or standing per lifecycle-tracks.md. Missing or invalid values flagged as errors.

**2026-03-14T06:44:28Z**

Completed: TestIsResolvedWithTrack class added to test_resolved.py — 9 tests covering explicit track parameter, standing track resolution, container track, implementable track, and None track fallback. All pass.
