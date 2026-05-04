---
id: s2spd-1cbi
status: closed
deps: [s2spd-dn7k]
links: []
created: 2026-04-13T13:30:51Z
type: task
priority: 2
assignee: cristos
parent: s2spd-5lo8
tags: [spec:SPEC-297]
---
# Update SKILL.md: agent renders purpose from greeting JSON (no write)

In skills/swain-init/SKILL.md Step 7.4 and skills/swain-session/SKILL.md 'Session purpose text' section: remove instruction that agent parses prompt and calls swain-bookmark.sh. Replace with: 'greeting JSON includes a purpose field — display it as **Session purpose:** <text>.' Agent is consumer, not writer.


## Notes

**2026-04-13T14:24:12Z**

Updated Step 7.4 in swain-init/SKILL.md and 'Session purpose text' section in swain-session/SKILL.md. Agent now reads greeting JSON .purpose field and displays; greeting script owns extraction + bookmark write. Agent no longer parses initial prompt.
