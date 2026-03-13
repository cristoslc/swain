#!/usr/bin/env bash
set -euo pipefail

# swain-status.sh — Cross-cutting project status aggregator
#
# Collects data from specgraph, tk (tickets), git, GitHub, and session state.
# Writes a structured JSON cache and outputs rich terminal text.
#
# Usage:
#   swain-status.sh                  # full rich output (for in-conversation display)
#   swain-status.sh --compact        # condensed output (for MOTD consumption)
#   swain-status.sh --json           # raw JSON cache (for programmatic access)
#   swain-status.sh --refresh        # force-refresh cache, then full output

# --- Resolve paths ---
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: not inside a git repository" >&2
  exit 1
}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SPECGRAPH="$SCRIPT_DIR/../../swain-design/scripts/specgraph.sh"

PROJECT_NAME="$(basename "$REPO_ROOT")"
SETTINGS_PROJECT="$REPO_ROOT/swain.settings.json"
SETTINGS_USER="${XDG_CONFIG_HOME:-$HOME/.config}/swain/settings.json"

# Memory directory (Claude Code convention — slug derived from repo path)
_PROJECT_SLUG=$(echo "$REPO_ROOT" | tr '/' '-')
MEMORY_DIR="${SWAIN_MEMORY_DIR:-$HOME/.claude/projects/${_PROJECT_SLUG}/memory}"
CACHE_FILE="$MEMORY_DIR/status-cache.json"
SESSION_FILE="$MEMORY_DIR/session.json"

# GitHub remote
GH_REMOTE_URL="$(git remote get-url origin 2>/dev/null || echo "")"
GH_REPO=""
if [[ "$GH_REMOTE_URL" =~ github\.com[:/]([^/]+/[^/.]+) ]]; then
  GH_REPO="${BASH_REMATCH[1]}"
fi

# Cache TTL in seconds (default: 120)
CACHE_TTL=120

# --- Settings reader ---
read_setting() {
  local key="$1" default="$2" val=""
  if [[ -f "$SETTINGS_USER" ]]; then
    val=$(jq -r "$key // empty" "$SETTINGS_USER" 2>/dev/null) || true
  fi
  if [[ -z "$val" && -f "$SETTINGS_PROJECT" ]]; then
    val=$(jq -r "$key // empty" "$SETTINGS_PROJECT" 2>/dev/null) || true
  fi
  echo "${val:-$default}"
}

# --- OSC 8 hyperlink helpers ---
# Usage: link "URL" "display text"
link() {
  local url="$1" text="$2"
  printf '\e]8;;%s\e\\%s\e]8;;\e\\' "$url" "$text"
}

file_link() {
  local filepath="$1" display="${2:-$(basename "$1")}"
  link "file://${filepath}" "$display"
}

gh_issue_link() {
  local number="$1" title="$2"
  if [[ -n "$GH_REPO" ]]; then
    link "https://github.com/${GH_REPO}/issues/${number}" "#${number} ${title}"
  else
    echo "#${number} ${title}"
  fi
}

artifact_link() {
  local id="$1" file="$2" display="$1"
  if [[ -n "$file" ]]; then
    file_link "${REPO_ROOT}/${file}" "$display"
  else
    echo "$display"
  fi
}

# --- Data collectors ---

collect_git() {
  local branch dirty changed_count last_hash last_msg last_age recent_json

  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")

  if git diff --quiet HEAD 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
    dirty="false"
    changed_count=0
  else
    dirty="true"
    changed_count=$(git diff --name-only HEAD 2>/dev/null | wc -l | tr -d ' ')
  fi

  last_hash=$(git log -1 --pretty=format:'%h' 2>/dev/null || echo "")
  last_msg=$(git log -1 --pretty=format:'%s' 2>/dev/null || echo "")
  last_age=$(git log -1 --pretty=format:'%cr' 2>/dev/null || echo "")

  # Recent commits (last 5)
  recent_json=$(git log -5 --pretty=format:'{"hash":"%h","message":"%s","age":"%cr"}' 2>/dev/null | jq -s '.' 2>/dev/null || echo "[]")

  jq -n \
    --arg branch "$branch" \
    --argjson dirty "$dirty" \
    --argjson changed "$changed_count" \
    --arg lastHash "$last_hash" \
    --arg lastMsg "$last_msg" \
    --arg lastAge "$last_age" \
    --argjson recent "$recent_json" \
    '{
      branch: $branch,
      dirty: $dirty,
      changedFiles: $changed,
      lastCommit: { hash: $lastHash, message: $lastMsg, age: $lastAge },
      recentCommits: $recent
    }'
}

