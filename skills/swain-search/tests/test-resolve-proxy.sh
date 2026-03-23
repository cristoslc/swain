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

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1 — $2"; FAIL=$((FAIL + 1)); }

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

first_proxy="$(echo "$output" | grep "^PROXY:" | head -1)"
second_proxy="$(echo "$output" | grep "^PROXY:" | sed -n '2p')"

if [[ "$first_proxy" == *"freedium"* && "$second_proxy" == *"archive-today"* ]]; then
  pass "AC1: proxies output in list order (freedium first, archive-today second)"
else
  fail "AC1: proxy order" "first=$first_proxy second=$second_proxy"
fi

rm -rf "$TMPDIR_REG"

# --- Integration: Default registry outputs mirror first ---
echo ""
echo "--- Integration: freedium-mirror before freedium in default registry ---"
output="$(bash "$RESOLVE_PROXY" "https://medium.com/test-article" 2>&1)"
first_proxy="$(echo "$output" | grep "^PROXY:" | head -1)"
if [[ "$first_proxy" == *"freedium-mirror"* ]]; then
  pass "Integration: freedium-mirror is first proxy"
else
  fail "Integration: first proxy" "expected freedium-mirror, got: $first_proxy"
fi

proxy_count="$(echo "$output" | grep -c "^PROXY:")"
if [[ $proxy_count -eq 2 ]]; then
  pass "Integration: 2 proxy lines output"
else
  fail "Integration: proxy count" "expected 2, got $proxy_count"
fi

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
