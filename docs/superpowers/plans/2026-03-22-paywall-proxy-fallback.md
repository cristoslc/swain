# Paywall Proxy Fallback Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add automatic paywall detection and proxy fallback to swain-search's web page collection flow.

**Architecture:** A YAML registry maps domains to ordered proxy lists with truncation signals. A deterministic shell script (`resolve-proxy.sh`) reads the registry and outputs proxy URLs + signals for a given URL. The skill file (SKILL.md) instructs the agent to call the script after fetching, check for signals, and try proxies before degrading gracefully.

**Tech Stack:** Bash (script), YAML (registry), Markdown (skill file edits)

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Create | `skills/swain-search/references/paywall-proxies.yaml` | Domain-to-proxy registry (many-to-many) |
| Create | `skills/swain-search/scripts/resolve-proxy.sh` | Deterministic URL→proxy matching script |
| Create | `skills/swain-search/tests/test-resolve-proxy.sh` | Acceptance tests for resolve-proxy.sh |
| Modify | `.claude/skills/swain-search/SKILL.md` | Add "Paywall proxy fallback" section, update graceful degradation table |
| Modify | `skills/swain-search/SKILL.md` | Mirror of above — both copies must stay identical |
| Modify | `skills/swain-search/references/manifest-schema.md` | Add optional `proxy-used` field to source entry docs |

---

## Chunk 1: Registry and Script

### Task 1: Create paywall-proxies.yaml

**Files:**
- Create: `skills/swain-search/references/paywall-proxies.yaml`

- [ ] **Step 1: Create the registry file**

```yaml
# Paywall proxy registry — many-to-many mapping of domains to proxy strategies.
# Proxies are tried in list order per domain until one returns full content.

domains:
  - pattern: "medium.com"
    match: host-or-subdomain  # matches medium.com and *.medium.com
    proxies: [freedium]
    truncation-signals:
      - "Member-only story"
      - "You have 2 free member-only stories left"
      - "Sign up to discover human stories"

proxies:
  freedium:
    url-template: "https://freedium.cfd/{url}"
    notes: "Mirrors Medium member-only articles. May be intermittent."
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-search/references/paywall-proxies.yaml
git commit -m "feat(swain-search): add paywall proxy registry"
```

---

### Task 2: Write failing tests for resolve-proxy.sh

**Files:**
- Create: `skills/swain-search/tests/test-resolve-proxy.sh`

- [ ] **Step 1: Write the test file**

Follow the project's test pattern from `skills/swain-doctor/tests/test-ssh-readiness.sh`: `set +e`, `PASS`/`FAIL` counters, `pass()`/`fail()` helpers, temp dirs for isolation.

