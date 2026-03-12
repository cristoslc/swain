#!/bin/bash
set -euo pipefail

# swain-keys — per-project SSH key provisioning for git signing and authentication
#
# Usage:
#   swain-keys.sh [--provision | --status | --verify]
#
# Idempotent — safe to re-run. Skips steps where artifacts already exist.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Helpers ---

die()   { echo "ERROR: $*" >&2; exit 1; }
info()  { echo ":: $*"; }
warn()  { echo "WARN: $*" >&2; }
ok()    { echo "OK: $*"; }
skip()  { echo "SKIP: $*"; }

# --- Derive project name ---

derive_project_name() {
  local remote_url name
  remote_url="$(git remote get-url origin 2>/dev/null || true)"
  if [[ -n "$remote_url" ]]; then
    # Extract repo name from URL (handles both HTTPS and SSH forms)
    name="$(basename "$remote_url" .git)"
  else
    name="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")"
  fi
  # Sanitize: lowercase, alphanumeric and hyphens only
  echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g'
}

# --- Derive git email ---

get_git_email() {
  git config user.email 2>/dev/null || git config --global user.email 2>/dev/null || die "No git user.email configured (local or global)"
}

# --- Step implementations ---

step_generate_key() {
  local key_path="$1"
  if [[ -f "$key_path" ]]; then
    skip "Key already exists: $key_path"
    return 0
  fi
  info "Generating ed25519 key: $key_path"
  ssh-keygen -t ed25519 -f "$key_path" -N "" -C "swain-keys:${PROJECT_NAME}" -q
  ok "Key generated: $key_path"
}

step_create_allowed_signers() {
  local signers_path="$1" email="$2" pub_key_path="$3"
  local pub_key
  pub_key="$(cat "$pub_key_path")"
  local expected_line="${email} ${pub_key}"

  if [[ -f "$signers_path" ]]; then
    if grep -qF "$pub_key" "$signers_path" 2>/dev/null; then
      skip "Allowed signers file already contains this key: $signers_path"
      return 0
    fi
  fi

  info "Writing allowed signers file: $signers_path"
  echo "$expected_line" > "$signers_path"
  ok "Allowed signers file created: $signers_path"
}

step_add_key_to_github() {
  local pub_key_path="$1" key_title="$2" key_type="$3"

  if ! command -v gh &>/dev/null; then
    warn "gh CLI not found — skipping GitHub key registration for type '$key_type'"
    return 1
  fi

  local pub_key
  pub_key="$(cat "$pub_key_path")"

  # Check if key already registered
  local existing
  existing="$(gh ssh-key list 2>/dev/null || true)"
  if echo "$existing" | grep -qF "$(awk '{print $2}' "$pub_key_path")"; then
    # Key fingerprint is present — check if this specific type is registered
    # gh ssh-key list shows: TITLE  TYPE  FINGERPRINT  CREATED
    if echo "$existing" | grep -q "$key_type"; then
      skip "Key already registered on GitHub for $key_type"
      return 0
    fi
  fi

  info "Adding key to GitHub for $key_type (title: $key_title)..."

  # Try adding — may fail if scopes are insufficient
  if gh ssh-key add "$pub_key_path" --title "$key_title" --type "$key_type" 2>/dev/null; then
    ok "Key registered on GitHub for $key_type"
  else
    warn "Failed to add key for $key_type — you may need to run: gh auth refresh -s admin:public_key,admin:ssh_signing_key"
    echo "NEEDS_SCOPE_REFRESH" >&2
    return 1
  fi
}

step_create_ssh_config() {
  local config_path="$1" project="$2" key_path="$3"
  local config_dir host_alias

  host_alias="github.com-${project}"
  config_dir="$(dirname "$config_path")"

  # Ensure config.d directory exists
  mkdir -p "$config_dir"

  if [[ -f "$config_path" ]]; then
    if grep -qF "$host_alias" "$config_path" 2>/dev/null; then
      skip "SSH config already exists: $config_path"
      return 0
    fi
  fi

  info "Creating SSH config: $config_path"
  cat > "$config_path" <<SSHEOF
# swain-keys: per-project SSH config for ${project}
Host ${host_alias}
  HostName github.com
  User git
  IdentityFile ${key_path}
  IdentitiesOnly yes
SSHEOF

  ok "SSH config created: $config_path (alias: $host_alias)"

  # Ensure ~/.ssh/config includes config.d/*
  local main_config="$HOME/.ssh/config"
  if [[ -f "$main_config" ]]; then
    if ! grep -qF "Include config.d/" "$main_config" 2>/dev/null; then
      info "Adding 'Include config.d/*' to ~/.ssh/config"
      local tmp
      tmp="$(mktemp)"
      echo "Include config.d/*" > "$tmp"
      echo "" >> "$tmp"
      cat "$main_config" >> "$tmp"
      mv "$tmp" "$main_config"
      ok "Updated ~/.ssh/config with Include directive"
    fi
  else
    info "Creating ~/.ssh/config with Include directive"
    mkdir -p "$HOME/.ssh"
    echo "Include config.d/*" > "$main_config"
    chmod 600 "$main_config"
    ok "Created ~/.ssh/config"
  fi
}

