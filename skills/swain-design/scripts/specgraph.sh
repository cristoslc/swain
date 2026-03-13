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
Usage: specgraph.sh <command> [args] [--all] [--all-edges]

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
  neighbors <ID>     All directly connected artifacts (any edge type, both directions)
  scope <ID>         Alignment scope — parent chain to Vision, siblings, lateral links
  impact <ID>        What depends on this artifact transitively (inverse of scope)
  edges [<ID>]       Raw edge list with types, optionally filtered to one artifact

Options:
  --all              Include finished artifacts (resolved/terminal states).
                     By default, overview/status/mermaid hide them.
  --all-edges        Show all edge types in mermaid output (not just depends-on/parent).
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

# Extract a one-line description for an artifact.
# Priority: question (spikes) > description (frontmatter) > first body paragraph
get_description() {
  local file="$1"
  local desc
  # Try question field first (SPIKEs use this)
  desc=$(get_field "$file" "question")
  [ -n "$desc" ] && { printf '%s' "${desc:0:120}"; return; }
  # Try description field
  desc=$(get_field "$file" "description")
  [ -n "$desc" ] && { printf '%s' "${desc:0:120}"; return; }
  # Fall back to first non-heading, non-empty body line after frontmatter
  desc=$(awk '/^---$/{n++; next} n>=2 && /^[^#\[\|>!-]/ && NF>0 {print; exit}' "$file") || true
  printf '%s' "${desc:0:120}"
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

# Extract a YAML list field as newline-separated full values (preserving suffixes like .PP-NN)
# Always succeeds (returns empty if field not found or has no list items)
get_list_field_full() {
  local file="$1" field="$2"
  sed -n '/^---$/,/^---$/p' "$file" | \
    sed -n "/^${field}:/,/^[^[:space:]-]/p" | \
    grep '^[[:space:]]*-' | \
    sed 's/^[[:space:]]*-[[:space:]]*//' | \
    sed 's/^"\(.*\)"$/\1/' | \
    sed "s/^'\(.*\)'$/\1/" | \
    sed '/^[[:space:]]*$/d' || true
}

# Check if a value is a valid reference (not a YAML null/empty placeholder)
is_valid_ref() {
  local val="$1"
  case "$val" in
    ""|\~|null|"[]"|"--"|"\"\""|"''") return 1 ;;
    *) return 0 ;;
  esac
}

# Build the graph JSON from frontmatter
do_build() {
  local nodes_json=""
  local edges_json=""
  local first_node=1
  local first_edge=1

  add_edge() {
    local from="$1" to="$2" etype="$3"
    is_valid_ref "$to" || return 0
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

    # Extract a one-line description for human context
    local desc
    desc=$(get_description "$file")

    # Build node JSON
    local node_json
    node_json=$(jq -n \
      --arg title "$title" \
      --arg status "$status" \
      --arg type "$atype" \
      --arg file "$file_rel" \
      --arg desc "$desc" \
      '{title: $title, status: $status, type: $type, file: $file, description: $desc}')

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

    # parent-vision edges (scalar or list format)
    local pv
    pv=$(get_field "$file" "parent-vision")
    if [ -z "$pv" ]; then
      pv=$(get_list_field "$file" "parent-vision" | head -1)
    fi
    if [ -n "$pv" ]; then
      add_edge "$artifact" "$pv" "parent-vision"
    fi

    # parent-epic edges (scalar or list format)
    local pe
    pe=$(get_field "$file" "parent-epic")
    if [ -z "$pe" ]; then
      pe=$(get_list_field "$file" "parent-epic" | head -1)
    fi
    if [ -n "$pe" ]; then
      add_edge "$artifact" "$pe" "parent-epic"
    fi

    # List-type relationship edges
    local list_field
    for list_field in linked-adrs linked-specs linked-epics linked-research \
                      linked-personas linked-journeys linked-stories linked-designs \
                      validates; do
      while IFS= read -r ref; do
        [ -z "$ref" ] && continue
        add_edge "$artifact" "$ref" "$list_field"
      done <<< "$(get_list_field "$file" "$list_field")"
    done

    # addresses edges (preserves JOURNEY-NNN.PP-NN format)
    while IFS= read -r ref; do
      [ -z "$ref" ] && continue
      add_edge "$artifact" "$ref" "addresses"
    done <<< "$(get_list_field_full "$file" "addresses")"

    # Scalar relationship edges
    local scalar_field scalar_val
    for scalar_field in superseded-by evidence-pool source-issue; do
      scalar_val=$(get_field "$file" "$scalar_field")
      if [ -n "$scalar_val" ]; then
        add_edge "$artifact" "$scalar_val" "$scalar_field"
      fi
    done

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
    .repo as $repo |
    .nodes as $nodes |
    .edges as $edges |
    def art_link($aid; $file):
      if $file != null and $file != "" then
        "\u001b]8;;file://\($repo)/\($file)\u001b\\\($aid)\u001b]8;;\u001b\\"
      else $aid end;
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
      "  \(art_link(.key; .value.file))  (\(.value.status))  \(.value.title)"
    ] | .[]
  ' "$CACHE_FILE"
}

