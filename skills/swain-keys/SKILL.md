---
name: swain-keys
description: "Per-project key provisioning for git signing and authentication. Invoke to configure git signing, set up keys for this project, bypass 1Password for git operations, add a key to GitHub or Forgejo, troubleshoot signing prompts, or check key status. Generates ed25519 SSH keys (GitHub) or GPG keys (Forgejo), configures git signing, registers keys on the forge, and sets up SSH host aliases to bypass global agents."
user-invocable: true
allowed-tools: Bash, Read, Edit, Glob, AskUserQuestion
metadata:
  short-description: Key provisioning for projects
  version: 1.1.0
  author: cristos
  license: MIT
  source: swain
---
<!-- swain-model-hint: haiku, effort: low -->

# swain-keys

Per-project key provisioning for git signing and authentication.

Supports two forges with the right signing mode for each:
- **GitHub** — SSH signing via `gh ssh-key add`.
- **Forgejo** — GPG signing via `fj user gpg upload`.

Forge is auto-detected from the origin remote URL. Set `SWAIN_FORGE` to override.

## When invoked

Locate and run the provisioning script at `scripts/swain-keys.sh` (relative to this skill's directory):

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT="$REPO_ROOT/.agents/bin/swain-keys.sh"
```

If the path search fails, glob for `**/swain-keys/scripts/swain-keys.sh`.

## Workflows

### Default (no arguments or "set up keys")

Run `--status` first to show current state:

```bash
bash "$SCRIPT" --status
```

If keys are not fully provisioned, ask the user if they'd like to proceed with provisioning.

### Provision ("provision keys", "configure signing", "set up SSH")

Run the full provisioning flow:

```bash
bash "$SCRIPT" --provision
```

**On GitHub, the script will:**
1. Derive a project name from the git remote or directory.
2. Generate `~/.ssh/<project>_signing` (ed25519, no passphrase) if not exists.
3. Create `~/.ssh/allowed_signers_<project>` with the configured git email.
4. Add the public key to GitHub via `gh ssh-key add` for both authentication and signing.
5. Create `~/.ssh/config.d/<project>.conf` with a host alias that bypasses global SSH agents and routes GitHub SSH over `ssh.github.com:443`.
6. Update the git remote URL to use the project-specific host alias.
7. Set local git config for SSH commit and tag signing.
8. Verify SSH connectivity and signing capability.

**On Forgejo, the script will:**
1. Derive a project name from the git remote or directory.
2. Generate an OpenPGP ed25519 key via `gpg --batch --generate-key` (unattended, `%no-protection`) if not exists.
3. Upload the GPG public key to Forgejo via `fj user gpg upload`.
4. Configure local git for OpenPGP signing (`gpg.format=openpgp`), overriding any global SSH signing config.
5. Leave the remote URL unchanged (Forgejo SSH auth is handled by the user's existing SSH config).
6. Verify signing capability and Forgejo GPG key status.

### Status ("key status", "check keys")

```bash
bash "$SCRIPT" --status
```

Shows forge type, key state, git config, and forge registration status. Reports "GPG key registered on Forgejo as signing key (Verified: true)" when applicable.

### Verify ("verify keys", "test signing")

```bash
bash "$SCRIPT" --verify
```

Tests signing capability and forge key registration. For Forgejo, verifies the GPG key has `Can Sign: true` on the forge.

## Environment variables

- `SWAIN_FORGE` — set to `github` or `forgejo` to override auto-detection.
- `SWAIN_FORGEJO_HOST` — set the Forgejo instance URL (e.g., `https://codeberg.org`). Defaults to `http://localhost:3000` when origin includes `localhost`.

## Handling scope refresh

### GitHub

If `gh ssh-key add` fails due to insufficient scopes, the script will print an action-needed message. When this happens:

1. Tell the user they need to authorize additional GitHub scopes.
2. Show them the command: `gh auth refresh -s admin:public_key,admin:ssh_signing_key`.
3. This will open a browser for OAuth — it requires human interaction.
4. After they confirm, re-run `--provision` (idempotent, will skip completed steps).

### Forgejo

If `fj user gpg upload` fails, check that `fj` is authenticated:

```
fj auth login
```

Then re-run `--provision`.

## Integration with swain-init

When called from swain-init, run `--provision` directly without the status-first flow. swain-init handles the "would you like to?" prompt.

## Session bookmark

After provisioning, update the bookmark: `bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" "Provisioned keys for {project}"`

## Error handling

- If not in a git repo: fail with clear message.
- If `gh` CLI unavailable (GitHub): skip GitHub registration steps, warn user to add keys manually.
- If `fj` CLI unavailable (Forgejo): skip Forgejo registration, warn user to upload GPG key manually.
- If `gpg` not installed (Forgejo): fail with install instructions.
- If git email not configured: fail early with instructions.
- All steps are idempotent — safe to re-run after fixing issues.