step_update_remote_url() {
  local project="$1"
  local host_alias="github.com-${project}"
  local current_url

  current_url="$(git remote get-url origin 2>/dev/null || true)"
  if [[ -z "$current_url" ]]; then
    warn "No origin remote — skipping URL update"
    return 0
  fi

  # If already using the alias, skip
  if echo "$current_url" | grep -qF "$host_alias"; then
    skip "Remote URL already uses host alias: $current_url"
    return 0
  fi

  # Extract owner/repo from HTTPS or SSH URL
  local owner_repo
  if [[ "$current_url" =~ github\.com[:/](.+)$ ]]; then
    owner_repo="${BASH_REMATCH[1]}"
    owner_repo="${owner_repo%.git}"
  else
    warn "Could not parse GitHub owner/repo from: $current_url"
    return 1
  fi

  local new_url="git@${host_alias}:${owner_repo}.git"
  info "Updating remote URL: $current_url -> $new_url"
  git remote set-url origin "$new_url"
  ok "Remote URL updated to: $new_url"
}

step_configure_git_signing() {
  local key_path="$1" signers_path="$2"

  info "Configuring local git signing..."

  git config --local gpg.format ssh
  git config --local user.signingkey "$key_path"
  git config --local gpg.ssh.allowedSignersFile "$signers_path"
  git config --local commit.gpgsign true
  git config --local tag.gpgsign true

  ok "Git signing configured (local scope)"
}

step_verify_connectivity() {
  local host_alias="$1"

  info "Verifying SSH connectivity to $host_alias..."
  # ssh -T returns exit code 1 for GitHub even on success (it prints a greeting)
  local output
  output="$(ssh -T "git@${host_alias}" 2>&1 || true)"
  if echo "$output" | grep -qi "successfully authenticated"; then
    ok "SSH connectivity verified: $output"
    return 0
  else
    warn "SSH connectivity check returned: $output"
    return 1
  fi
}

step_verify_signing() {
  info "Verifying commit signing capability..."
  # Create an empty signed commit to test, then remove it
  local test_output
  if test_output="$(echo 'test' | git commit-tree HEAD^{tree} -S 2>&1)"; then
    ok "Commit signing works (test object: ${test_output:0:8})"
    return 0
  else
    warn "Signing verification failed: $test_output"
    return 1
  fi
}

# --- Commands ---

cmd_status() {
  local project email key_path pub_key_path signers_path config_path host_alias

  project="$(derive_project_name)"
  email="$(get_git_email 2>/dev/null || echo "(not set)")"
  key_path="$HOME/.ssh/${project}_signing"
  pub_key_path="${key_path}.pub"
  signers_path="$HOME/.ssh/allowed_signers_${project}"
  config_path="$HOME/.ssh/config.d/${project}.conf"
  host_alias="github.com-${project}"

  echo "=== swain-keys status ==="
  echo "Project:          $project"
  echo "Git email:        $email"
  echo ""
  echo "SSH key:          $([ -f "$key_path" ] && echo "EXISTS ($key_path)" || echo "MISSING")"
  echo "Public key:       $([ -f "$pub_key_path" ] && echo "EXISTS" || echo "MISSING")"
  echo "Allowed signers:  $([ -f "$signers_path" ] && echo "EXISTS ($signers_path)" || echo "MISSING")"
  echo "SSH config:       $([ -f "$config_path" ] && echo "EXISTS ($config_path)" || echo "MISSING")"
  echo ""

  # Check git config
  local signing_key gpg_format commit_sign
  signing_key="$(git config --local user.signingkey 2>/dev/null || echo "(not set)")"
  gpg_format="$(git config --local gpg.format 2>/dev/null || echo "(not set)")"
  commit_sign="$(git config --local commit.gpgsign 2>/dev/null || echo "(not set)")"

  echo "Git config (local):"
  echo "  gpg.format:     $gpg_format"
  echo "  user.signingkey: $signing_key"
  echo "  commit.gpgsign: $commit_sign"
  echo ""

  # Check remote URL
  local remote_url
  remote_url="$(git remote get-url origin 2>/dev/null || echo "(no remote)")"
  echo "Remote URL:       $remote_url"
  if echo "$remote_url" | grep -qF "$host_alias"; then
    echo "  (uses project-specific host alias)"
  elif echo "$remote_url" | grep -q "^https://"; then
    echo "  (HTTPS — will be changed to SSH alias on provision)"
  fi

  echo ""

  # Check GitHub key registration
  if command -v gh &>/dev/null; then
    echo "GitHub keys:"
    local gh_keys
    gh_keys="$(gh ssh-key list 2>/dev/null || echo "(could not list)")"
    if [[ -f "$pub_key_path" ]]; then
      local fingerprint
      fingerprint="$(awk '{print $2}' "$pub_key_path")"
      if echo "$gh_keys" | grep -qF "$fingerprint" 2>/dev/null; then
        echo "  Key is registered on GitHub"
      else
        echo "  Key NOT found on GitHub"
      fi
    else
      echo "  (no local key to check)"
    fi
  else
    echo "GitHub keys:      (gh CLI not available)"
  fi
}