# next — what to work on next (ready items + what they'd unblock + blocked items)
do_next() {
  ensure_cache
  # Ready items with what completing them would unblock
  local ready_output
  ready_output=$(jq -r '
    .repo as $repo |
    .nodes as $nodes |
    .edges as $edges |
    def is_resolved: test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined");
    def art_link($aid; $file):
      if $file != null and $file != "" then
        "\u001b]8;;file://\($repo)/\($file)\u001b\\\($aid)\u001b]8;;\u001b\\"
      else $aid end;

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
      {id: $id, status: .value.status, title: .value.title, file: .value.file, unblocks: $would_unblock}
    ] |
    sort_by(.id) |
    if length == 0 then "  (none)\n"
    else .[] |
      "  \(art_link(.id; .file))  (\(.status))  \(.title)" +
      if (.unblocks | length) > 0 then "\n    unblocks: \(.unblocks | map(art_link(.; ($nodes[.].file // ""))) | join(", "))"
      else "" end
    end
  ' "$CACHE_FILE") || true

  # Blocked items
  local blocked_output
  blocked_output=$(jq -r '
    .repo as $repo |
    .nodes as $nodes |
    .edges as $edges |
    def is_resolved: test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined");
    def art_link($aid; $file):
      if $file != null and $file != "" then
        "\u001b]8;;file://\($repo)/\($file)\u001b\\\($aid)\u001b]8;;\u001b\\"
      else $aid end;

    [.nodes | to_entries[] |
      select(.value.status | is_resolved | not) |
      .key as $id |
      ([$edges[] | select(.from == $id and .type == "depends-on") | .to] | unique) as $deps |
      ($deps | map(select(. as $dep | $nodes[$dep] == null or ($nodes[$dep].status | is_resolved | not)))) as $unresolved |
      select(($unresolved | length) > 0) |
      {id: $id, status: .value.status, title: .value.title, file: .value.file, waiting: $unresolved}
    ] |
    sort_by(.id) |
    if length == 0 then "  (none)\n"
    else .[] |
      "  \(art_link(.id; .file))  (\(.status))  \(.title)\n    waiting on: \(.waiting | map(art_link(.; ($nodes[.].file // ""))) | join(", "))"
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
  # Node labels (filtered by visibility)
  jq -r --argjson show_all "$SHOW_ALL" '
    def is_resolved: test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined");
    (.nodes | to_entries | map(select($show_all == 1 or (.value.status | is_resolved | not))) | map(.key)) as $visible |
    .nodes | to_entries[] |
    select(.key | IN($visible[])) |
    "    \(.key)[\"\(.key): \(.value.title | gsub("\""; "#quot;"))\"]"
  ' "$CACHE_FILE"
  # Edges (only between visible nodes)
  jq -r --argjson show_all "$SHOW_ALL" --argjson show_all_edges "$SHOW_ALL_EDGES" '
    def is_resolved: test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined");
    (.nodes | to_entries | map(select($show_all == 1 or (.value.status | is_resolved | not))) | map(.key)) as $visible |
    .nodes as $nodes |
    .edges[] |
    select(.from | IN($visible[])) |
    select(if $show_all_edges == 1 then (.to | IN($visible[])) or ($nodes[.to] == null) else (.to | IN($visible[])) end) |
    if .type == "depends-on" then
      "    \(.from) -->|depends-on| \(.to)"
    elif .type == "parent-vision" then
      "    \(.from) -.->|child-of| \(.to)"
    elif .type == "parent-epic" then
      "    \(.from) -.->|child-of| \(.to)"
    elif $show_all_edges == 1 and ($nodes[.to] != null) then
      "    \(.from) -.-|\(.type)| \(.to)"
    else empty end
  ' "$CACHE_FILE"
  # Style resolved nodes (only when --all is used)
  if [ "$SHOW_ALL" -eq 1 ]; then
    jq -r '
      .nodes | to_entries[] |
      select(.value.status | test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined")) |
      "    style \(.key) fill:#90EE90"
    ' "$CACHE_FILE"
  fi
}

