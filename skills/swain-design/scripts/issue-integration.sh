#!/usr/bin/env bash
set -euo pipefail

# issue-integration.sh — GitHub Issues ↔ swain artifact integration
#
# Subcommands:
#   check                        Verify gh CLI is available and authenticated
#   promote <issue-url>          Fetch issue data for SPEC creation (outputs JSON)
#   comment <source-issue> <msg> Post a comment to the linked issue
#   close   <source-issue> <msg> Close the linked issue with a comment
#   scan    [docs-root]          Scan artifacts for source-issue fields (outputs JSON)
#
# source-issue format: github:<owner>/<repo>#<number>
#
# Backend abstraction: dispatch on URL prefix (github:, linear:, jira:, etc.)
# Only the GitHub backend is implemented. Adding a new backend means adding
# a parse_<backend> + <backend>_promote/comment/close set of functions.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# ── Helpers ──────────────────────────────────────────────────────────────────

die()  { echo "Error: $*" >&2; exit 1; }
warn() { echo "Warning: $*" >&2; }

# ── Backend dispatch ─────────────────────────────────────────────────────────

# Parse a source-issue value into backend + owner + repo + number.
# Sets: SI_BACKEND, SI_OWNER, SI_REPO, SI_NUMBER
parse_source_issue() {
  local val="$1"
  SI_BACKEND="" SI_OWNER="" SI_REPO="" SI_NUMBER=""

  if [[ "$val" =~ ^github:([^/]+)/([^#]+)#([0-9]+)$ ]]; then
    SI_BACKEND="github"
    SI_OWNER="${BASH_REMATCH[1]}"
    SI_REPO="${BASH_REMATCH[2]}"
    SI_NUMBER="${BASH_REMATCH[3]}"
  else
    die "Unsupported source-issue format: $val (expected github:<owner>/<repo>#<number>)"
  fi
}

# ── GitHub backend ───────────────────────────────────────────────────────────

github_check() {
  if ! command -v gh &>/dev/null; then
    echo '{"available":false,"error":"gh CLI not found. Install: https://cli.github.com"}'
    return 1
  fi

  if ! gh auth status &>/dev/null; then
    echo '{"available":false,"error":"gh CLI not authenticated. Run: gh auth login"}'
    return 1
  fi

  echo '{"available":true}'
}

github_promote() {
  local owner="$1" repo="$2" number="$3"

  local issue_json
  issue_json=$(gh issue view "$number" --repo "${owner}/${repo}" \
    --json number,title,body,labels,assignees,state,url 2>/dev/null) || \
    die "Failed to fetch issue #${number} from ${owner}/${repo}"

  # Output structured JSON for SPEC creation
  local title body url labels_csv
  title=$(echo "$issue_json" | jq -r '.title')
  body=$(echo "$issue_json" | jq -r '.body // ""')
  url=$(echo "$issue_json" | jq -r '.url')
  labels_csv=$(echo "$issue_json" | jq -r '[.labels[].name] | join(", ")')

  jq -n \
    --arg source_issue "github:${owner}/${repo}#${number}" \
    --arg title "$title" \
    --arg body "$body" \
    --arg url "$url" \
    --arg labels "$labels_csv" \
    --argjson number "$number" \
    '{
      source_issue: $source_issue,
      number: $number,
      title: $title,
      body: $body,
      url: $url,
      labels: $labels
    }'
}

github_comment() {
  local owner="$1" repo="$2" number="$3" message="$4"

  gh issue comment "$number" --repo "${owner}/${repo}" --body "$message" &>/dev/null || \
    die "Failed to comment on issue #${number} in ${owner}/${repo}"

  echo '{"ok":true}'
}

github_close() {
  local owner="$1" repo="$2" number="$3" message="$4"

  # Post closing comment first
  if [[ -n "$message" ]]; then
    gh issue comment "$number" --repo "${owner}/${repo}" --body "$message" &>/dev/null || \
      warn "Failed to post closing comment on #${number}"
  fi

  gh issue close "$number" --repo "${owner}/${repo}" &>/dev/null || \
    die "Failed to close issue #${number} in ${owner}/${repo}"

  echo '{"ok":true,"closed":true}'
}

# ── scan: find all source-issue fields in artifacts ──────────────────────────

cmd_scan() {
  local docs_root="${1:-${REPO_ROOT}/docs}"
  local results="[]"

  while IFS= read -r -d '' file; do
    # Extract source-issue from YAML frontmatter
    local si_val artifact_id title status
    si_val=$(awk '/^---$/{n++; next} n==1 && /^source-issue:/{gsub(/^source-issue:[[:space:]]*/, ""); print; exit}' "$file")
    [[ -z "$si_val" || "$si_val" == '""' ]] && continue

    artifact_id=$(awk '/^---$/{n++; next} n==1 && /^artifact:/{gsub(/^artifact:[[:space:]]*/, ""); print; exit}' "$file")
    title=$(awk '/^---$/{n++; next} n==1 && /^title:/{gsub(/^title:[[:space:]]*"?/, ""); gsub(/"$/, ""); print; exit}' "$file")
    status=$(awk '/^---$/{n++; next} n==1 && /^status:/{gsub(/^status:[[:space:]]*/, ""); print; exit}' "$file")

    local rel_path="${file#"${REPO_ROOT}/"}"
    results=$(echo "$results" | jq \
      --arg si "$si_val" \
      --arg id "$artifact_id" \
      --arg title "$title" \
      --arg status "$status" \
      --arg file "$rel_path" \
      '. + [{source_issue: $si, artifact: $id, title: $title, status: $status, file: $file}]')
  done < <(find "$docs_root" -name '*.md' -print0 2>/dev/null)

  echo "$results"
}

# ── Transition hooks (called by swain-design during phase transitions) ───────

# Post a transition comment to the linked issue.
# Usage: issue-integration.sh transition-comment <source-issue> <artifact-id> <new-phase>
cmd_transition_comment() {
  local source_issue="$1" artifact_id="$2" new_phase="$3"

  parse_source_issue "$source_issue"

  local message="**${artifact_id}** transitioned to **${new_phase}**."

  case "$SI_BACKEND" in
    github) github_comment "$SI_OWNER" "$SI_REPO" "$SI_NUMBER" "$message" ;;
    *)      die "No backend for: $SI_BACKEND" ;;
  esac
}

# Close the linked issue (for Implemented transitions).
# Usage: issue-integration.sh transition-close <source-issue> <artifact-id>
cmd_transition_close() {
  local source_issue="$1" artifact_id="$2"

  parse_source_issue "$source_issue"

  local message="Closing: **${artifact_id}** has been implemented."

  case "$SI_BACKEND" in
    github) github_close "$SI_OWNER" "$SI_REPO" "$SI_NUMBER" "$message" ;;
    *)      die "No backend for: $SI_BACKEND" ;;
  esac
}

