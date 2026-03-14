---
id: swa-chy1
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
# Research git signing key forwarding in containers and sandboxes

How do SSH-based signing keys (swain-keys) work inside Docker? Can gh auth be forwarded via binding ~/.config/gh/? Does Tier 1 (sandbox-exec) need explicit path allowlist for ~/.ssh and ~/.config/gh?


## Notes

**2026-03-14T06:13:26Z**

Completed: SSH_AUTH_SOCK unreliable on macOS->Docker. Use file-based keys. swain-keys already writes git config --local gpg.ssh.program ssh-keygen to override op-ssh-sign. Repo uses HTTPS push — only signing is SSH, which is file-based.

**2026-03-14T06:14:02Z**

Completed: Findings in SPIKE-008 §5 (Git Signing in Containers). SSH_AUTH_SOCK forwarding into Docker on macOS is unreliable — Docker Desktop VM cannot see macOS host Unix sockets. swain-keys file-based keys are the correct approach: mount ~/.ssh/<project>_signing (ro) into container; git config --local gpg.ssh.program=ssh-keygen already set by step_configure_git_signing(). For sandbox-exec: allow file-read* on specific per-project files only (not full ~/.ssh/), see §6 SBPL rules. 1Password agent socket is explicitly excluded.