# status — summary table
do_status() {
  ensure_cache
  echo "=== Artifact Status Summary ==="
  echo ""
  # Group by type, then by status within type
  jq -r --argjson show_all "$SHOW_ALL" '
    .repo as $repo |
    def is_resolved: test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined");
    def art_link($aid; $file):
      if $file != null and $file != "" then
        "\u001b]8;;file://\($repo)/\($file)\u001b\\\($aid)\u001b]8;;\u001b\\"
      else $aid end;
    [.nodes | to_entries[] |
      select($show_all == 1 or (.value.status | is_resolved | not)) |
      {type: .value.type, status: .value.status, id: .key, title: .value.title, file: .value.file}] |
    if length == 0 then "  (no active artifacts)\n"
    else
      group_by(.type) | .[] |
      ("## " + .[0].type),
      (. | sort_by(.id) | .[] | "  \(art_link(.id; .file))  [\(.status)]  \(.title)"),
      ""
    end
  ' "$CACHE_FILE"
  if [ "$SHOW_ALL" -eq 0 ]; then
    local hidden
    hidden=$(jq '[.nodes | to_entries[] | select(.value.status | test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined"))] | length' "$CACHE_FILE")
    if [ "$hidden" -gt 0 ]; then
      echo "($hidden finished artifact$([ "$hidden" -gt 1 ] && echo "s") hidden — use --all to show)"
    fi
  fi
}

