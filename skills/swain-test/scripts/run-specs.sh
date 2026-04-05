#!/usr/bin/env bash
# Run the full swain BDD suite, or a subset by domain.
#
# Usage:
#   run-specs.sh                # all specs
#   run-specs.sh session        # just session specs
#   run-specs.sh session worktree   # session + worktree specs
#   run-specs.sh --tap          # TAP output (for CI)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SPEC_DIR="$REPO_ROOT/spec"
FORMATTER="pretty"
DOMAINS=()

for arg in "$@"; do
  case "$arg" in
    --tap)    FORMATTER="tap13" ;;
    --junit)  FORMATTER="junit" ;;
    *)        DOMAINS+=("$arg") ;;
  esac
done

if [[ ${#DOMAINS[@]} -eq 0 ]]; then
  # Run all domain directories, excluding support/lib (bats helpers have their own tests)
  PATHS=()
  for dir in "$SPEC_DIR"/*/; do
    [[ "$(basename "$dir")" == "support" ]] && continue
    [[ "$(basename "$dir")" == "fixtures" ]] && continue
    PATHS+=("$dir")
  done
  bats --formatter "$FORMATTER" --recursive "${PATHS[@]}"
else
  PATHS=()
  for domain in "${DOMAINS[@]}"; do
    if [[ -d "$SPEC_DIR/$domain" ]]; then
      PATHS+=("$SPEC_DIR/$domain")
    else
      echo "Unknown domain: $domain (expected directory at $SPEC_DIR/$domain)" >&2
      exit 1
    fi
  done
  bats --formatter "$FORMATTER" --recursive "${PATHS[@]}"
fi