```bash
#!/usr/bin/env bash
# test-resolve-proxy.sh — Acceptance tests for resolve-proxy.sh (SPEC-155)
#
# Usage: bash skills/swain-search/tests/test-resolve-proxy.sh

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOLVE_PROXY="$(cd "$SCRIPT_DIR/.." && pwd)/scripts/resolve-proxy.sh"
REGISTRY="$(cd "$SCRIPT_DIR/.." && pwd)/references/paywall-proxies.yaml"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1 — $2"; ((FAIL++)); }

echo "=== resolve-proxy.sh Tests (SPEC-155) ==="
echo "Script: $RESOLVE_PROXY"
echo "Registry: $REGISTRY"
echo ""

# --- AC2: Domain matching for Medium URLs ---
echo "--- AC2: Medium URL produces PROXY and SIGNAL lines ---"
output="$(bash "$RESOLVE_PROXY" "https://medium.com/pub/article-slug" 2>&1)"
status=$?
if [[ $status -eq 0 ]]; then
  pass "AC2: exit 0 for medium.com URL"
else
  fail "AC2: exit code" "expected 0, got $status"
fi

if echo "$output" | grep -q "^PROXY:freedium:https://freedium.cfd/https://medium.com/pub/article-slug$"; then
  pass "AC2: PROXY line format correct"
else
  fail "AC2: PROXY line" "output=$output"
fi

if echo "$output" | grep -q "^SIGNAL:Member-only story$"; then
  pass "AC2: SIGNAL line present"
else
  fail "AC2: SIGNAL line" "output=$output"
fi

# Count SIGNAL lines — should match truncation-signals count in registry
signal_count="$(echo "$output" | grep -c "^SIGNAL:")"
if [[ $signal_count -eq 3 ]]; then
  pass "AC2: all 3 SIGNAL lines present"
else
  fail "AC2: SIGNAL count" "expected 3, got $signal_count"
fi

# --- AC3: No-match passthrough ---
echo ""
echo "--- AC3: Non-matching URL exits 1 with no output ---"
output="$(bash "$RESOLVE_PROXY" "https://example.com/page" 2>&1)"
status=$?
if [[ $status -eq 1 ]]; then
  pass "AC3: exit 1 for non-matching domain"
else
  fail "AC3: exit code" "expected 1, got $status"
fi

if [[ -z "$output" ]]; then
  pass "AC3: no output for non-matching domain"
else
  fail "AC3: unexpected output" "output=$output"
fi

# --- AC4: Subdomain matching ---
echo ""
echo "--- AC4: Subdomain of medium.com matches ---"
output="$(bash "$RESOLVE_PROXY" "https://engineering.medium.com/some-article" 2>&1)"
status=$?
if [[ $status -eq 0 ]]; then
  pass "AC4: exit 0 for subdomain"
else
  fail "AC4: exit code" "expected 0, got $status"
fi

if echo "$output" | grep -q "^PROXY:freedium:https://freedium.cfd/https://engineering.medium.com/some-article$"; then
  pass "AC4: PROXY line uses original subdomain URL"
else
  fail "AC4: PROXY line" "output=$output"
fi

# --- AC1: Multiple proxies in priority order ---
echo ""
echo "--- AC1: Multiple proxies output in list order ---"
# Create a temp registry with two proxies for medium.com
TMPDIR_REG="$(mktemp -d)"
cat > "$TMPDIR_REG/paywall-proxies.yaml" <<'YAML'
domains:
  - pattern: "medium.com"
    match: host-or-subdomain
    proxies: [freedium, archive-today]
    truncation-signals:
      - "Member-only story"

proxies:
  freedium:
    url-template: "https://freedium.cfd/{url}"
    notes: "test"
  archive-today:
    url-template: "https://archive.today/latest/{url}"
    notes: "test"
YAML

output="$(PAYWALL_REGISTRY="$TMPDIR_REG/paywall-proxies.yaml" bash "$RESOLVE_PROXY" "https://medium.com/test" 2>&1)"
status=$?

# Check order: freedium should come before archive-today
first_proxy="$(echo "$output" | grep "^PROXY:" | head -1)"
second_proxy="$(echo "$output" | grep "^PROXY:" | tail -1)"

if [[ "$first_proxy" == *"freedium"* && "$second_proxy" == *"archive-today"* ]]; then
  pass "AC1: proxies output in list order (freedium first, archive-today second)"
else
  fail "AC1: proxy order" "first=$first_proxy second=$second_proxy"
fi

rm -rf "$TMPDIR_REG"

# --- Edge: No arguments ---
echo ""
echo "--- Edge: No arguments exits 1 ---"
output="$(bash "$RESOLVE_PROXY" 2>&1)"
status=$?
if [[ $status -eq 1 ]]; then
  pass "Edge: exit 1 with no arguments"
else
  fail "Edge: no-arg exit code" "expected 1, got $status"
fi

# --- Summary ---
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `bash skills/swain-search/tests/test-resolve-proxy.sh`
Expected: All tests FAIL (resolve-proxy.sh doesn't exist yet)

- [ ] **Step 3: Commit the test file**

```bash
git add skills/swain-search/tests/test-resolve-proxy.sh
git commit -m "test(swain-search): add resolve-proxy.sh acceptance tests (SPEC-155)"
```

---

### Task 3: Implement resolve-proxy.sh

**Files:**
- Create: `skills/swain-search/scripts/resolve-proxy.sh`

- [ ] **Step 1: Write the script**

**Important:** This script must be compatible with bash 3.2 (macOS default). No `declare -A` (associative arrays require bash 4+). Use parallel indexed arrays instead.

```bash
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

# --- Parse registry and match domain ---
# We parse YAML line-by-line to avoid dependencies (no yq/python required).
# Uses parallel indexed arrays instead of associative arrays for bash 3.2 compat.

# First pass: collect proxy definitions (parallel arrays: names + templates)
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
    # Proxy name (indented, no dash) — tolerant of 2+ spaces
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
```

- [ ] **Step 2: Make the script executable**

```bash
chmod +x skills/swain-search/scripts/resolve-proxy.sh
```

- [ ] **Step 3: Run the tests**

Run: `bash skills/swain-search/tests/test-resolve-proxy.sh`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add skills/swain-search/scripts/resolve-proxy.sh
git commit -m "feat(swain-search): implement resolve-proxy.sh (SPEC-155)"
```

---

## Chunk 2: Skill File and Schema Updates

### Task 4: Update SKILL.md with paywall proxy fallback section

