#!/bin/bash
# specgraph.sh — Build and query the spec artifact dependency graph
# Source of truth: YAML frontmatter in docs/*.md files containing artifact: field
# Cache: /tmp/agents-specgraph-<repo-hash>.json

set -euo pipefail

# --- Resolve repo root ---
# Use the caller's working directory to find the repo root via git,
# not the script's install location (which may be in a different repo).
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: not inside a git repository" >&2
  exit 1
}
DOCS_DIR="$REPO_ROOT/docs"

# --- Cache path ---
REPO_HASH=$(printf '%s' "$REPO_ROOT" | shasum -a 256 | cut -c1-12)
CACHE_FILE="/tmp/agents-specgraph-${REPO_HASH}.json"

# --- Resolved statuses (for ready command) ---
RESOLVED_RE="Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined"

# --- Helpers ---

usage() {
  cat <<'USAGE'
Usage: specgraph.sh <command> [args]

Commands:
  build              Force-rebuild the dependency graph from frontmatter
  blocks <ID>        What does this artifact depend on? (direct dependencies)
  blocked-by <ID>    What depends on this artifact? (inverse lookup)
  tree <ID>          Transitive dependency tree (all ancestors)
  ready              Active/Planned artifacts with all deps resolved
  next               What to work on next (ready items + what they unblock)
  mermaid            Mermaid diagram to stdout
  status             Summary table by type and phase
  overview           Hierarchy tree with status + execution tracking
USAGE
  exit 1
}

# Check if cache needs rebuild: any docs/*.md newer than cache
needs_rebuild() {
  [ ! -f "$CACHE_FILE" ] && return 0
  local newer
  newer=$(find "$DOCS_DIR" -name '*.md' -newer "$CACHE_FILE" 2>/dev/null | head -1) || true
  [ -n "$newer" ]
}

# Extract a single-line frontmatter field value (after "field: ")
# Always succeeds (returns empty string if field not found)
get_field() {
  local file="$1" field="$2"
  local val
  val=$(sed -n '/^---$/,/^---$/p' "$file" | grep "^${field}:" | head -1 | sed "s/^${field}:[[:space:]]*//" | sed 's/^"\(.*\)"$/\1/' | sed "s/^'\(.*\)'$/\1/") || true
  printf '%s' "$val"
}

# Extract a YAML list field as newline-separated bare IDs (TYPE-NNN)
# Always succeeds (returns empty if field not found or has no list items)
get_list_field() {
  local file="$1" field="$2"
  sed -n '/^---$/,/^---$/p' "$file" | \
    sed -n "/^${field}:/,/^[^[:space:]-]/p" | \
    grep '^[[:space:]]*-' | \
    sed 's/^[[:space:]]*-[[:space:]]*//' | \
    sed 's/^"\(.*\)"$/\1/' | \
    sed "s/^'\(.*\)'$/\1/" | \
    grep -oE '[A-Z]+-[0-9]+' || true
}

