---
id: swa-anuo
status: closed
deps: [swa-872z, swa-odv1, swa-251k, swa-fwou, swa-gyrv]
links: []
created: 2026-03-18T03:37:18Z
type: task
priority: 1
assignee: cristos
parent: swa-u7jl
tags: [spike:SPIKE-027, spec:SPEC-067]
---
# Synthesize findings and update SPIKE-027 + SPEC-067

Populate SPIKE-027 Findings section. Write Summary with verdict (Go/No-Go/Conditional). Update SPEC-067 AC-8 to reflect resolved credential strategy. Transition SPIKE-027 to Complete. Remove SPIKE-027 from SPEC-067 depends-on-artifacts if Go, or document No-Go pivot.


## Notes

**2026-03-18T03:56:15Z**

SPIKE-027 Complete. Verdict: Conditional Go — do not mount ~/.claude/. Credentials via ANTHROPIC_API_KEY (proxy) or CLAUDE_CODE_OAUTH_TOKEN (Max sub). Sandbox home=/home/agent; host path would land wrong anyway. ~/.claude/projects/ has 60+ memory dirs — exposure risk. SPEC-067 unblocked: depends-on-artifacts cleared, AC-8 updated, open question resolved.
