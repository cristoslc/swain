#!/usr/bin/env bash
# Run external tests against containerized swain-helm services.
#
# Usage:
#   ./run-external-tests.sh smoke     # Run smoke tests
#   ./run-external-tests.sh uat       # Run UAT tests against container
#   ./run-external-tests.sh e2e       # Run E2E tests against container
#   ./run-external-tests.sh all       # Run all external tests

set -e

COMPOSE_FILE="docker-compose.external-tests.yml"
TEST_TYPE="${1:-smoke}"

case "$TEST_TYPE" in
  smoke)
    echo "=== Running smoke tests ==="
    docker compose -f "$COMPOSE_FILE" up -d smoke-test-target
    sleep 2
    python -m pytest tests/external/test_smoke.py -v --tb=short
    ;;
  uat)
    echo "=== Running UAT tests against external container ==="
    docker compose -f "$COMPOSE_FILE" up -d uat-test-target
    sleep 5
    SWAIN_HELM_EXTERNAL_TEST=1 python -m pytest tests/uat/test_watchdog_core.py -v --tb=short
    ;;
  e2e)
    echo "=== Running E2E tests against external container ==="
    docker compose -f "$COMPOSE_FILE" up -d e2e-test-target
    sleep 5
    SWAIN_HELM_EXTERNAL_TEST=1 python -m pytest tests/e2e/test_e2e_pipeline.py -v --tb=short
    ;;
  all)
    echo "=== Running all external tests ==="
    docker compose -f "$COMPOSE_FILE" up -d smoke-test-target uat-test-target
    sleep 5
    python -m pytest tests/external/test_smoke.py -v --tb=short
    SWAIN_HELM_EXTERNAL_TEST=1 python -m pytest tests/uat/test_watchdog_core.py -v --tb=short
    ;;
  *)
    echo "Unknown test type: $TEST_TYPE"
    echo "Usage: $0 {smoke|uat|e2e|all}"
    exit 1
    ;;
esac

echo "=== Tests complete ==="
echo "To stop containers: docker compose -f $COMPOSE_FILE down"
