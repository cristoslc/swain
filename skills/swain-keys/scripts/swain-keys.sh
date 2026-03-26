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

# Check whether gh CLI is available AND authenticated
gh_is_authed() {
  command -v gh &>/dev/null && gh auth status &>/dev/null
}

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

get_git_email_or_placeholder() {
  local email
  email="$(git config user.email 2>/dev/null || git config --global user.email 2>/dev/null || true)"
  echo "${email:-"(not set)"}"
}

# --- Step implementations ---

step_generate_key() {
  local key_path="$1"
  if [[ -f "$key_path" ]]; then
    skip "Key already exists: $key_path"
    return 0
  fi
  mkdir -p "$(dirname "$key_path")"
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

  if ! gh_is_authed; then
    warn "gh CLI not authenticated — skipping GitHub key registration for type '$key_type'"
    return 1
  fi

  local pub_key
  pub_key="$(cat "$pub_key_path")"

  # Check if THIS key is already registered for THIS type
  local existing fingerprint
  existing="$(gh ssh-key list 2>/dev/null || true)"
  fingerprint="$(awk '{print $2}' "$pub_key_path")"
  # gh ssh-key list format: TITLE  KEY_TYPE  FINGERPRINT  CREATED  ID  TYPE
  # We need to check that a line contains BOTH this key's fingerprint AND the target type
  if echo "$existing" | grep -F "$fingerprint" | grep -q "$key_type"; then
    skip "Key already registered on GitHub for $key_type"
    return 0
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
    if grep -qF "$host_alias" "$config_path" 2>/dev/null \
      && grep -qF "HostName ssh.github.com" "$config_path" 2>/dev/null \
      && grep -qF "Port 443" "$config_path" 2>/dev/null; then
      skip "SSH config already exists: $config_path"
      return 0
    elif grep -qF "$host_alias" "$config_path" 2>/dev/null; then
      info "Migrating SSH config to ssh.github.com:443: $config_path"
    fi
  fi

  info "Creating SSH config: $config_path"
  cat > "$config_path" <<SSHEOF
# swain-keys: per-project SSH config for ${project}
Host ${host_alias}
  HostName ssh.github.com
  Port 443
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
    skip "Remote URL already uses host alias: $current_url" # nosemgrep: hooks-dns-exfiltration-generic
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

  # Detect if gpg.ssh.program resolves to 1Password's op-ssh-sign (may be
  # set in an included config file, not just --global).  File-based keys
  # cannot be used by op-ssh-sign, so override locally with ssh-keygen.
  local current_ssh_program
  current_ssh_program="$(git config gpg.ssh.program 2>/dev/null || true)"
  if [[ "$current_ssh_program" == *"op-ssh-sign"* ]]; then
    info "Detected 1Password ssh signing program ($current_ssh_program), overriding with ssh-keygen"
    git config --local gpg.ssh.program ssh-keygen
  fi

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

step_verify_github_signing() {
  info "Verifying commit shows as signed on GitHub..."
  if ! command -v gh &>/dev/null; then
    warn "gh CLI not found — skipping GitHub signing verification"
    return 1
  fi

  # Check the latest commit's verification status on GitHub
  local remote_url owner_repo
  remote_url="$(git remote get-url origin 2>/dev/null || true)"
  if [[ "$remote_url" =~ github\.com[:/](.+)$ ]]; then
    owner_repo="${BASH_REMATCH[1]}"
    owner_repo="${owner_repo%.git}"
  else
    warn "Could not determine GitHub owner/repo for verification"
    return 1
  fi

  local head_sha verified reason
  head_sha="$(git rev-parse HEAD)"
  local result
  result="$(gh api "repos/${owner_repo}/commits/${head_sha}" --jq '.commit.verification | "\(.verified) \(.reason)"' 2>/dev/null || echo "error")"
  verified="$(echo "$result" | awk '{print $1}')"
  reason="$(echo "$result" | awk '{print $2}')"

  if [[ "$verified" == "true" ]]; then
    ok "Latest commit (${head_sha:0:7}) shows as Verified on GitHub"
    return 0
  else
    warn "Latest commit (${head_sha:0:7}) not verified on GitHub (reason: ${reason:-unknown})"
    warn "This may be expected if the commit was made before signing was configured"
    return 1
  fi
}

# --- Commands ---

cmd_status() {
  local project email key_path pub_key_path signers_path config_path host_alias

  project="$(derive_project_name)"
  email="$(get_git_email_or_placeholder)"
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
  if gh_is_authed; then
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
    echo "GitHub keys:      (gh CLI not authenticated)"
    if [[ -f "$pub_key_path" ]]; then
      echo "  To register manually: https://github.com/settings/ssh/new"
      echo "  Public key: $(cat "$pub_key_path")"
    fi
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
  step_verify_signing || had_errors=true

  # Only test SSH connectivity if keys were registered on GitHub
  if [[ "$gh_auth_ok" == true ]]; then
    step_verify_connectivity "$host_alias" || had_errors=true
  else
    info "Skipping SSH connectivity check — key not yet registered on GitHub"
  fi
  echo ""

  echo "NOTE: GitHub signing verification requires a signed commit to be pushed."
  echo "Run 'swain-keys.sh --verify' after your next push to confirm Verified status."
  echo ""

  if [[ "$gh_auth_ok" == false ]]; then
    echo "ACTION NEEDED: Key not registered on GitHub (gh CLI not authenticated)."
    echo ""
    echo "Add this public key to GitHub for both authentication and signing:"
    echo "  https://github.com/settings/ssh/new"
    echo ""
    echo "Public key:"
    cat "$pub_key_path"
    echo ""
    echo "Or, if gh becomes available later:"
    echo "  gh auth login && bash $0 --provision"
    echo ""
    echo "SSH push/pull will not work until the key is registered."
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
  local had_warnings=false

  echo "=== swain-keys verify ==="
  step_verify_connectivity "$host_alias" || had_warnings=true
  step_verify_signing || had_warnings=true
  step_verify_github_signing || had_warnings=true

  if [[ "$had_warnings" == true ]]; then
    echo "=== Some checks had warnings ==="
  else
    echo "=== All checks passed ==="
  fi
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