# overview — combined hierarchy tree with status indicators, dependency info, and executive summary
do_overview() {
  ensure_cache

  jq -r --argjson show_all "$SHOW_ALL" '
    def is_resolved: test("Complete|Implemented|Adopted|Validated|Archived|Retired|Superseded|Abandoned|Sunset|Deprecated|Verified|Declined");
    def status_icon: if is_resolved then "[x]" else "[ ]" end;
    # Filter: hide resolved artifacts unless --all is passed
    def visible: if $show_all == 1 then true else (.status | is_resolved | not) end;
    # Note: titles are already cleaned of ID prefixes during cache build

    .nodes as $nodes |
    .edges as $edges |
    .repo as $repo |
    def art_link($aid; $file):
      if $file != null and $file != "" then
        "\u001b]8;;file://\($repo)/\($file)\u001b\\\($aid)\u001b]8;;\u001b\\"
      else $aid end;

    # Find all Vision nodes (top-level)
    ($nodes | to_entries | map(select(.value.type == "VISION" and (.value | visible))) | sort_by(.key)) as $visions |

    # Find orphans (no parent-vision or parent-epic edge)
    ([$nodes | to_entries[] |
      .key as $id |
      select(
        (.value | visible) and
        .value.type != "VISION" and
        ([$edges[] | select(.from == $id and (.type == "parent-vision" or .type == "parent-epic"))] | length == 0)
      )
    ] | sort_by(.key)) as $orphans |

    # Helper: get children of a node by parent edge type (filtered by visibility)
    def children_of($parent_id):
      [$edges[] | select(.to == $parent_id and (.type == "parent-vision" or .type == "parent-epic")) | .from] |
      unique | sort |
      map(. as $id | {id: $id, node: $nodes[$id]}) |
      map(select(.node != null and (.node | visible)));

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
      "\($prefix)\($connector)\($final_icon) \(art_link($id; $node.file)): \($node.title // "(untitled)") [\($node.status // "Unknown")]" +
      if ($udeps | length) > 0 then
        if ($udeps | length) <= 3 then
          "  <- blocked by: \($udeps | map(art_link(.; ($nodes[.].file // ""))) | join(", "))"
        else
          "\n\($prefix)\(if $connector == "└── " then "    " else "│   " end)    <- blocked by: \($udeps | map(art_link(.; ($nodes[.].file // ""))) | join(", "))"
        end
      else "" end;

    # Cross-cutting artifacts (ADR, PERSONA, RUNBOOK, SPIKE without parent)
    def is_cross_cutting: .type | test("ADR|PERSONA|RUNBOOK|SPIKE");

    # ── Hierarchy Tree ──
    "── Hierarchy ──",
    "",

    # Render tree for each Vision
    ($visions | to_entries[] |
      .value as $v |
      ($v.value.status | status_icon) as $vicon |
      "\($vicon) \(art_link($v.key; $v.value.file)): \($v.value.title // "(untitled)") [\($v.value.status // "Unknown")]",

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
          "\($conn)\($final_icon) \(art_link($o.key; $o.value.file)): \($o.value.title // "(untitled)") [\($o.value.status // "Unknown")]" +
          if ($udeps | length) > 0 then "  <- blocked by: \($udeps | map(art_link(.; ($nodes[.].file // ""))) | join(", "))" else "" end
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
        ($ready[] | "    \(art_link(.id; ($nodes[.id].file // ""))): \(.title) [\(.status)]")
      else
        "    (none)"
      end,
      "  Blocked:",
      if ($blocked | length) > 0 then
        ($blocked[] | "    \(art_link(.id; ($nodes[.id].file // ""))): \(.title) [\(.status)]  <- waiting on: \(.waiting | map(art_link(.; ($nodes[.].file // ""))) | join(", "))")
      else
        "    (none)"
      end,
      "  Counts: \($total_count) total -- \($resolved_count) resolved, \($ready | length) ready, \($blocked | length) blocked",
      if $show_all == 0 and $resolved_count > 0 then
        "  (\($resolved_count) finished artifact\(if $resolved_count > 1 then "s" else "" end) hidden — use --all to show)"
      else empty end
    )
  ' "$CACHE_FILE"

  # Execution tracking integration
  echo ""
  echo "── Execution Tracking ──"
  if command -v tk >/dev/null 2>&1; then
    local tk_status
    tk_status=$(tk ready 2>/dev/null) || true
    if [ -n "$tk_status" ]; then
      echo "$tk_status" | sed 's/^/  /'
    else
      echo "  (no active plans)"
    fi
  else
    echo "  (tk not installed — use swain-do skill to bootstrap)"
  fi
}

# edges [<ID>] — raw edge list, optionally filtered to one artifact
do_edges() {
  local id="${1:-}"
  ensure_cache
  if [ -n "$id" ]; then
    jq -r --arg id "$id" '
      .edges[] | select(.from == $id or .to == $id) |
      "\(.from)\t\(.to)\t\(.type)"
    ' "$CACHE_FILE" | sort
  else
    jq -r '.edges[] | "\(.from)\t\(.to)\t\(.type)"' "$CACHE_FILE" | sort
  fi
}