collect_artifacts() {
  # Ensure specgraph cache is fresh
  if [[ -x "$SPECGRAPH" ]] || [[ -f "$SPECGRAPH" ]]; then
    bash "$SPECGRAPH" build >/dev/null 2>&1 || true
  fi

  # Read specgraph cache
  local REPO_HASH
  REPO_HASH=$(printf '%s' "$REPO_ROOT" | shasum -a 256 | cut -c1-12)
  local SG_CACHE="/tmp/agents-specgraph-${REPO_HASH}.json"

  if [[ ! -f "$SG_CACHE" ]]; then
    echo '{"ready":[],"blocked":[],"epics":{},"counts":{"total":0,"resolved":0,"ready":0,"blocked":0}}'
    return
  fi

  jq '
    def is_resolved: test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined");

    .nodes as $nodes |
    .edges as $edges |

    # All unresolved
    [$nodes | to_entries[] | select(.value.status | is_resolved | not)] as $unresolved |

    # Ready: unresolved with no unresolved deps, enriched with unblock info
    ([$unresolved[] |
      .key as $id |
      ([$edges[] | select(.from == $id and .type == "depends-on") | .to] | unique) as $deps |
      select(
        ($deps | length == 0) or
        ($deps | all(. as $dep | $nodes[$dep] == null or ($nodes[$dep].status | is_resolved)))
      ) |
      # What unresolved items depend on this one?
      ([$edges[] | select(.to == $id and .type == "depends-on") | .from] |
        map(select(. as $dep | $nodes[$dep] != null and ($nodes[$dep].status | is_resolved | not))) |
        unique) as $unblocks |
      {id: .key, status: .value.status, title: .value.title, type: .value.type, file: .value.file, description: .value.description, unblocks: $unblocks}
    ] | sort_by(-(.unblocks | length), .id)) as $ready |

    # Blocked
    ([$unresolved[] |
      .key as $id |
      ([$edges[] | select(.from == $id and .type == "depends-on") | .to] | unique) as $deps |
      ($deps | map(select(. as $dep | $nodes[$dep] != null and ($nodes[$dep].status | is_resolved | not)))) as $waiting |
      select(($waiting | length) > 0) |
      {id: .key, status: .value.status, title: .value.title, type: .value.type, file: .value.file, description: .value.description, waiting: $waiting}
    ] | sort_by(.id)) as $blocked |

    # Epic progress: for each active epic, count child spec status
    ([$nodes | to_entries[] |
      select(.value.type == "EPIC" and (.value.status | is_resolved | not)) |
      .key as $epic_id |
      # Find children (specs/stories parented to this epic)
      ([$edges[] | select(.to == $epic_id and .type == "parent-epic") | .from]) as $child_ids |
      ($child_ids | map(. as $cid | $nodes[$cid]) | map(select(. != null))) as $children |
      ($children | map(select(.status | is_resolved)) | length) as $done |
      ($children | length) as $total |
      {
        id: $epic_id,
        title: .value.title,
        status: .value.status,
        file: .value.file,
        progress: { done: $done, total: $total },
        children: [$child_ids[] | . as $cid | $nodes[$cid] | select(. != null) |
          {id: $cid, title: .title, status: .status, type: .type, file: .file, description: .description}
        ]
      }
    ] | sort_by(.id)) as $epics |

    # Counts
    ([$nodes | to_entries[]] | length) as $total |
    ([$nodes | to_entries[] | select(.value.status | is_resolved)] | length) as $resolved |

    {
      ready: $ready,
      blocked: $blocked,
      epics: ($epics | map({(.id): .}) | add // {}),
      counts: {
        total: $total,
        resolved: $resolved,
        ready: ($ready | length),
        blocked: ($blocked | length)
      }
    }
  ' "$SG_CACHE"
}

collect_tasks() {
  # Locate .tickets directory and ticket-query
  local tickets_dir=""
  if [[ -d "$REPO_ROOT/.tickets" ]]; then
    tickets_dir="$REPO_ROOT/.tickets"
  fi

  local tq_bin=""
  local skill_bin="$REPO_ROOT/skills/swain-do/bin/ticket-query"
  if [[ -x "$skill_bin" ]]; then
    tq_bin="$skill_bin"
  elif command -v ticket-query &>/dev/null; then
    tq_bin="ticket-query"
  fi

  if [[ -z "$tickets_dir" ]] || [[ -z "$tq_bin" ]]; then
    echo '{"inProgress":[],"recentlyCompleted":[],"total":0,"available":false}'
    return
  fi

  local in_progress recent total raw

  # In-progress tasks
  raw=$(TICKETS_DIR="$tickets_dir" "$tq_bin" '.status == "in_progress"' 2>/dev/null | jq -c '{id: .id, title: .title}' 2>/dev/null) || true
  if [[ -n "$raw" ]]; then
    in_progress=$(echo "$raw" | jq -s '.' 2>/dev/null || echo "[]")
  else
    in_progress="[]"
  fi

  # Recently completed (last 5)
  raw=$(TICKETS_DIR="$tickets_dir" "$tq_bin" '.status == "closed"' 2>/dev/null | jq -c '{id: .id, title: .title}' 2>/dev/null | head -5) || true
  if [[ -n "$raw" ]]; then
    recent=$(echo "$raw" | jq -s '.' 2>/dev/null || echo "[]")
  else
    recent="[]"
  fi

  # Total count
  total=$(TICKETS_DIR="$tickets_dir" "$tq_bin" 2>/dev/null | wc -l | tr -d ' ') || true
  total="${total:-0}"

  jq -n \
    --argjson inProgress "$in_progress" \
    --argjson recent "$recent" \
    --argjson total "${total}" \
    '{inProgress: $inProgress, recentlyCompleted: $recent, total: $total, available: true}'
}

collect_issues() {
  if [[ -z "$GH_REPO" ]] || ! command -v gh &>/dev/null; then
    echo '{"open":[],"assigned":[],"available":false}'
    return
  fi

  local open assigned

  # Open issues (limit 10, most recent)
  open=$(gh issue list --repo "$GH_REPO" --state open --limit 10 --json number,title,labels,assignees,updatedAt 2>/dev/null || echo "[]")

  # Assigned to current user
  local gh_user
  gh_user=$(gh api user --jq '.login' 2>/dev/null || echo "")
  if [[ -n "$gh_user" ]]; then
    assigned=$(gh issue list --repo "$GH_REPO" --state open --assignee "$gh_user" --limit 10 --json number,title,labels,updatedAt 2>/dev/null || echo "[]")
  else
    assigned="[]"
  fi

  jq -n \
    --argjson open "$open" \
    --argjson assigned "$assigned" \
    '{open: $open, assigned: $assigned, available: true}'
}

collect_linked_issues() {
  local ISSUE_SCRIPT="$SCRIPT_DIR/../../swain-design/scripts/issue-integration.sh"

  if [[ ! -f "$ISSUE_SCRIPT" ]]; then
    echo '[]'
    return
  fi

  local linked
  linked=$(bash "$ISSUE_SCRIPT" scan 2>/dev/null) || linked="[]"

  # Enrich with live GitHub issue data if gh is available
  if command -v gh &>/dev/null && [[ "$linked" != "[]" ]]; then
    echo "$linked" | jq -c '.[]' | while IFS= read -r entry; do
      local si
      si=$(echo "$entry" | jq -r '.source_issue')

      # Parse github:<owner>/<repo>#<number>
      if [[ "$si" =~ ^github:([^/]+)/([^#]+)#([0-9]+)$ ]]; then
        local owner="${BASH_REMATCH[1]}" repo="${BASH_REMATCH[2]}" number="${BASH_REMATCH[3]}"
        local issue_state issue_title
        issue_state=$(gh issue view "$number" --repo "${owner}/${repo}" --json state --jq '.state' 2>/dev/null || echo "UNKNOWN")
        issue_title=$(gh issue view "$number" --repo "${owner}/${repo}" --json title --jq '.title' 2>/dev/null || echo "")
        echo "$entry" | jq \
          --arg issue_state "$issue_state" \
          --arg issue_title "$issue_title" \
          --argjson issue_number "$number" \
          '. + {issue_state: $issue_state, issue_title: $issue_title, issue_number: $issue_number}'
      else
        echo "$entry"
      fi
    done | jq -s '.'
  else
    echo "$linked"
  fi
}

collect_session() {
  if [[ -f "$SESSION_FILE" ]]; then
    jq '{
      bookmark: (.bookmark // null),
      lastBranch: (.lastBranch // null),
      lastContext: (.lastContext // null)
    }' "$SESSION_FILE" 2>/dev/null || echo '{"bookmark":null,"lastBranch":null,"lastContext":null}'
  else
    echo '{"bookmark":null,"lastBranch":null,"lastContext":null}'
  fi
}

# --- Build cache ---

build_cache() {
  local git_data artifact_data task_data issue_data session_data

  # Collect in parallel where possible
  git_data=$(collect_git)
  artifact_data=$(collect_artifacts)
  task_data=$(collect_tasks)
  issue_data=$(collect_issues)
  linked_issue_data=$(collect_linked_issues)
  session_data=$(collect_session)

  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  jq -n \
    --arg ts "$timestamp" \
    --arg repo "$REPO_ROOT" \
    --arg project "$PROJECT_NAME" \
    --argjson git "$git_data" \
    --argjson artifacts "$artifact_data" \
    --argjson tasks "$task_data" \
    --argjson issues "$issue_data" \
    --argjson session "$session_data" \
    --argjson linked "$linked_issue_data" \
    '{
      timestamp: $ts,
      repo: $repo,
      project: $project,
      git: $git,
      artifacts: $artifacts,
      tasks: $tasks,
      issues: $issues,
      linkedIssues: $linked,
      session: $session
    }' > "$CACHE_FILE"
}

cache_is_fresh() {
  [[ -f "$CACHE_FILE" ]] || return 1
  local cache_age
  if [[ "$(uname)" == "Darwin" ]]; then
    cache_age=$(( $(date +%s) - $(stat -f %m "$CACHE_FILE") ))
  else
    cache_age=$(( $(date +%s) - $(stat -c %Y "$CACHE_FILE") ))
  fi
  [[ "$cache_age" -lt "$CACHE_TTL" ]]
}

ensure_cache() {
  if ! cache_is_fresh; then
    build_cache
  fi
}

# --- Output formatters ---

# Full rich output for in-conversation display
render_full() {
  local data
  data=$(cat "$CACHE_FILE")

  local project branch dirty changed_count
  project=$(echo "$data" | jq -r '.project')
  branch=$(echo "$data" | jq -r '.git.branch')
  dirty=$(echo "$data" | jq -r '.git.dirty')
  changed_count=$(echo "$data" | jq -r '.git.changedFiles')

  echo ""
  echo "# ${project} — Status"
  echo ""

  # --- Session bookmark ---
  local bookmark_note
  bookmark_note=$(echo "$data" | jq -r '.session.bookmark.note // empty')
  if [[ -n "$bookmark_note" ]]; then
    echo "**Resuming:** ${bookmark_note}"
    local bookmark_files
    bookmark_files=$(echo "$data" | jq -r '.session.bookmark.files // [] | .[]' 2>/dev/null)
    if [[ -n "$bookmark_files" ]]; then
      echo -n "  Files: "
      local first=1
      while IFS= read -r f; do
        [[ $first -eq 1 ]] && first=0 || echo -n ", "
        file_link "${REPO_ROOT}/${f}" "$f"
      done <<< "$bookmark_files"
      echo ""
    fi
    echo ""
  fi

  # --- Pipeline ---
  echo "## Pipeline"
  echo ""
  echo -n "Branch: **${branch}**"
  if [[ "$dirty" == "true" ]]; then
    echo " (${changed_count} uncommitted changes)"
  else
    echo " (clean)"
  fi

  local last_msg last_age last_hash
  last_msg=$(echo "$data" | jq -r '.git.lastCommit.message')
  last_age=$(echo "$data" | jq -r '.git.lastCommit.age')
  last_hash=$(echo "$data" | jq -r '.git.lastCommit.hash')
  echo "Last commit: \`${last_hash}\` ${last_msg} (${last_age})"
  echo ""

  # --- Active Epics with progress ---
  local epic_count
  epic_count=$(echo "$data" | jq '.artifacts.epics | length')

  if [[ "$epic_count" -gt 0 ]]; then
    echo "## Active Epics"
    echo ""
    echo "$data" | jq -r --arg repo "$REPO_ROOT" '
      def art_link($aid; $file):
        if $file != null and $file != "" then
          "\u001b]8;;file://\($repo)/\($file)\u001b\\\($aid)\u001b]8;;\u001b\\"
        else $aid end;
      def next_step:
        if .type == "SPEC" and .status == "Draft" then "review and approve"
        elif .type == "SPEC" and .status == "Approved" then "create implementation plan"
        elif .type == "SPEC" and .status == "Implementing" then "complete implementation"
        elif .type == "STORY" and .status == "Draft" then "refine acceptance criteria"
        elif .type == "STORY" and .status == "Approved" then "create implementation plan"
        elif .type == "SPIKE" and .status == "Planned" then "begin investigation"
        elif .type == "SPIKE" and .status == "Active" then "complete findings"
        elif .type == "BUG" then "triage and fix"
        else "progress to next phase" end;
      .artifacts.epics | to_entries[] |
      .value as $e |
      "### \(art_link($e.id; $e.file)): \($e.title) [\($e.status)]",
      "",
      (if $e.progress.total == 0 then
        "Progress: **needs decomposition into specs**"
      elif $e.progress.done == $e.progress.total then
        "Progress: **all \($e.progress.total) specs resolved** — ready for completion"
      else
        "Progress: **\($e.progress.done)/\($e.progress.total)** specs resolved (\($e.progress.total - $e.progress.done) remaining)"
      end),
      "",
      ($e.children | sort_by(.status) | .[] |
        (if (.status | test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined"))
         then "  - [x]"
         else "  - [ ]"
         end) + " \(art_link(.id; .file)): \(.title) [\(.status)]" +
        (if (.status | test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined") | not)
         then " — \(next_step)"
         else "" end),
        (if .description and (.description | length > 0) then
          "    _\(.description)_"
        else empty end)
      ),
      ""
    '
  fi

  # --- Decision backlog / Implementation backlog split ---
  #
  # Classify each ready item as a "decision" (needs human judgment) or
  # "implementation" (agent can handle).  Show decisions first — they are
  # the developer's bottleneck.
  local ready_count
  ready_count=$(echo "$data" | jq '.artifacts.ready | length')

  if [[ "$ready_count" -gt 0 ]]; then
    # Count decisions vs implementation items
    local decision_count
    decision_count=$(echo "$data" | jq '
      def is_decision:
        (.type == "SPEC" and .status == "Draft") or
        (.type == "STORY" and .status == "Draft") or
        (.type == "SPIKE" and (.status | test("Planned|Active"))) or
        (.type == "ADR" and .status == "Proposed") or
        (.type == "VISION" and .status == "Draft") or
        (.type == "JOURNEY" and (.status | test("Draft|Planned"))) or
        (.type == "PERSONA" and .status == "Draft") or
        (.type == "EPIC" and (.status | test("Proposed|Planned"))) or
        (.type == "BUG") or
        (.type == "RUNBOOK" and .status == "Draft") or
        (.type == "DESIGN" and .status == "Draft");
      [.artifacts.ready[] | select(is_decision)] | length
    ')

    # --- Decisions waiting on you ---
    if [[ "$decision_count" -gt 0 ]]; then
      echo "## Decisions Waiting on You (${decision_count})"
      echo ""
      echo "$data" | jq -r --arg repo "$REPO_ROOT" '
        def art_link($aid; $file):
          if $file != null and $file != "" then
            "\u001b]8;;file://\($repo)/\($file)\u001b\\\($aid)\u001b]8;;\u001b\\"
          else $aid end;
        def next_step:
          if .type == "EPIC" and (.status | test("Proposed|Planned")) then "activate and decompose into specs"
          elif .type == "EPIC" and (.status | test("Active")) then "work on child specs"
          elif .type == "SPEC" and .status == "Draft" then "review and approve"
          elif .type == "SPEC" and .status == "Approved" then "create implementation plan"
          elif .type == "SPEC" and .status == "Implementing" then "complete implementation"
          elif .type == "STORY" and .status == "Draft" then "refine acceptance criteria"
          elif .type == "STORY" and .status == "Approved" then "create implementation plan"
          elif .type == "SPIKE" and .status == "Planned" then "begin investigation"
          elif .type == "SPIKE" and .status == "Active" then "complete findings"
          elif .type == "ADR" and .status == "Proposed" then "review and decide"
          elif .type == "VISION" and .status == "Draft" then "align on goals and audience"
          elif .type == "JOURNEY" and (.status | test("Draft|Planned")) then "map pain points and opportunities"
          elif .type == "BUG" then "triage and fix"
          elif .type == "PERSONA" and .status == "Draft" then "validate with user research"
          elif .type == "RUNBOOK" and .status == "Draft" then "test procedure and finalize"
          elif .type == "DESIGN" and .status == "Draft" then "review interaction flows"
          else "progress to next phase" end;
        def is_decision:
          (.type == "SPEC" and .status == "Draft") or
          (.type == "STORY" and .status == "Draft") or
          (.type == "SPIKE" and (.status | test("Planned|Active"))) or
          (.type == "ADR" and .status == "Proposed") or
          (.type == "VISION" and .status == "Draft") or
          (.type == "JOURNEY" and (.status | test("Draft|Planned"))) or
          (.type == "PERSONA" and .status == "Draft") or
          (.type == "EPIC" and (.status | test("Proposed|Planned"))) or
          (.type == "BUG") or
          (.type == "RUNBOOK" and .status == "Draft") or
          (.type == "DESIGN" and .status == "Draft");
        [.artifacts.ready[] | select(is_decision)] | sort_by(-(.unblocks | length), .id)[] |
        "- \(art_link(.id; .file)): \(.title) [\(.status)] — \(next_step)" +
        (if (.unblocks | length) > 0 then " (unblocks \(.unblocks | length))" else "" end),
        (if .description and (.description | length > 0) then
          "  _\(.description)_"
        else empty end)
      '
      echo ""
    fi

    # --- Implementation (agent can handle) ---
    local impl_count
    impl_count=$(( ready_count - decision_count ))

    if [[ "$impl_count" -gt 0 ]]; then
      echo "## Implementation (${impl_count} — agent can handle)"
      echo ""
      echo "$data" | jq -r --arg repo "$REPO_ROOT" '
        def art_link($aid; $file):
          if $file != null and $file != "" then
            "\u001b]8;;file://\($repo)/\($file)\u001b\\\($aid)\u001b]8;;\u001b\\"
          else $aid end;
        def next_step:
          if .type == "EPIC" and (.status | test("Proposed|Planned")) then "activate and decompose into specs"
          elif .type == "EPIC" and (.status | test("Active")) then "work on child specs"
          elif .type == "SPEC" and .status == "Draft" then "review and approve"
          elif .type == "SPEC" and .status == "Approved" then "create implementation plan"
          elif .type == "SPEC" and .status == "Implementing" then "complete implementation"
          elif .type == "STORY" and .status == "Draft" then "refine acceptance criteria"
          elif .type == "STORY" and .status == "Approved" then "create implementation plan"
          elif .type == "SPIKE" and .status == "Planned" then "begin investigation"
          elif .type == "SPIKE" and .status == "Active" then "complete findings"
          elif .type == "ADR" and .status == "Proposed" then "review and decide"
          elif .type == "VISION" and .status == "Draft" then "align on goals and audience"
          elif .type == "JOURNEY" and (.status | test("Draft|Planned")) then "map pain points and opportunities"
          elif .type == "BUG" then "triage and fix"
          elif .type == "PERSONA" and .status == "Draft" then "validate with user research"
          elif .type == "RUNBOOK" and .status == "Draft" then "test procedure and finalize"
          elif .type == "DESIGN" and .status == "Draft" then "review interaction flows"
          else "progress to next phase" end;
        def is_decision:
          (.type == "SPEC" and .status == "Draft") or
          (.type == "STORY" and .status == "Draft") or
          (.type == "SPIKE" and (.status | test("Planned|Active"))) or
          (.type == "ADR" and .status == "Proposed") or
          (.type == "VISION" and .status == "Draft") or
          (.type == "JOURNEY" and (.status | test("Draft|Planned"))) or
          (.type == "PERSONA" and .status == "Draft") or
          (.type == "EPIC" and (.status | test("Proposed|Planned"))) or
          (.type == "BUG") or
          (.type == "RUNBOOK" and .status == "Draft") or
          (.type == "DESIGN" and .status == "Draft");
        [.artifacts.ready[] | select(is_decision | not)] | sort_by(-(.unblocks | length), .id)[] |
        "- \(art_link(.id; .file)): \(.title) [\(.status)] — \(next_step)" +
        (if (.unblocks | length) > 0 then " (unblocks \(.unblocks | length))" else "" end),
        (if .description and (.description | length > 0) then
          "  _\(.description)_"
        else empty end)
      '
      echo ""
    fi
  fi

  # --- Blocked ---
  local blocked_count
  blocked_count=$(echo "$data" | jq '.artifacts.blocked | length')

  if [[ "$blocked_count" -gt 0 ]]; then
    echo "## Blocked"
    echo ""
    echo "$data" | jq -r --arg repo "$REPO_ROOT" '
      def art_link($aid; $file):
        if $file != null and $file != "" then
          "\u001b]8;;file://\($repo)/\($file)\u001b\\\($aid)\u001b]8;;\u001b\\"
        else $aid end;
      # Build a lookup of ready item IDs for unblock hints
      ([.artifacts.ready[].id] | unique) as $ready_ids |
      .artifacts.blocked[] |
      "- \(art_link(.id; .file)): \(.title) [\(.status)]" +
      "  <- waiting on: \(.waiting | map(
        . as $w |
        if ($ready_ids | index($w)) then "\($w) (actionable now)"
        else $w end
      ) | join(", "))",
      (if .description and (.description | length > 0) then
        "  _\(.description)_"
      else empty end)'
    echo ""
  fi

  # --- Tasks (tk) ---
  local tasks_available
  tasks_available=$(echo "$data" | jq -r '.tasks.available')

  if [[ "$tasks_available" == "true" ]]; then
    local ip_count
    ip_count=$(echo "$data" | jq '.tasks.inProgress | length')

    echo "## Tasks"
    echo ""
    if [[ "$ip_count" -gt 0 ]]; then
      echo "**In progress:**"
      echo "$data" | jq -r '.tasks.inProgress[] | "- \(.id) \(.title)"'
    else
      echo "No tasks in progress."
    fi

    local recent_count
    recent_count=$(echo "$data" | jq '.tasks.recentlyCompleted | length')
    if [[ "$recent_count" -gt 0 ]]; then
      echo ""
      echo "**Recently completed:**"
      echo "$data" | jq -r '.tasks.recentlyCompleted[] | "- \(.id) \(.title)"'
    fi

    local total_tasks
    total_tasks=$(echo "$data" | jq -r '.tasks.total')
    echo ""
    echo "${total_tasks} total tracked issues."
    echo ""
  fi

  # --- GitHub Issues ---
  local issues_available
  issues_available=$(echo "$data" | jq -r '.issues.available')

  if [[ "$issues_available" == "true" ]]; then
    local assigned_count open_count
    assigned_count=$(echo "$data" | jq '.issues.assigned | length')
    open_count=$(echo "$data" | jq '.issues.open | length')

    if [[ "$assigned_count" -gt 0 || "$open_count" -gt 0 ]]; then
      echo "## GitHub Issues"
      echo ""
    fi

    if [[ "$assigned_count" -gt 0 ]]; then
      echo "**Assigned to you:**"
      while IFS= read -r line; do
        local num title
        num=$(echo "$line" | jq -r '.number')
        title=$(echo "$line" | jq -r '.title')
        echo -n "- "
        gh_issue_link "$num" "$title"
        echo ""
      done < <(echo "$data" | jq -c '.issues.assigned[]')
      echo ""
    fi

    if [[ "$open_count" -gt 0 && "$assigned_count" -eq 0 ]]; then
      echo "**Open issues:**"
      while IFS= read -r line; do
        local num title
        num=$(echo "$line" | jq -r '.number')
        title=$(echo "$line" | jq -r '.title')
        echo -n "- "
        gh_issue_link "$num" "$title"
        echo ""
      done < <(echo "$data" | jq -c '.issues.open[] | select(.number)' | head -5)
      echo ""
    fi
  fi

  # --- Linked Issues (source-issue artifacts) ---
  local linked_count
  linked_count=$(echo "$data" | jq '.linkedIssues | length')

  if [[ "$linked_count" -gt 0 ]]; then
    echo "## Linked Issues"
    echo ""
    echo "$data" | jq -r --arg repo "$REPO_ROOT" '
      def art_link($aid; $file):
        if $file != null and $file != "" then
          "\u001b]8;;file://\($repo)/\($file)\u001b\\\($aid)\u001b]8;;\u001b\\"
        else $aid end;
      .linkedIssues[] |
      "- \(art_link(.artifact; .file)): \(.title) [\(.status)]" +
      (if .issue_number then
        " — linked to #\(.issue_number)" +
        (if .issue_state then " (\(.issue_state | ascii_downcase))" else "" end)
      else
        " — \(.source_issue)"
      end)
    '
    echo ""
  fi

  # --- Artifact counts footer ---
  local total resolved ready blocked
  total=$(echo "$data" | jq -r '.artifacts.counts.total')
  resolved=$(echo "$data" | jq -r '.artifacts.counts.resolved')
  ready=$(echo "$data" | jq -r '.artifacts.counts.ready')
  blocked=$(echo "$data" | jq -r '.artifacts.counts.blocked')

  echo "---"
  echo "Artifacts: ${total} total, ${resolved} resolved, ${ready} ready, ${blocked} blocked"

  local ts
  ts=$(echo "$data" | jq -r '.timestamp')
  echo "Updated: ${ts}"
}

# Compact output for MOTD consumption
render_compact() {
  local data
  data=$(cat "$CACHE_FILE")

  local branch dirty epic_summary task_line

  branch=$(echo "$data" | jq -r '.git.branch')
  dirty=$(echo "$data" | jq -r 'if .git.dirty then "\(.git.changedFiles) changed" else "clean" end')

  # Epic progress summary (most active epic)
  epic_summary=$(echo "$data" | jq -r '
    .artifacts.epics | to_entries |
    if length > 0 then
      (.[0].value) as $e |
      "\($e.id) \($e.progress.done)/\($e.progress.total)"
    else "no active epics" end
  ')

  # Active task
  task_line=$(echo "$data" | jq -r '
    if .tasks.inProgress | length > 0 then
      .tasks.inProgress[0] | "\(.id) \(.title)" | .[0:40]
    else "no active task" end
  ')

  # Ready count
  local ready_count
  ready_count=$(echo "$data" | jq -r '.artifacts.counts.ready')

  # Issue count
  local issue_count
  issue_count=$(echo "$data" | jq -r '.issues.assigned | length // 0')

  echo "${branch} (${dirty})"
  echo "epic: ${epic_summary}"
  echo "task: ${task_line}"
  echo "ready: ${ready_count} actionable"
  if [[ "$issue_count" -gt 0 ]]; then
    echo "issues: ${issue_count} assigned"
  fi
}

# --- Main ---

MODE="full"
FORCE_REFRESH=0

for arg in "$@"; do
  case "$arg" in
    --compact)  MODE="compact" ;;
    --json)     MODE="json" ;;
    --refresh)  FORCE_REFRESH=1 ;;
    --help|-h)
      echo "Usage: swain-status.sh [--compact|--json] [--refresh]"
      echo ""
      echo "  (default)   Rich terminal output with clickable links"
      echo "  --compact   Condensed output for MOTD panel"
      echo "  --json      Raw JSON cache"
      echo "  --refresh   Force cache rebuild before output"
      exit 0
      ;;
  esac
done

if [[ "$FORCE_REFRESH" -eq 1 ]]; then
  build_cache
else
  ensure_cache
fi

case "$MODE" in
  full)    render_full ;;
  compact) render_compact ;;
  json)    cat "$CACHE_FILE" ;;
esac