# Build the graph JSON from frontmatter
do_build() {
  local nodes_json=""
  local edges_json=""
  local first_node=1
  local first_edge=1

  add_edge() {
    local from="$1" to="$2" etype="$3"
    local edge
    edge=$(jq -n --arg from "$from" --arg to "$to" --arg type "$etype" \
      '{from: $from, to: $to, type: $type}')
    if [ $first_edge -eq 1 ]; then
      edges_json="$edge"
      first_edge=0
    else
      edges_json="$edges_json, $edge"
    fi
  }

  # Find all .md files in docs/ that contain "artifact:" in frontmatter
  while IFS= read -r file; do
    # Check if file has artifact: in frontmatter
    local artifact
    artifact=$(get_field "$file" "artifact")
    [ -z "$artifact" ] && continue

    local title status file_rel
    title=$(get_field "$file" "title")
    # Strip leading "TYPE-NNN: " prefix from title if present (avoid duplicate IDs in display)
    title="${title#"$artifact: "}"
    status=$(get_field "$file" "status")
    file_rel="${file#"$REPO_ROOT/"}"

    # Determine type from artifact ID
    local atype
    atype=$(printf '%s' "$artifact" | sed 's/-[0-9]*//')

    # Build node JSON
    local node_json
    node_json=$(jq -n \
      --arg title "$title" \
      --arg status "$status" \
      --arg type "$atype" \
      --arg file "$file_rel" \
      '{title: $title, status: $status, type: $type, file: $file}')

    if [ $first_node -eq 1 ]; then
      nodes_json="\"$artifact\": $node_json"
      first_node=0
    else
      nodes_json="$nodes_json, \"$artifact\": $node_json"
    fi

    # depends-on edges
    while IFS= read -r dep; do
      [ -z "$dep" ] && continue
      add_edge "$artifact" "$dep" "depends-on"
    done <<< "$(get_list_field "$file" "depends-on")"

    # parent-vision edges
    local pv
    pv=$(get_field "$file" "parent-vision")
    if [ -n "$pv" ]; then
      add_edge "$artifact" "$pv" "parent-vision"
    fi

    # parent-epic edges
    local pe
    pe=$(get_field "$file" "parent-epic")
    if [ -n "$pe" ]; then
      add_edge "$artifact" "$pe" "parent-epic"
    fi

  done < <(find "$DOCS_DIR" -name '*.md' -not -name 'README.md' -not -name 'list-*.md' | sort)

  # Assemble final JSON
  local generated
  generated=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  printf '{"generated":"%s","repo":"%s","nodes":{%s},"edges":[%s]}\n' \
    "$generated" "$REPO_ROOT" "$nodes_json" "$edges_json" | jq '.' > "$CACHE_FILE"

  echo "Graph built: $CACHE_FILE"
  echo "  Nodes: $(jq '.nodes | keys | length' "$CACHE_FILE")"
  echo "  Edges: $(jq '.edges | length' "$CACHE_FILE")"
}

# Ensure cache is fresh
ensure_cache() {
  if needs_rebuild; then
    do_build >/dev/null
  fi
}

# blocks <ID> — what does this artifact depend on?
do_blocks() {
  local id="$1"
  ensure_cache
  jq -r --arg id "$id" '
    .edges[] | select(.from == $id and .type == "depends-on") | .to
  ' "$CACHE_FILE" | sort
}

# blocked-by <ID> — what depends on this artifact?
do_blocked_by() {
  local id="$1"
  ensure_cache
  jq -r --arg id "$id" '
    .edges[] | select(.to == $id and .type == "depends-on") | .from
  ' "$CACHE_FILE" | sort
}

# tree <ID> — transitive dependency tree
do_tree() {
  local id="$1"
  ensure_cache

  # Use jq to compute transitive closure
  jq -r --arg id "$id" '
    def transitive_deps($start; $edges):
      def helper($queue; $visited):
        if ($queue | length) == 0 then $visited
        else
          ($queue[0]) as $current |
          ($queue[1:]) as $rest |
          if ($visited | index($current)) then helper($rest; $visited)
          else
            ([$edges[] | select(.from == $current and .type == "depends-on") | .to] | unique) as $deps |
            helper($rest + $deps; $visited + [$current])
          end
        end;
      helper([$start]; []) | .[1:];  # Remove the start node itself

    transitive_deps($id; .edges) | .[]
  ' "$CACHE_FILE" | sort
}

