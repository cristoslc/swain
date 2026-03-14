---
id: swa-fkfl
status: closed
deps: []
links: []
created: 2026-03-14T06:07:57Z
type: task
priority: 2
assignee: cristos
parent: swa-ymk2
tags: [spec:SPIKE-008]
---
# Map minimal credential set for Claude Code

What credentials does Claude Code need? ANTHROPIC_API_KEY, git identity, gh auth token. What paths does each live in and how does each flow into an isolated environment?


## Notes

**2026-03-14T06:13:26Z**

Completed: Minimal set = ANTHROPIC_API_KEY (env), GH_TOKEN (env), ~/.gitconfig, ~/.config/git/local.gitconfig, ~/.ssh/<project>_signing{,.pub}, allowed_signers, config.d/<project>.conf, known_hosts. State dirs (.claude/, .agents/, .tickets/) covered by project root mount.

**2026-03-14T06:14:10Z**

Completed: Findings in SPIKE-008 §1, §3, §4. Minimal credential set: ANTHROPIC_API_KEY (env var, never file), GH_TOKEN via gh auth token (env var, bypasses Keychain), ~/.gitconfig + ~/.config/git/local.gitconfig (ro bind), ~/.ssh/<project>_signing + .pub + allowed_signers + config.d/<project>.conf (ro binds), ~/.ssh/known_hosts (ro). API key: -e ANTHROPIC_API_KEY, no file, no Dockerfile. gh auth: GH_TOKEN env var preferred over ~/.config/gh/ bind (Keychain token not in file). Excluded: ~/Library/, personal identity keys, ~/.aws/, ~/.netrc, ~/.zshrc.