cmd_provision() {
  local project email key_path pub_key_path signers_path config_path host_alias
  local needs_scope_refresh=false
  local had_errors=false

  project="$(derive_project_name)"
  email="$(get_git_email)"
  key_path="$HOME/.ssh/${project}_signing"
  pub_key_path="${key_path}.pub"
  signers_path="$HOME/.ssh/allowed_signers_${project}"
  config_path="$HOME/.ssh/config.d/${project}.conf"
  host_alias="github.com-${project}"

  echo "=== swain-keys provision ==="
  echo "Project: $project | Email: $email"
  echo ""

  # Step 1: Generate key
  step_generate_key "$key_path"
  echo ""

  # Step 2: Allowed signers
  step_create_allowed_signers "$signers_path" "$email" "$pub_key_path"
  echo ""

  # Step 3: Add to GitHub (authentication + signing)
  local gh_auth_ok=true
  if ! step_add_key_to_github "$pub_key_path" "swain-keys:${project}" "authentication" 2>/dev/null; then
    gh_auth_ok=false
  fi
  if ! step_add_key_to_github "$pub_key_path" "swain-keys:${project}-signing" "signing" 2>/dev/null; then
    gh_auth_ok=false
  fi
  echo ""

  # Step 4: SSH config
  step_create_ssh_config "$config_path" "$project" "$key_path"
  echo ""

  # Step 5: Update remote URL
  step_update_remote_url "$project"
  echo ""

  # Step 6: Git signing config
  step_configure_git_signing "$key_path" "$signers_path"
  echo ""

  # Step 7: Verify
  echo "--- Verification ---"
  step_verify_connectivity "$host_alias" || had_errors=true
  step_verify_signing || had_errors=true
  echo ""

  if [[ "$gh_auth_ok" == false ]]; then
    echo "ACTION NEEDED: Some GitHub key registrations failed."
    echo "Run:  gh auth refresh -s admin:public_key,admin:ssh_signing_key"
    echo "Then: bash $0 --provision   (re-run is safe — idempotent)"
  fi

  if [[ "$had_errors" == true ]]; then
    echo ""
    echo "Some verification steps had warnings — review output above."
    exit 1
  fi

  echo "=== Provisioning complete ==="
}

cmd_verify() {
  local project host_alias
  project="$(derive_project_name)"
  host_alias="github.com-${project}"

  echo "=== swain-keys verify ==="
  step_verify_connectivity "$host_alias"
  step_verify_signing
  echo "=== All checks passed ==="
}

# --- Main ---

# Must be in a git repo
git rev-parse --git-dir &>/dev/null || die "Not in a git repository"

PROJECT_NAME="$(derive_project_name)"

case "${1:-}" in
  --provision) cmd_provision ;;
  --status)    cmd_status ;;
  --verify)    cmd_verify ;;
  -h|--help)
    echo "Usage: swain-keys.sh [--provision | --status | --verify]"
    echo ""
    echo "  --provision  Generate SSH key, configure git signing, register on GitHub"
    echo "  --status     Show current key/config state for this project"
    echo "  --verify     Test SSH connectivity and commit signing"
    ;;
  *)
    # Default: show status, then offer to provision
    cmd_status
    ;;
esac
