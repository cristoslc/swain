#!/bin/bash
set -euo pipefail

# swain-keys — per-project key provisioning for git signing and authentication
#
# Usage:
#   swain-keys.sh [--provision | --status | --verify]
#
# Supports GitHub (SSH signing via gh) and Forgejo (GPG signing via fj).
# Idempotent — safe to re-run. Skips steps where artifacts already exist.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Helpers ---

die()   { echo "ERROR: $*" >&2; exit 1; }
info()  { echo ":: $*"; }
warn()  { echo "WARN: $*" >&2; }
ok()    { echo "OK: $*"; }
skip()  { echo "SKIP: $*"; }

gh_is_authed() {
  command -v gh &>/dev/null && gh auth status &>/dev/null
}

fj_is_authed() {
  command -v fj &>/dev/null && fj user info &>/dev/null
}

# --- Forge detection ---

detect_forge() {
  SWAIN_FORGE="${SWAIN_FORGE:-}"
  if [[ -n "$SWAIN_FORGE" ]]; then
    return 0
  fi

  local remote name url
  for name in $(git remote 2>/dev/null); do
    url="$(git remote get-url "$name" 2>/dev/null || true)"
    if echo "$url" | grep -qE 'github\.com[:/-]'; then
      SWAIN_FORGE="${SWAIN_FORGE}github "
    elif echo "$url" | grep -qE '(codeberg\.org|forgejo\.|gitea\.|localhost|127\.0\.0\.1)'; then
      SWAIN_FORGE="${SWAIN_FORGE}forgejo "
    else
      SWAIN_FORGE="${SWAIN_FORGE}unknown "
    fi
  done

  SWAIN_FORGE="$(echo "$SWAIN_FORGE" | tr ' ' '\n' | sort -u | tr '\n' ' ' | xargs)"
  if [[ -z "$SWAIN_FORGE" ]]; then
    echo "UNKNOWN_FORGE: Could not detect forge from any remote URL." >&2
    echo "Set SWAIN_FORGE to 'github', 'forgejo', or 'github forgejo' and re-run." >&2
    exit 2
  fi
}

