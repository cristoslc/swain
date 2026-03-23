#!/usr/bin/env bash
# resolve-proxy.sh — Deterministic paywall proxy resolver for swain-search
#
# Usage: resolve-proxy.sh <url>
#
# Reads paywall-proxies.yaml and outputs proxy URLs + truncation signals
# for the given URL's domain. Exits 0 if proxies found, 1 if no match.
#
# Output format (line-oriented):
#   PROXY:<name>:<proxy-url>
#   SIGNAL:<text>
#
# Override registry path: PAYWALL_REGISTRY=path/to/file.yaml
#
# Note: YAML values in the registry MUST be double-quoted for parsing.
# Compatible with bash 3.2+ (no associative arrays).
#
# Part of SPEC-155: Paywall Proxy Fallback

set -euo pipefail

if [[ $# -lt 1 ]]; then
  exit 1
fi

URL="$1"

# Extract host from URL
HOST="$(echo "$URL" | sed -E 's|^https?://([^/]+).*|\1|')"

# Locate registry
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="${PAYWALL_REGISTRY:-$SCRIPT_DIR/../references/paywall-proxies.yaml}"

if [[ ! -f "$REGISTRY" ]]; then
  exit 1
fi

# --- Parse registry ---
# Line-by-line YAML parsing to avoid yq/python dependencies.
# Uses parallel indexed arrays for bash 3.2 compatibility (no declare -A).

# First pass: collect proxy definitions (parallel arrays)
proxy_def_names=()
proxy_def_templates=()
in_proxies_section=false
current_proxy_name=""

while IFS= read -r line; do
  if [[ "$line" =~ ^proxies: ]]; then
    in_proxies_section=true
    continue
  fi

  if $in_proxies_section && [[ "$line" =~ ^[a-z] && ! "$line" =~ ^[[:space:]] ]]; then
    in_proxies_section=false
    continue
  fi

  if $in_proxies_section; then
    # Proxy name (indented, ends with bare colon)
    if [[ "$line" =~ ^[[:space:]]+([a-zA-Z0-9_-]+):$ ]]; then
      current_proxy_name="${BASH_REMATCH[1]}"
    fi
    if [[ -n "$current_proxy_name" && "$line" =~ url-template:[[:space:]]*\"(.+)\" ]]; then
      proxy_def_names+=("$current_proxy_name")
      proxy_def_templates+=("${BASH_REMATCH[1]}")
      current_proxy_name=""
    fi
  fi
done < "$REGISTRY"

# Helper: look up url-template by proxy name
lookup_template() {
  local name="$1"
  local i
  for (( i=0; i<${#proxy_def_names[@]}; i++ )); do
    if [[ "${proxy_def_names[$i]}" == "$name" ]]; then
      echo "${proxy_def_templates[$i]}"
      return 0
    fi
  done
  return 1
}

# Second pass: find matching domain entry
matched=false
current_proxies=()
current_signals=()
in_domains_section=false
in_domain_entry=false
in_signals=false

while IFS= read -r line; do
  if [[ "$line" =~ ^domains: ]]; then
    in_domains_section=true
    continue
  fi

  if $in_domains_section && [[ "$line" =~ ^[a-z] && ! "$line" =~ ^[[:space:]] ]]; then
    in_domains_section=false
    continue
  fi

  if ! $in_domains_section; then
    continue
  fi

  # New domain entry (list item with pattern)
  if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*pattern:[[:space:]]*\"(.+)\" ]]; then
    if $matched; then
      break
    fi
    local_pattern="${BASH_REMATCH[1]}"
    current_proxies=()
    current_signals=()
    in_domain_entry=true
    in_signals=false

    # host-or-subdomain matching
    if [[ "$HOST" == "$local_pattern" ]] || [[ "$HOST" == *".$local_pattern" ]]; then
      matched=true
    fi
    continue
  fi

  if ! $in_domain_entry; then
    continue
  fi

  # Proxies list (inline YAML array)
  if [[ "$line" =~ proxies:[[:space:]]*\[(.+)\] ]]; then
    IFS=',' read -ra proxy_items <<< "${BASH_REMATCH[1]}"
    for item in "${proxy_items[@]}"; do
      item="$(echo "$item" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')"
      current_proxies+=("$item")
    done
    continue
  fi

  # Truncation signals section
  if [[ "$line" =~ truncation-signals: ]]; then
    in_signals=true
    continue
  fi

  if $in_signals && [[ "$line" =~ ^[[:space:]]*-[[:space:]]*\"(.+)\" ]]; then
    current_signals+=("${BASH_REMATCH[1]}")
    continue
  fi

  if $in_signals && [[ ! "$line" =~ ^[[:space:]]*- ]]; then
    in_signals=false
  fi

done < "$REGISTRY"

# --- Output ---

if ! $matched; then
  exit 1
fi

for proxy_name in "${current_proxies[@]}"; do
  template="$(lookup_template "$proxy_name" 2>/dev/null || true)"
  if [[ -n "$template" ]]; then
    proxy_url="${template//\{url\}/$URL}"
    echo "PROXY:${proxy_name}:${proxy_url}"
  fi
done

for signal in "${current_signals[@]}"; do
  echo "SIGNAL:${signal}"
done

exit 0
