#!/usr/bin/env bash
set -euo pipefail

# ssh-readiness.sh — validate and optionally repair per-project SSH alias wiring
#
# Usage:
#   ssh-readiness.sh --check
#   ssh-readiness.sh --repair
#
# Exit 0: SSH alias wiring is healthy or not applicable for this repo
# Exit 1: Remaining issues need operator action

MODE="${1:---check}"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

issue_count=0

add_issue() {
  echo "ISSUE: $*"
  issue_count=$((issue_count + 1))
}

add_note() {
  echo "NOTE: $*"
}

derive_project_from_alias_remote() {
  local remote_url
  remote_url="$(git -C "$REPO_ROOT" remote get-url origin 2>/dev/null || true)"
  if [[ "$remote_url" =~ ^git@github\.com-([a-z0-9-]+): ]]; then
    echo "${BASH_REMATCH[1]}"
  fi
}

ensure_main_config_include() {
  local ssh_dir="$1" config_dir="$2" main_config="$3"
  mkdir -p "$ssh_dir" "$config_dir"
  chmod 700 "$ssh_dir"

  if [[ ! -f "$main_config" ]]; then
    printf 'Include config.d/*\n' > "$main_config"
    chmod 600 "$main_config"
    add_note "Created $main_config with Include config.d/*"
    return 0
  fi

  if ! grep -qF "Include config.d/*" "$main_config" 2>/dev/null; then
    local tmp
    tmp="$(mktemp)"
    printf 'Include config.d/*\n\n' > "$tmp"
    cat "$main_config" >> "$tmp"
    mv "$tmp" "$main_config"
    chmod 600 "$main_config"
    add_note "Updated $main_config to include config.d/*"
  fi
}

write_alias_config() {
  local alias_file="$1" host_alias="$2" key_path="$3"
  mkdir -p "$(dirname "$alias_file")"
  cat > "$alias_file" <<EOF
# swain-doctor: per-project SSH config for ${host_alias}
Host ${host_alias}
  HostName ssh.github.com
  Port 443
  User git
  IdentityFile ${key_path}
  IdentitiesOnly yes
EOF
  chmod 600 "$alias_file"
  add_note "Created $alias_file"
}

read_identity_file() {
  local alias_file="$1"
  awk '/^[[:space:]]*IdentityFile[[:space:]]+/ { print $2; exit }' "$alias_file" 2>/dev/null || true
}

alias_uses_github_443() {
  local alias_file="$1"
  grep -qF "HostName ssh.github.com" "$alias_file" 2>/dev/null \
    && grep -qF "Port 443" "$alias_file" 2>/dev/null
}

main() {
  local project host_alias ssh_dir config_dir main_config alias_file default_key alias_key

  project="$(derive_project_from_alias_remote)"
  if [[ -z "$project" ]]; then
    exit 0
  fi

  host_alias="github.com-${project}"
  ssh_dir="$HOME/.ssh"
  config_dir="$ssh_dir/config.d"
  main_config="$ssh_dir/config"
  alias_file="$config_dir/${project}.conf"
  default_key="$ssh_dir/${project}_signing"

  if ! command -v ssh >/dev/null 2>&1; then
    add_issue "ssh client not found on PATH — install OpenSSH client before using ${host_alias}"
  fi

  if [[ "$MODE" == "--repair" ]]; then
    ensure_main_config_include "$ssh_dir" "$config_dir" "$main_config"
  else
    if [[ ! -f "$main_config" ]]; then
      add_issue "${host_alias} remote requires $main_config with 'Include config.d/*'"
    elif ! grep -qF "Include config.d/*" "$main_config" 2>/dev/null; then
      add_issue "$main_config is missing 'Include config.d/*' for ${host_alias}"
    fi
  fi

  if [[ ! -f "$alias_file" ]]; then
    if [[ "$MODE" == "--repair" && -f "$default_key" ]]; then
      write_alias_config "$alias_file" "$host_alias" "$default_key"
    else
      add_issue "${host_alias} remote is configured but $alias_file is missing. Run swain-keys --provision."
    fi
  fi

  if [[ -f "$alias_file" ]]; then
    if ! grep -qE "^[[:space:]]*Host[[:space:]]+${host_alias}\$" "$alias_file" 2>/dev/null; then
      add_issue "$alias_file does not define Host ${host_alias}"
    fi

    alias_key="$(read_identity_file "$alias_file")"
    alias_key="${alias_key/#\~/$HOME}"
    if [[ -z "$alias_key" ]]; then
      add_issue "$alias_file is missing IdentityFile for ${host_alias}"
    elif [[ ! -f "$alias_key" ]]; then
      add_issue "${host_alias} points to missing key ${alias_key}. Run swain-keys --provision."
    elif ! alias_uses_github_443 "$alias_file"; then
      if [[ "$MODE" == "--repair" ]]; then
        write_alias_config "$alias_file" "$host_alias" "$alias_key"
      else
        add_issue "$alias_file still targets legacy github.com:22. Re-run swain-keys --provision or doctor repair."
      fi
    fi
  elif [[ ! -f "$default_key" ]]; then
    add_issue "${host_alias} remote has no local key at $default_key. Run swain-keys --provision."
  fi

  if [[ $issue_count -gt 0 ]]; then
    exit 1
  fi
}

main