# ready — active/planned artifacts with all deps resolved
do_ready() {
  ensure_cache
  jq -r '
    .nodes as $nodes |
    .edges as $edges |
    [.nodes | to_entries[] |
      select(
        (.value.status | test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined") | not)
      ) |
      .key as $id |
      ([$edges[] | select(.from == $id and .type == "depends-on") | .to] | unique) as $deps |
      select(
        ($deps | length == 0) or
        ($deps | all(. as $dep | $nodes[$dep] != null and ($nodes[$dep].status | test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined"))))
      ) |
      "\(.key)\t\(.value.status)\t\(.value.title)"
    ] | .[]
  ' "$CACHE_FILE" | column -t -s $'\t'
}

# next — what to work on next (ready items + what they'd unblock + blocked items)
do_next() {
  ensure_cache
  # Ready items with what completing them would unblock
  local ready_output
  ready_output=$(jq -r '
    .nodes as $nodes |
    .edges as $edges |
    # Resolved status regex
    def is_resolved: test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined");

    # Find ready (unresolved, all deps satisfied)
    [.nodes | to_entries[] |
      select(.value.status | is_resolved | not) |
      .key as $id |
      ([$edges[] | select(.from == $id and .type == "depends-on") | .to] | unique) as $deps |
      select(
        ($deps | length == 0) or
        ($deps | all(. as $dep | $nodes[$dep] != null and ($nodes[$dep].status | is_resolved)))
      ) |
      # What would completing this unblock?
      ([$edges[] | select(.to == $id and .type == "depends-on") | .from] |
        map(select(. as $blocked |
          [$edges[] | select(.from == $blocked and .type == "depends-on") | .to] |
          all(. as $dep | if $dep == $id then true elif $nodes[$dep] == null then false else ($nodes[$dep].status | is_resolved) end)
        ))
      ) as $would_unblock |
      {id: $id, status: .value.status, title: .value.title, unblocks: $would_unblock}
    ] |
    sort_by(.id) |
    if length == 0 then "  (none)\n"
    else .[] |
      "  \(.id)  (\(.status))  \(.title)" +
      if (.unblocks | length) > 0 then "\n    unblocks: \(.unblocks | join(", "))"
      else "" end
    end
  ' "$CACHE_FILE") || true

  # Blocked items
  local blocked_output
  blocked_output=$(jq -r '
    .nodes as $nodes |
    .edges as $edges |
    def is_resolved: test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined");

    [.nodes | to_entries[] |
      select(.value.status | is_resolved | not) |
      .key as $id |
      ([$edges[] | select(.from == $id and .type == "depends-on") | .to] | unique) as $deps |
      ($deps | map(select(. as $dep | $nodes[$dep] == null or ($nodes[$dep].status | is_resolved | not)))) as $unresolved |
      select(($unresolved | length) > 0) |
      {id: $id, status: .value.status, title: .value.title, waiting: $unresolved}
    ] |
    sort_by(.id) |
    if length == 0 then "  (none)\n"
    else .[] |
      "  \(.id)  (\(.status))  \(.title)\n    waiting on: \(.waiting | join(", "))"
    end
  ' "$CACHE_FILE") || true

  echo "=== Ready ==="
  echo "$ready_output"
  echo ""
  echo "=== Blocked ==="
  echo "$blocked_output"
}

# mermaid — output Mermaid diagram
do_mermaid() {
  ensure_cache
  echo "graph TD"
  # Node labels
  jq -r '
    .nodes | to_entries[] |
    "    \(.key)[\"\(.key): \(.value.title | gsub("\""; "#quot;"))\"]"
  ' "$CACHE_FILE"
  # Edges
  jq -r '
    .edges[] |
    if .type == "depends-on" then
      "    \(.from) -->|depends-on| \(.to)"
    elif .type == "parent-vision" then
      "    \(.from) -.->|child-of| \(.to)"
    elif .type == "parent-epic" then
      "    \(.from) -.->|child-of| \(.to)"
    else empty end
  ' "$CACHE_FILE"
  # Style resolved nodes
  jq -r '
    .nodes | to_entries[] |
    select(.value.status | test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined")) |
    "    style \(.key) fill:#90EE90"
  ' "$CACHE_FILE"
}

# status — summary table
do_status() {
  ensure_cache
  echo "=== Artifact Status Summary ==="
  echo ""
  # Group by type, then by status within type
  jq -r '
    [.nodes | to_entries[] | {type: .value.type, status: .value.status, id: .key, title: .value.title}] |
    group_by(.type) | .[] |
    ("## " + .[0].type),
    (. | sort_by(.id) | .[] | "  \(.id)\t\(.status)\t\(.title)"),
    ""
  ' "$CACHE_FILE" | column -t -s $'\t'
}

# overview — combined hierarchy tree with status indicators, dependency info, and executive summary
do_overview() {
  ensure_cache

  jq -r '
    def is_resolved: test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined");
    def status_icon: if is_resolved then "[x]" else "[ ]" end;
    # Note: titles are already cleaned of ID prefixes during cache build

    .nodes as $nodes |
    .edges as $edges |

    # Find all Vision nodes (top-level)
    ($nodes | to_entries | map(select(.value.type == "VISION")) | sort_by(.key)) as $visions |

    # Find orphans (no parent-vision or parent-epic edge)
    ([$nodes | to_entries[] |
      .key as $id |
      select(
        .value.type != "VISION" and
        ([$edges[] | select(.from == $id and (.type == "parent-vision" or .type == "parent-epic"))] | length == 0)
      )
    ] | sort_by(.key)) as $orphans |

    # Helper: get children of a node by parent edge type
    def children_of($parent_id):
      [$edges[] | select(.to == $parent_id and (.type == "parent-vision" or .type == "parent-epic")) | .from] |
      unique | sort |
      map(. as $id | {id: $id, node: $nodes[$id]}) |
      map(select(.node != null));

    # Helper: get depends-on for a node (unresolved only, skips missing refs)
    def unresolved_deps($id):
      [$edges[] | select(.from == $id and .type == "depends-on") | .to] |
      map(select(. as $dep | $nodes[$dep] != null and ($nodes[$dep].status | is_resolved | not)));

    # Helper: all depends-on for a node (all, not just unresolved)
    def all_deps($id):
      [$edges[] | select(.from == $id and .type == "depends-on") | .to] | unique;

    # Print a node line with icon, id, title, status, and blocked-by info
    def node_line($id; $node; $prefix; $connector):
      ($node.status | status_icon) as $icon |
      (unresolved_deps($id)) as $udeps |
      (if ($udeps | length) > 0 then "[!]" else $icon end) as $final_icon |
      "\($prefix)\($connector)\($final_icon) \($id): \($node.title // "(untitled)") [\($node.status // "Unknown")]" +
      if ($udeps | length) > 0 then
        if ($udeps | length) <= 3 then
          "  <- blocked by: \($udeps | join(", "))"
        else
          "\n\($prefix)\(if $connector == "└── " then "    " else "│   " end)    <- blocked by: \($udeps | join(", "))"
        end
      else "" end;

    # Cross-cutting artifacts (ADR, PERSONA, RUNBOOK, BUG, SPIKE without parent)
    def is_cross_cutting: .type | test("ADR|PERSONA|RUNBOOK|BUG|SPIKE");

    # ── Hierarchy Tree ──
    "── Hierarchy ──",
    "",

    # Render tree for each Vision
    ($visions | to_entries[] |
      .value as $v |
      ($v.value.status | status_icon) as $vicon |
      "\($vicon) \($v.key): \($v.value.title // "(untitled)") [\($v.value.status // "Unknown")]",

      # Children of this Vision (Epics, Journeys)
      (children_of($v.key) | to_entries[] |
        (if .key == (length - 1) then "└── " else "├── " end) as $conn |
        (if .key == (length - 1) then "    " else "│   " end) as $next_prefix |
        .value as $child |
        node_line($child.id; $child.node; ""; $conn),

        # Children of this child (Specs, Stories under Epics)
        (children_of($child.id) | to_entries[] |
          (if .key == (length - 1) then "└── " else "├── " end) as $conn2 |
          .value as $grandchild |
          node_line($grandchild.id; $grandchild.node; $next_prefix; $conn2)
        )
      ),
      ""
    ),

    # Cross-cutting artifacts section
    (($orphans | map(select(.value | is_cross_cutting))) as $cc |
    if ($cc | length) > 0 then
      "── Cross-cutting ──",
      # Group cross-cutting by type for readability
      ($cc | group_by(.value.type) | .[] |
        "  \(.[0].value.type):",
        (. | sort_by(.key) | to_entries[] |
          (if .key == (length - 1) then "  └── " else "  ├── " end) as $conn |
          .value as $o |
          (unresolved_deps($o.key)) as $udeps |
          ($o.value.status | status_icon) as $icon |
          (if ($udeps | length) > 0 then "[!]" else $icon end) as $final_icon |
          "\($conn)\($final_icon) \($o.key): \($o.value.title // "(untitled)") [\($o.value.status // "Unknown")]" +
          if ($udeps | length) > 0 then "  <- blocked by: \($udeps | join(", "))" else "" end
        )
      ),
      ""
    else empty end),

    # Truly orphaned (non-cross-cutting without parents)
    (($orphans | map(select(.value | is_cross_cutting | not))) as $unp |
    if ($unp | length) > 0 then
      "── Unparented ──",
      ($unp | to_entries[] |
        (if .key == (length - 1) then "└── " else "├── " end) as $conn |
        .value as $o |
        node_line($o.key; $o.value; ""; $conn)
      ),
      ""
    else empty end),

    # ── Executive Summary ──
    # Compute ready and blocked lists
    (
      # All unresolved artifacts
      [$nodes | to_entries[] | select(.value.status | is_resolved | not)] as $unresolved |

      # Ready: unresolved with no unresolved deps
      ([$unresolved[] |
        .key as $id |
        (all_deps($id)) as $deps |
        select(
          ($deps | length == 0) or
          ($deps | all(. as $dep | $nodes[$dep] == null or ($nodes[$dep].status | is_resolved)))
        ) |
        {id: .key, status: .value.status, title: (.value.title // "(untitled)")}
      ] | sort_by(.id)) as $ready |

      # Blocked: unresolved with at least one unresolved dep
      ([$unresolved[] |
        .key as $id |
        (all_deps($id)) as $deps |
        ($deps | map(select(. as $dep | $nodes[$dep] != null and ($nodes[$dep].status | is_resolved | not)))) as $waiting |
        select(($waiting | length) > 0) |
        {id: .key, status: .value.status, title: (.value.title // "(untitled)"), waiting: $waiting}
      ] | sort_by(.id)) as $blocked |

      # Resolved count
      ([$nodes | to_entries[] | select(.value.status | is_resolved)] | length) as $resolved_count |
      ([$nodes | to_entries[]] | length) as $total_count |

      "── Summary ──",
      "  Ready (unblocked, actionable):",
      if ($ready | length) > 0 then
        ($ready[] | "    \(.id): \(.title) [\(.status)]")
      else
        "    (none)"
      end,
      "  Blocked:",
      if ($blocked | length) > 0 then
        ($blocked[] | "    \(.id): \(.title) [\(.status)]  <- waiting on: \(.waiting | join(", "))")
      else
        "    (none)"
      end,
      "  Counts: \($total_count) total -- \($resolved_count) resolved, \($ready | length) ready, \($blocked | length) blocked"
    )
  ' "$CACHE_FILE"

  # Execution tracking integration
  echo ""
  echo "── Execution Tracking ──"
  if command -v bd >/dev/null 2>&1; then
    local bd_status
    bd_status=$(bd status 2>/dev/null) || true
    if [ -n "$bd_status" ]; then
      echo "$bd_status" | sed 's/^/  /'
    else
      echo "  (no active plans)"
    fi
  else
    echo "  (bd not installed — use execution-tracking skill to bootstrap)"
  fi
}

# --- Main ---
[ $# -lt 1 ] && usage

case "$1" in
  build)
    do_build
    ;;
  blocks)
    [ $# -lt 2 ] && { echo "Usage: specgraph.sh blocks <ID>"; exit 1; }
    do_blocks "$2"
    ;;
  blocked-by)
    [ $# -lt 2 ] && { echo "Usage: specgraph.sh blocked-by <ID>"; exit 1; }
    do_blocked_by "$2"
    ;;
  tree)
    [ $# -lt 2 ] && { echo "Usage: specgraph.sh tree <ID>"; exit 1; }
    do_tree "$2"
    ;;
  ready)
    do_ready
    ;;
  next)
    do_next
    ;;
  mermaid)
    do_mermaid
    ;;
  status)
    do_status
    ;;
  overview)
    do_overview
    ;;
  *)
    echo "Unknown command: $1"
    usage
    ;;
esac