fj_forgejo_host() {
  local remote_url host
  host="${SWAIN_FORGEJO_HOST:-}"
  if [[ -n "$host" ]]; then
    echo "$host"
    return 0
  fi

  # Priority 1: existing HTTPS remotes (most reliable)
  local name
  for name in $(git remote 2>/dev/null); do
    remote_url="$(git remote get-url "$name" 2>/dev/null || true)"
    if [[ "$remote_url" =~ ^https?:// ]]; then
      if echo "$remote_url" | grep -qE 'localhost|127\.0\.0\.1'; then
        echo "http://localhost:3000"
        return 0
      elif [[ "$remote_url" =~ ^(https?://[^/]+) ]]; then
        echo "${BASH_REMATCH[1]}"
        return 0
      fi
    fi
  done

  # Priority 2: SSH remotes (extract hostname, guess HTTPS)
  for name in $(git remote 2>/dev/null); do
    remote_url="$(git remote get-url "$name" 2>/dev/null || true)"
    if echo "$remote_url" | grep -qE 'localhost|127\.0\.0\.1'; then
      echo "http://localhost:3000"
      return 0
    elif echo "$remote_url" | grep -qE 'codeberg\.org'; then
      echo "https://codeberg.org"
      return 0
    elif [[ "$remote_url" =~ ^git@([^:]+): ]]; then
      echo "https://${BASH_REMATCH[1]}"
      return 0
    fi
  done

  echo "http://localhost:3000"
}

# --- Derive project name ---

derive_project_name() {
  local remote_url name
  local found_remote
  for found_remote in $(git remote 2>/dev/null); do
    remote_url="$(git remote get-url "$found_remote" 2>/dev/null || true)"
    if [[ -n "$remote_url" ]]; then
      name="$(basename "$remote_url" .git)"
      if [[ -n "$name" ]]; then
        echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g'
        return 0
      fi
    fi
  done
  name="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")"
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

# --- Step: SSH key generation (GitHub path) ---

step_generate_ssh_key() {
  local key_path="$1"
  if [[ -f "$key_path" ]]; then
    skip "SSH key already exists: $key_path"
    return 0
  fi
  mkdir -p "$(dirname "$key_path")"
  info "Generating ed25519 key: $key_path"
  ssh-keygen -t ed25519 -f "$key_path" -N "" -C "swain-keys:${PROJECT_NAME}" -q
  ok "SSH key generated: $key_path"
}

# --- Step: GPG key generation (Forgejo path) ---

step_generate_gpg_key() {
  local gpg_keyid_file="$1" email="$2"

  if ! command -v gpg &>/dev/null; then
    die "gpg is required for Forgejo signing. Install it: brew install gnupg"
  fi

  mkdir -p "$(dirname "$gpg_keyid_file")"

  local existing_keyid
  existing_keyid="$(gpg --list-secret-keys --with-colons "$email" 2>/dev/null | grep '^sec:' | head -1 | cut -d: -f5 || true)"
  if [[ -n "$existing_keyid" ]]; then
    echo "$existing_keyid" > "$gpg_keyid_file"
    skip "GPG key already exists for $email (keyid: $existing_keyid)"
    return 0
  fi

  if [[ -f "$gpg_keyid_file" ]]; then
    local cached_keyid
    cached_keyid="$(cat "$gpg_keyid_file")"
    if gpg --list-secret-keys "$cached_keyid" &>/dev/null 2>&1; then
      skip "GPG key already tracked (keyid: $cached_keyid)"
      return 0
    fi
  fi

  info "Generating OpenPGP ed25519 key for $email..."
  local gpg_batch
  gpg_batch="$(mktemp)"
  cat > "$gpg_batch" <<GPGSETUP
%no-protection
Key-Type: EDDSA
Key-Curve: ed25519
Key-Usage: sign
Subkey-Type: EDDSA
Subkey-Curve: ed25519
Subkey-Usage: encrypt
Name-Email: ${email}
Name-Comment: swain-keys:${PROJECT_NAME}
%commit
GPGSETUP

  local new_keyid
  new_keyid="$(gpg --batch --generate-key "$gpg_batch" 2>&1 | grep -oE 'gpg: key [A-F0-9]+' | head -1 | awk '{print $3}' || true)"
  rm -f "$gpg_batch"

  if [[ -z "$new_keyid" ]]; then
    new_keyid="$(gpg --list-secret-keys --with-colons "$email" 2>/dev/null | grep '^sec:' | head -1 | cut -d: -f5)"
  fi

  if [[ -z "$new_keyid" ]]; then
    die "GPG key generation failed — unable to find generated key"
  fi

  mkdir -p "$(dirname "$gpg_keyid_file")"
  echo "$new_keyid" > "$gpg_keyid_file"
  ok "GPG key generated (keyid: $new_keyid)"
}

# --- Step: allowed signers ---

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

# --- Step: GitHub key registration ---

step_add_key_to_github() {
  local pub_key_path="$1" key_title="$2" key_type="$3"

  if ! gh_is_authed; then
    warn "gh CLI not authenticated — skipping GitHub key registration for type '$key_type'"
    return 1
  fi

  local pub_key fingerprint existing
  pub_key="$(cat "$pub_key_path")"
  existing="$(gh ssh-key list 2>/dev/null || true)"
  fingerprint="$(awk '{print $2}' "$pub_key_path")"

  if echo "$existing" | grep -F "$fingerprint" | grep -q "$key_type"; then
    skip "Key already registered on GitHub for $key_type"
    return 0
  fi

  info "Adding key to GitHub for $key_type (title: $key_title)..."
  if gh ssh-key add "$pub_key_path" --title "$key_title" --type "$key_type" 2>/dev/null; then
    ok "Key registered on GitHub for $key_type"
  else
    warn "Failed to add key for $key_type — you may need to run: gh auth refresh -s admin:public_key,admin:ssh_signing_key"
    echo "NEEDS_SCOPE_REFRESH" >&2
    return 1
  fi
}

# --- Step: Forgejo GPG key upload ---

step_add_gpg_key_to_forgejo() {
  local gpg_keyid_file="$1"
  local host keyid fj_cmd

  host="$(fj_forgejo_host)"
  keyid="$(cat "$gpg_keyid_file")"

  if [[ "$host" == "http://localhost:3000" ]]; then
    fj_cmd="fj -H http://localhost:3000"
  else
    fj_cmd="fj -H $host"
  fi

  if ! $fj_cmd user info &>/dev/null 2>&1; then
    warn "fj not authenticated — skipping Forgejo GPG upload"
    return 1
  fi

  local fj_keys
  fj_keys="$($fj_cmd user gpg list 2>/dev/null || true)"
  if echo "$fj_keys" | grep "$keyid" | grep -q "Can Sign: true"; then
    skip "GPG key ${keyid:0:16} already registered on Forgejo (Can Sign: true)"
    return 0
  fi

  if echo "$fj_keys" | grep -q "$keyid"; then
    info "GPG key ${keyid:0:16} exists on Forgejo but not as signing key — re-uploading..."
  else
    info "Uploading GPG key ${keyid:0:16} to Forgejo..."
  fi

  local tmp_pub
  tmp_pub="$(mktemp)"
  gpg --armor --export "$keyid" > "$tmp_pub" 2>/dev/null || true
  if [[ ! -s "$tmp_pub" ]]; then
    rm -f "$tmp_pub"
    warn "Could not export GPG public key for $keyid"
    return 1
  fi

  if $fj_cmd user gpg upload "$keyid" --key-file "$tmp_pub" 2>/dev/null; then
    rm -f "$tmp_pub"
    ok "GPG key registered on Forgejo as signing key"
  else
    rm -f "$tmp_pub"
    warn "Failed to upload GPG key to Forgejo — try manually: $fj_cmd user gpg upload $keyid"
    return 1
  fi
}

# --- Step: SSH config (GitHub path) ---

step_create_ssh_config() {
  local config_path="$1" project="$2" key_path="$3"
  local config_dir host_alias

  host_alias="github.com-${project}"
  config_dir="$(dirname "$config_path")"

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

# --- Step: update remote URL (GitHub path) ---

step_rename_remotes() {
  local project="$1"
  local host_alias="github.com-${project}"

  local name url owner_repo new_url
  for name in $(git remote 2>/dev/null); do
    # Skip already-canonical remote names
    if [[ "$name" == "gh" ]] || [[ "$name" == "fjl" ]]; then
      skip "Remote '$name' already uses canonical name"
      continue
    fi

    url="$(git remote get-url "$name" 2>/dev/null || true)"

    # GitHub remotes
    if echo "$url" | grep -qE 'github\.com[:/-]'; then
      if echo "$url" | grep -qF "$host_alias"; then
        skip "Remote '$name' already uses host alias: $url"
      else
        if [[ "$url" =~ github\.com[:/](.+)$ ]]; then
          owner_repo="${BASH_REMATCH[1]}"
          owner_repo="${owner_repo%.git}"
          new_url="git@${host_alias}:${owner_repo}.git"
          info "Renaming '$name' to 'gh' (URL: $url -> $new_url)"
          git remote remove "$name" 2>/dev/null || true
          git remote add gh "$new_url"
          ok "Remote '$name' -> 'gh' with host alias URL: $new_url"
        else
          warn "Could not parse GitHub owner/repo from: $url"
        fi
      fi

    # Forgejo remotes — always use HTTPS (fj CLI bug: doesn't work with SSH)
    elif echo "$url" | grep -qE '(forgejo\.|gitea\.|localhost|127\.0\.0\.1)'; then
      local fj_base fj_repo https_url
      fj_base="$(fj_forgejo_host)"
      # Extract owner/repo from any URL format
      fj_repo="${url##*:}"
      fj_repo="${fj_repo%.git}"
      [[ "$fj_repo" == "$url" ]] && fj_repo="$(basename "$url" .git)"
      https_url="${fj_base}/${fj_repo}.git"
      info "Renaming '$name' to 'fjl' (URL: $url -> $https_url)"
      git remote remove "$name" 2>/dev/null || true
      git remote add fjl "$https_url"
      ok "Remote '$name' -> 'fjl' with HTTPS URL: $https_url"

    else
      info "Skipping remote '$name' — cannot classify URL: $url"
    fi
  done
}

# --- Step: git signing config ---

step_configure_git_signing() {
  local key_path="$1" signers_path="$2"

  info "Configuring local git SSH signing..."

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

  ok "Git SSH signing configured (local scope)"
}

# --- Step: GPG signing config (Forgejo path) ---

step_configure_gpg_signing() {
  local gpg_keyid="$1"

  info "Configuring local git GPG signing..."

  local gpg_program
  gpg_program="$(command -v gpg 2>/dev/null || echo "/opt/homebrew/bin/gpg")"

  local global_format
  global_format="$(git config --global gpg.format 2>/dev/null || true)"
  if [[ "$global_format" == "ssh" ]]; then
    info "Global gpg.format is 'ssh', overriding locally to openpgp"
  fi

  local global_program
  global_program="$(git config --global gpg.program 2>/dev/null || true)"
  if [[ -z "$global_program" ]] && [[ "$global_format" == "ssh" ]]; then
    info "Global gpg.program is empty (likely 1Password user), setting locally"
    git config --local gpg.program "$gpg_program"
  fi

  git config --local gpg.format openpgp
  git config --local user.signingkey "$gpg_keyid"
  git config --local commit.gpgsign true
  git config --local tag.gpgsign true

  ok "Git GPG signing configured (local scope)"
}

# --- Verification ---

step_verify_connectivity() {
  local host_alias="$1"

  info "Verifying SSH connectivity to $host_alias..."
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

  local remote_url owner_repo
  remote_url="$(git remote get-url origin 2>/dev/null || true)"
  if [[ "$remote_url" =~ github\.com[:/](.+)$ ]]; then
    owner_repo="${BASH_REMATCH[1]}"
    owner_repo="${owner_repo%.git}"
  else
    warn "Could not determine GitHub owner/repo for verification"
    return 1
  fi

  local head_sha verified reason result
  head_sha="$(git rev-parse HEAD)"
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

step_verify_forgejo_signing() {
  info "Verifying GPG key on Forgejo..."
  local gpg_keyid_file="$1"
  local host keyid fj_cmd verified can_sign verified_status

  host="$(fj_forgejo_host)"
  keyid="$(cat "$gpg_keyid_file")"

  if [[ "$host" == "http://localhost:3000" ]]; then
    fj_cmd="fjl"
  else
    fj_cmd="fj -H $host"
  fi

  if ! $fj_cmd user info &>/dev/null 2>&1; then
    warn "fj not authenticated — skipping Forgejo GPG verification"
    return 1
  fi

  verified="$($fj_cmd user gpg list 2>/dev/null | grep "$keyid" || true)"
  if [[ -z "$verified" ]]; then
    warn "GPG key ${keyid:0:16} not found on Forgejo"
    return 1
  fi

  can_sign="$(echo "$verified" | grep "Can Sign: true" || true)"
  verified_status="$(echo "$verified" | grep "Verified: true" || true)"

  if [[ -n "$can_sign" && -n "$verified_status" ]]; then
    ok "GPG key registered on Forgejo as signing key (Verified: true)"
    return 0
  elif [[ -n "$can_sign" ]]; then
    ok "GPG key registered on Forgejo as signing key (not yet verified by Forgejo)"
    return 0
  else
    warn "GPG key ${keyid:0:16} exists on Forgejo but not as signing key"
    return 1
  fi
}

# --- Commands ---

cmd_status() {
  local project email key_path pub_key_path signers_path config_path host_alias
  local remote_url gpg_keyid_file gpg_keyid

  detect_forge

  project="$(derive_project_name)"
  email="$(get_git_email_or_placeholder)"
  key_path="$HOME/.ssh/${project}_signing"
  pub_key_path="${key_path}.pub"
  signers_path="$HOME/.ssh/allowed_signers_${project}"
  config_path="$HOME/.ssh/config.d/${project}.conf"
  gpg_keyid_file="$HOME/.ssh/${project}_gpg_keyid"

  echo "=== swain-keys status ==="
  echo "Forge:            $SWAIN_FORGE"
  echo "Project:          $project"
  echo "Git email:        $email"
  echo ""

  if [[ "$SWAIN_FORGE" == *"forgejo"* ]]; then
    echo "GPG keyid file:   $([ -f "$gpg_keyid_file" ] && echo "EXISTS ($gpg_keyid_file)" || echo "MISSING")"
    if [[ -f "$gpg_keyid_file" ]]; then
      gpg_keyid="$(cat "$gpg_keyid_file")"
      echo "GPG keyid:        ${gpg_keyid:0:16}..."
    fi
    echo ""
  else
    echo "SSH key:          $([ -f "$key_path" ] && echo "EXISTS ($key_path)" || echo "MISSING")"
    echo "Public key:       $([ -f "$pub_key_path" ] && echo "EXISTS" || echo "MISSING")"
    echo "Allowed signers:  $([ -f "$signers_path" ] && echo "EXISTS ($signers_path)" || echo "MISSING")"
    echo "SSH config:       $([ -f "$config_path" ] && echo "EXISTS ($config_path)" || echo "MISSING")"
    echo ""
  fi

  local signing_key gpg_format commit_sign
  signing_key="$(git config --local user.signingkey 2>/dev/null || echo "(not set)")"
  gpg_format="$(git config --local gpg.format 2>/dev/null || echo "(not set)")"
  commit_sign="$(git config --local commit.gpgsign 2>/dev/null || echo "(not set)")"

  echo "Git config (local):"
  echo "  gpg.format:     $gpg_format"
  echo "  user.signingkey: $signing_key"
  echo "  commit.gpgsign: $commit_sign"
  echo ""

  echo "Remotes:"
  local name url
  for name in $(git remote 2>/dev/null); do
    url="$(git remote get-url "$name" 2>/dev/null || true)"
    echo "  $name: $url"
    if [[ "$SWAIN_FORGE" == *"github"* ]] && [[ "$name" == "gh" ]]; then
      if echo "$url" | grep -qF "$host_alias"; then
        echo "    (uses project-specific host alias)"
      elif echo "$url" | grep -q "^https://"; then
        echo "    (HTTPS — will be changed to SSH alias on provision)"
      fi
    elif [[ "$SWAIN_FORGE" == *"forgejo"* ]] && [[ "$name" == "fjl" ]]; then
      echo "    (Forgejo — left unchanged)"
    fi
  done

  echo ""

  if [[ "$SWAIN_FORGE" == *"github"* ]]; then
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
  else
    echo "Forgejo GPG keys:"
    if [[ -f "$gpg_keyid_file" ]]; then
      local host fj_cmd
      host="$(fj_forgejo_host)"
      if [[ "$host" == "http://localhost:3000" ]]; then
        fj_cmd="fjl"
      else
        fj_cmd="fj -H $host"
      fi
      gpg_keyid="$(cat "$gpg_keyid_file")"
      if $fj_cmd user info &>/dev/null 2>&1; then
        local fj_keys verified can_sign
        fj_keys="$($fj_cmd user gpg list 2>/dev/null || true)"
        verified="$(echo "$fj_keys" | grep "$gpg_keyid" || true)"
        if [[ -n "$verified" ]]; then
          can_sign="$(echo "$verified" | grep "Can Sign: true" || true)"
          if [[ -n "$can_sign" ]]; then
            echo "  GPG key registered on Forgejo as signing key (Verified: true)"
          else
            echo "  GPG key registered on Forgejo but not as signing key"
          fi
        else
          echo "  GPG key NOT found on Forgejo"
        fi
      else
        echo "  (fj CLI not authenticated)"
        echo "  Keyid: ${gpg_keyid:0:16}..."
      fi
    else
      echo "  (no GPG key generated for this project)"
    fi
  fi
}

cmd_provision() {
  local project email had_errors
  had_errors=false

  detect_forge

  project="$(derive_project_name)"
  email="$(get_git_email)"

  echo "=== swain-keys provision ==="
  echo "Forge: $SWAIN_FORGE | Project: $project | Email: $email"
  echo ""

  # Run forgejo provisioning
  if [[ "$SWAIN_FORGE" == *"forgejo"* ]]; then
    echo "--- Forgejo provisioning ---"
    local gpg_keyid_file gpg_keyid
    gpg_keyid_file="$HOME/.ssh/${project}_gpg_keyid"

    step_generate_gpg_key "$gpg_keyid_file" "$email"
    gpg_keyid="$(cat "$gpg_keyid_file")"
    echo ""

    local fj_auth_ok=true
    if ! step_add_gpg_key_to_forgejo "$gpg_keyid_file" 2>/dev/null; then
      fj_auth_ok=false
    fi
    echo ""

    step_configure_gpg_signing "$gpg_keyid"
    echo ""

    echo "--- Verification (Forgejo) ---"
    step_verify_signing || had_errors=true

    if [[ "$fj_auth_ok" == true ]]; then
      step_verify_forgejo_signing "$gpg_keyid_file" || had_errors=true
    else
      info "Skipping Forgejo GPG verification — key not yet registered"
    fi
    echo ""

    if [[ "$fj_auth_ok" == false ]]; then
      local host fj_cmd
      host="$(fj_forgejo_host)"
      if [[ "$host" == "http://localhost:3000" ]]; then
        fj_cmd="fjl"
      else
        fj_cmd="fj -H $host"
      fi
      echo "ACTION NEEDED: GPG key not registered on Forgejo (fj CLI not authenticated)."
      echo ""
      echo "Upload the GPG key manually:"
      echo "  $fj_cmd user gpg upload $gpg_keyid"
      echo ""
      echo "Or, if fj becomes available later:"
      echo "  fj auth login && bash $0 --provision"
    fi
  fi

  # Run GitHub provisioning
  if [[ "$SWAIN_FORGE" == *"github"* ]]; then
    echo "--- GitHub provisioning ---"
    local key_path pub_key_path signers_path config_path host_alias
    key_path="$HOME/.ssh/${project}_signing"
    pub_key_path="${key_path}.pub"
    signers_path="$HOME/.ssh/allowed_signers_${project}"
    config_path="$HOME/.ssh/config.d/${project}.conf"
    host_alias="github.com-${project}"

    step_generate_ssh_key "$key_path"
    echo ""

    step_create_allowed_signers "$signers_path" "$email" "$pub_key_path"
    echo ""

    local gh_auth_ok=true
    if ! step_add_key_to_github "$pub_key_path" "swain-keys:${project}" "authentication" 2>/dev/null; then
      gh_auth_ok=false
    fi
    if ! step_add_key_to_github "$pub_key_path" "swain-keys:${project}-signing" "signing" 2>/dev/null; then
      gh_auth_ok=false
    fi
    echo ""

    step_create_ssh_config "$config_path" "$project" "$key_path"
    echo ""

    step_configure_git_signing "$key_path" "$signers_path"
    echo ""

    echo "--- Verification (GitHub) ---"
    step_verify_signing || had_errors=true

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
  fi

  # Rename remotes (runs once, handles both forges)
  step_rename_remotes "$project"
  echo ""

  if [[ "$had_errors" == true ]]; then
    echo ""
    echo "Some verification steps had warnings — review output above."
    exit 1
  fi

  echo "=== Provisioning complete ==="
}

cmd_verify() {
  local had_warnings=false project host_alias gpg_keyid_file
  detect_forge

  echo "=== swain-keys verify (forge: $SWAIN_FORGE) ==="

  project="$(derive_project_name)"
  host_alias="github.com-${project}"
  gpg_keyid_file="$HOME/.ssh/${project}_gpg_keyid"

  if [[ "$SWAIN_FORGE" == *"forgejo"* ]]; then
    echo "--- Forgejo ---"
    step_verify_signing || had_warnings=true

    if [[ -f "$gpg_keyid_file" ]]; then
      step_verify_forgejo_signing "$gpg_keyid_file" || had_warnings=true
    else
      warn "No GPG keyid file found — run --provision first"
    fi
  fi

  if [[ "$SWAIN_FORGE" == *"github"* ]]; then
    echo "--- GitHub ---"
    step_verify_connectivity "$host_alias" || had_warnings=true
    step_verify_signing || had_warnings=true
    step_verify_github_signing || had_warnings=true
  fi

  if [[ "$had_warnings" == true ]]; then
    echo "=== Some checks had warnings ==="
  else
    echo "=== All checks passed ==="
  fi
}

# --- Main ---

git rev-parse --git-dir &>/dev/null || die "Not in a git repository"

PROJECT_NAME="$(derive_project_name)"

case "${1:-}" in
  --provision) cmd_provision ;;
  --status)    cmd_status ;;
  --verify)    cmd_verify ;;
  -h|--help)
    echo "Usage: swain-keys.sh [--provision | --status | --verify]"
    echo ""
    echo "  --provision  Generate keys, configure git signing, register on forge"
    echo "  --status     Show current key/config state for this project"
    echo "  --verify     Test signing capability and forge registration"
    echo ""
    echo "Supports GitHub (SSH signing) and Forgejo (GPG signing)."
    echo "Forge is auto-detected from all git remotes."
    echo "  Set SWAIN_FORGE to 'github', 'forgejo', or 'github forgejo' to override detection."
    echo "  Set SWAIN_FORGEJO_HOST to override the Forgejo instance URL."
    echo "Remotes are renamed to canonical names: 'gh' (GitHub), 'fjl' (Forgejo)."
    ;;
  *)
    cmd_status
    ;;
esac