# ── Main dispatch ────────────────────────────────────────────────────────────

cmd="${1:-help}"
shift || true

case "$cmd" in
  check)
    github_check
    ;;

  promote)
    [[ $# -lt 1 ]] && die "Usage: issue-integration.sh promote <issue-url-or-ref>"
    local_ref="$1"

    # Accept either github:<owner>/<repo>#<number> or https://github.com/<owner>/<repo>/issues/<number>
    if [[ "$local_ref" =~ ^github: ]]; then
      parse_source_issue "$local_ref"
    elif [[ "$local_ref" =~ github\.com/([^/]+)/([^/]+)/issues/([0-9]+) ]]; then
      SI_BACKEND="github"
      SI_OWNER="${BASH_REMATCH[1]}"
      SI_REPO="${BASH_REMATCH[2]}"
      SI_NUMBER="${BASH_REMATCH[3]}"
    else
      die "Cannot parse issue reference: $local_ref"
    fi

    case "$SI_BACKEND" in
      github) github_promote "$SI_OWNER" "$SI_REPO" "$SI_NUMBER" ;;
      *)      die "No backend for: $SI_BACKEND" ;;
    esac
    ;;

  comment)
    [[ $# -lt 2 ]] && die "Usage: issue-integration.sh comment <source-issue> <message>"
    parse_source_issue "$1"
    case "$SI_BACKEND" in
      github) github_comment "$SI_OWNER" "$SI_REPO" "$SI_NUMBER" "$2" ;;
      *)      die "No backend for: $SI_BACKEND" ;;
    esac
    ;;

  close)
    [[ $# -lt 2 ]] && die "Usage: issue-integration.sh close <source-issue> <message>"
    parse_source_issue "$1"
    case "$SI_BACKEND" in
      github) github_close "$SI_OWNER" "$SI_REPO" "$SI_NUMBER" "$2" ;;
      *)      die "No backend for: $SI_BACKEND" ;;
    esac
    ;;

  scan)
    cmd_scan "${1:-}"
    ;;

  transition-comment)
    [[ $# -lt 3 ]] && die "Usage: issue-integration.sh transition-comment <source-issue> <artifact-id> <new-phase>"
    cmd_transition_comment "$1" "$2" "$3"
    ;;

  transition-close)
    [[ $# -lt 2 ]] && die "Usage: issue-integration.sh transition-close <source-issue> <artifact-id>"
    cmd_transition_close "$1" "$2"
    ;;

  help|--help|-h)
    echo "Usage: issue-integration.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  check                           Verify gh CLI availability"
    echo "  promote <issue-ref>             Fetch issue data for SPEC creation"
    echo "  comment <source-issue> <msg>    Post comment to linked issue"
    echo "  close   <source-issue> <msg>    Close linked issue with comment"
    echo "  scan    [docs-root]             Find all artifacts with source-issue"
    echo "  transition-comment <si> <id> <phase>  Post transition comment"
    echo "  transition-close   <si> <id>    Close issue on Implemented"
    echo ""
    echo "source-issue format: github:<owner>/<repo>#<number>"
    ;;

  *)
    die "Unknown command: $cmd (try: help)"
    ;;
esac