**Files:**
- Modify: `.claude/skills/swain-search/SKILL.md` (after "Web page URLs" block)
- Modify: `skills/swain-search/SKILL.md` (mirror — both copies must stay identical)

- [ ] **Step 1: Add the "Paywall proxy fallback" section**

Insert after the "Web page URLs" block (after line 83, before "Video/audio URLs"):

```markdown
**Paywall proxy fallback:**

After fetching a web page, check if a paywall proxy is available for the URL's domain:

1. Run `skills/swain-search/scripts/resolve-proxy.sh <url>`
   - **Exit 1**: no proxy configured — use the direct fetch content as-is
   - **Exit 0**: outputs `PROXY:<name>:<proxy-url>` and `SIGNAL:<text>` lines
2. If exit 0, check the fetched content for each `SIGNAL` text (case-sensitive literal match)
3. If any signal matches (or the article body is under ~200 words):
   - Log: "Paywall detected for `<url>` — trying proxy fallback"
   - Try each `PROXY` URL in order, fetching via the same page-fetching capability used for web pages
   - First proxy that returns substantive content (more than the truncated original) wins
   - Set `proxy-used: <name>` and `notes: "Full article retrieved via <name> proxy"` in the manifest entry
4. If no signals match: use the direct fetch content as-is (no proxy needed)
5. If all proxies fail: keep the original truncated content, set `notes: "Paywalled; proxies exhausted — content from direct fetch only"`

The registry lives at `skills/swain-search/references/paywall-proxies.yaml`. Add new domains or proxies there — no skill file changes needed.
```

- [ ] **Step 2: Update the "Graceful degradation" table**

Find the existing table (around line 255) and add a new row:

```markdown
| Paywall proxy | Keep truncated content. Note in manifest: "Paywalled; proxies exhausted." Suggest user provide content manually. |
```

- [ ] **Step 3: Mirror edits to the second SKILL.md copy**

Both `.claude/skills/swain-search/SKILL.md` and `skills/swain-search/SKILL.md` must stay identical. Apply the same edits (Steps 1-2) to `skills/swain-search/SKILL.md`. Verify they match:

```bash
diff .claude/skills/swain-search/SKILL.md skills/swain-search/SKILL.md
```

Expected: no output (files identical).

- [ ] **Step 4: Verify the edits read correctly**

Read the modified sections to ensure they flow with the surrounding content.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/swain-search/SKILL.md skills/swain-search/SKILL.md
git commit -m "feat(swain-search): add paywall proxy fallback instructions to SKILL.md (SPEC-155)"
```

---

### Task 5: Update manifest-schema.md with proxy-used field

**Files:**
- Modify: `skills/swain-search/references/manifest-schema.md` (source entry optional fields)

- [ ] **Step 1: Add proxy-used to the optional fields section**

In the "Source entry fields" section, find the optional fields block. Insert after the `freshness-ttl` line (search for `freshness-ttl:` in the YAML code block):

```yaml
proxy-used: freedium                  # Which paywall proxy delivered the content (omit if direct fetch)
```

- [ ] **Step 2: Commit**

```bash
git add skills/swain-search/references/manifest-schema.md
git commit -m "docs(swain-search): add proxy-used field to manifest schema (SPEC-155)"
```

---

### Task 6: Final verification

- [ ] **Step 1: Run all tests one more time**

Run: `bash skills/swain-search/tests/test-resolve-proxy.sh`
Expected: All tests PASS, 0 failures

- [ ] **Step 2: Verify the full file set**

Check that all expected files exist and are properly formatted:

```bash
ls -la skills/swain-search/references/paywall-proxies.yaml
ls -la skills/swain-search/scripts/resolve-proxy.sh
ls -la skills/swain-search/tests/test-resolve-proxy.sh
head -5 .claude/skills/swain-search/SKILL.md
```

- [ ] **Step 3: Verify SKILL.md has both new sections**

```bash
grep -n "Paywall proxy fallback" .claude/skills/swain-search/SKILL.md
grep -n "Paywall proxy" .claude/skills/swain-search/SKILL.md
```

Expected: "Paywall proxy fallback" heading found, plus a row in the graceful degradation table.

- [ ] **Step 4: Verify AC6/AC7 note strings are in SKILL.md**

```bash
grep -q "proxies exhausted" .claude/skills/swain-search/SKILL.md && echo "AC6 string found" || echo "AC6 string MISSING"
grep -q "Full article retrieved via" .claude/skills/swain-search/SKILL.md && echo "AC7 string found" || echo "AC7 string MISSING"
```

Expected: Both strings found.
