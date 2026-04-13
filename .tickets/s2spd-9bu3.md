---
id: s2spd-9bu3
status: closed
deps: []
links: []
created: 2026-04-13T13:30:51Z
type: task
priority: 2
assignee: cristos
parent: s2spd-5lo8
tags: [spec:SPEC-297]
---
# Always export SWAIN_PURPOSE in launcher templates

Edit skills/swain-init/templates/launchers/*/swain.{zsh,bash,fish}: for Tier 1 runtimes (claude/gemini/codex/copilot), export SWAIN_PURPOSE=<text> IN ADDITION to passing the inline prompt. Crush already does this. This makes greeting's deterministic path work for all runtimes.


## Notes

**2026-04-13T14:23:39Z**

Main swain script now always exports SWAIN_PURPOSE (not only for crush). All 12 Tier 1 launcher templates (claude/codex/copilot/gemini × zsh/bash/fish) updated to export SWAIN_PURPOSE alongside the inline prompt.
