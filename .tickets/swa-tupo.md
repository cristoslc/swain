---
id: swa-tupo
status: open
deps: [swa-9wuc]
links: []
created: 2026-03-20T15:09:56Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-f0pa
tags: [spec:SPEC-103]
---
# Integrate link resolver into swain-design artifact creation

Update swain-design SKILL.md artifact creation workflow: after writing body text, resolve artifact ID references to relative markdown links. Frontmatter stays as plain IDs. Add instruction to call resolve-artifact-link.sh for each ID pattern found in body text.