# neighbors <ID> — all directly connected artifacts (any edge type, both directions)
do_neighbors() {
  local id="$1"
  ensure_cache
  jq -r --arg id "$id" '
    .nodes as $nodes |
    [.edges[] |
      if .from == $id then {id: .to, type: .type, direction: "outgoing"}
      elif .to == $id then {id: .from, type: .type, direction: "incoming"}
      else empty end
    ] | sort_by(.direction + .type + .id) |
    .[] | "\(.direction)\t\(.type)\t\(.id)" +
      (if $nodes[.id] != null then "\t[\($nodes[.id].status)]\t\($nodes[.id].title // "")" else "" end)
  ' "$CACHE_FILE"
}

# scope <ID> — alignment scope: walk parent chain to Vision, collect siblings and lateral links
do_scope() {
  local id="$1"
  ensure_cache

  jq -r --arg id "$id" '
    .nodes as $nodes |
    .edges as $edges |

    # Walk parent chain upward (parent-epic then parent-vision)
    def walk_parents($current):
      ([$edges[] | select(.from == $current and (.type == "parent-epic" or .type == "parent-vision")) | .to] | .[0]) as $parent |
      if $parent == null then []
      else [$parent] + walk_parents($parent)
      end;

    # Siblings: artifacts sharing the same immediate parent
    def siblings($art):
      ([$edges[] | select(.from == $art and (.type == "parent-epic" or .type == "parent-vision")) | .to] | .[0]) as $parent |
      if $parent == null then []
      else [$edges[] | select(.to == $parent and (.type == "parent-epic" or .type == "parent-vision") and .from != $art) | .from] | unique
      end;

    # Lateral: non-hierarchical relationship edges from an artifact
    def laterals($art):
      [$edges[] | select(.from == $art and (.type | test("^linked-|^addresses$|^validates$|^superseded-by$|^evidence-pool$"))) | {id: .to, type: .type}];

    # Also find incoming lateral links (artifacts that link TO this one)
    def incoming_laterals($art):
      [$edges[] | select(.to == $art and (.type | test("^linked-|^addresses$|^validates$|^superseded-by$"))) | {id: .from, type: .type}];

    # Build scope
    walk_parents($id) as $chain |
    siblings($id) as $sibs |

    # Laterals from the artifact itself, incoming laterals, and from each chain member
    (laterals($id) + incoming_laterals($id) + [$chain[] | laterals(.) | .[]] | unique_by(.id + .type)) as $lats |

    # Vision is the last element of chain (if any), or $id itself if it is a VISION
    (if ($chain | length) > 0 then $chain[-1]
     elif $nodes[$id] != null and $nodes[$id].type == "VISION" then $id
     else null end) as $vision |

    "CHAIN:",
    (if ($chain | length) > 0 then
      ($chain | to_entries[] |
        "  \(.value)" + (if $nodes[.value] != null then "  [\($nodes[.value].status)]  \($nodes[.value].title // "")" else "  (missing)" end))
    else "  (no parent chain)" end),
    "",
    "SIBLING:",
    (if ($sibs | length) > 0 then
      ($sibs | sort | .[] |
        "  \(.)" + (if $nodes[.] != null then "  [\($nodes[.].status)]  \($nodes[.].title // "")" else "  (missing)" end))
    else "  (none)" end),
    "",
    "LATERAL:",
    (if ($lats | length) > 0 then
      ($lats | sort_by(.type + .id) | .[] |
        "  \(.id)  (\(.type))" + (if $nodes[.id] != null then "  [\($nodes[.id].status)]  \($nodes[.id].title // "")" else "" end))
    else "  (none)" end),
    "",
    "SUPPORTING:",
    (if $vision != null then
      "  vision: \($vision)" + (if $nodes[$vision] != null then "  \($nodes[$vision].title // "")" else "" end),
      (if $nodes[$vision] != null then "  file: \($nodes[$vision].file // "(unknown)")" else empty end)
    else "  (no vision found)" end)
  ' "$CACHE_FILE"

  # Check for architecture-overview.md near the vision
  local vision_file
  vision_file=$(jq -r --arg id "$id" '
    .edges as $edges |
    .nodes as $nodes |
    def walk_parents($current):
      ([$edges[] | select(.from == $current and (.type == "parent-epic" or .type == "parent-vision")) | .to] | .[0]) as $parent |
      if $parent == null then
        (if $nodes[$current] != null and $nodes[$current].type == "VISION" then $current else null end)
      else walk_parents($parent)
      end;
    walk_parents($id) as $vision |
    if $vision != null and $nodes[$vision] != null then $nodes[$vision].file // ""
    else "" end
  ' "$CACHE_FILE")

  if [ -n "$vision_file" ]; then
    local vision_dir
    vision_dir=$(dirname "$REPO_ROOT/$vision_file")
    if [ -f "$vision_dir/architecture-overview.md" ]; then
      echo "  architecture: ${vision_dir#"$REPO_ROOT/"}/architecture-overview.md"
    fi
  fi
}

# impact <ID> — everything that references this artifact transitively
do_impact() {
  local id="$1"
  ensure_cache

  jq -r --arg id "$id" '
    .nodes as $nodes |
    .edges as $edges |

    # Find all edges where .to matches this ID (or starts with ID. for pain-point refs)
    def all_referencing($target):
      [$edges[] | select(.to == $target or (.to | tostring | startswith($target + "."))) | .from] | unique;

    # Walk parent chain upward
    def walk_parents($current):
      ([$edges[] | select(.from == $current and (.type == "parent-epic" or .type == "parent-vision")) | .to] | .[0]) as $parent |
      if $parent == null then []
      else [$parent] + walk_parents($parent)
      end;

    all_referencing($id) as $refs |
    ($refs | map(. as $r | {ref: $r, chain: walk_parents($r)})) as $ref_chains |
    ([$ref_chains[] | .ref, .chain[]] | unique | sort) as $all_affected |

    "DIRECT:",
    (if ($refs | length) > 0 then
      $refs | sort | .[] |
      "  \(.)" + (if $nodes[.] != null then "  [\($nodes[.].status)]  \($nodes[.].title // "")" else "" end)
    else "  (none)" end),
    "",
    "AFFECTED CHAINS:",
    (if ($ref_chains | length) > 0 then
      $ref_chains | sort_by(.ref) | .[] |
      "  \(.ref) → \(if (.chain | length) > 0 then (.chain | join(" → ")) else "(no parent)" end)"
    else "  (none)" end),
    "",
    "TOTAL AFFECTED: \($all_affected | length) artifact(s)"
  ' "$CACHE_FILE"
}

# --- Parse flags ---
SHOW_ALL=0
SHOW_ALL_EDGES=0
for arg in "$@"; do
  case "$arg" in
    --all) SHOW_ALL=1 ;;
    --all-edges) SHOW_ALL_EDGES=1 ;;
  esac
done
# Strip flags from positional args
ARGS=()
for arg in "$@"; do
  case "$arg" in
    --all|--all-edges) ;;
    *) ARGS+=("$arg") ;;
  esac
done
set -- "${ARGS[@]}"

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
  neighbors)
    [ $# -lt 2 ] && { echo "Usage: specgraph.sh neighbors <ID>"; exit 1; }
    do_neighbors "$2"
    ;;
  scope)
    [ $# -lt 2 ] && { echo "Usage: specgraph.sh scope <ID>"; exit 1; }
    do_scope "$2"
    ;;
  impact)
    [ $# -lt 2 ] && { echo "Usage: specgraph.sh impact <ID>"; exit 1; }
    do_impact "$2"
    ;;
  edges)
    do_edges "${2:-}"
    ;;
  *)
    echo "Unknown command: $1"
    usage
    ;;
esac
