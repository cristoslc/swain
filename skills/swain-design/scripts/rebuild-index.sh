#!/usr/bin/env bash
# rebuild-index.sh — Regenerate list-<type>.md from artifact frontmatter
# Usage: rebuild-index.sh <type> [<type> ...]
#   type: spec | epic | spike | adr | persona | runbook | design | vision | journey
# Reads all artifacts in docs/<type>/ across all phase subdirectories.
# Writes list-<type>.md atomically (temp file → rename).

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

rebuild_index() {
    local type="$1"
    local docs_dir="$REPO_ROOT/docs/$type"
    local index_file="$docs_dir/list-${type}.md"

    if [[ ! -d "$docs_dir" ]]; then
        echo "rebuild-index: docs/$type/ not found, skipping" >&2
        return 0
    fi

    # Collect all artifact .md files (not the index itself)
    local tmpfile title
    tmpfile="$(mktemp)"

    # Write header (portable title mapping, no bash 4+ extensions)
    case "$type" in
        spec)     title="Agent Specs" ;;
        epic)     title="Epics" ;;
        spike)    title="Research Spikes" ;;
        adr)      title="Architecture Decision Records" ;;
        persona)  title="Personas" ;;
        runbook)  title="Runbooks" ;;
        design)   title="Designs" ;;
        vision)   title="Visions" ;;
        journey)  title="Journeys" ;;
        *)        title="$(echo "$type" | sed 's/./\u&/')" ;;
    esac
    printf "# %s\n\n" "$title" > "$tmpfile"

    # Find all phases in order
    local phase phase_dir artifact file_date file_commit
    local -a phases=("Proposed" "Ready" "Active" "Complete" "Superseded" "Abandoned" "Retired" "Deprecated")

    for phase in "${phases[@]}"; do
        phase_dir="$docs_dir/$phase"
        [[ -d "$phase_dir" ]] || continue

        # Build artifact list for this phase
        local -a artifacts=()
        while IFS= read -r f; do
            [[ "$(basename "$f")" == "list-"* ]] && continue
            artifacts+=("$f")
        done < <(find "$phase_dir" -name "*.md" -type f | sort)

        [[ ${#artifacts[@]} -eq 0 ]] && continue

        printf "## %s\n\n" "$phase" >> "$tmpfile"
        printf "| Artifact | Title | Last Updated | Commit |\n" >> "$tmpfile"
        printf "|----------|-------|-------------|--------|\n" >> "$tmpfile"

        for f in "${artifacts[@]}"; do
            artifact="$(grep "^artifact:" "$f" 2>/dev/null | awk '{print $2}' | head -1)"
            title="$(grep "^title:" "$f" 2>/dev/null | sed "s/^title: *//;s/^\"//;s/\"$//" | head -1)"
            file_date="$(grep "^last-updated:" "$f" 2>/dev/null | awk '{print $2}' | head -1)"
            file_commit="$(grep "^| $phase " "$f" 2>/dev/null | tail -1 | awk -F'|' '{print $4}' | tr -d ' ' || true)"
            [[ -z "$file_commit" ]] && file_commit="—"
            [[ -z "$artifact" || -z "$title" ]] && continue
            printf "| %s | %s | %s | %s |\n" "$artifact" "$title" "${file_date:-—}" "$file_commit" >> "$tmpfile"
        done

        printf "\n" >> "$tmpfile"
    done

    # Atomic replace
    mv "$tmpfile" "$index_file"
    echo "rebuild-index: wrote $index_file"
}

if [[ $# -eq 0 ]]; then
    echo "Usage: rebuild-index.sh <type> [<type> ...]" >&2
    exit 1
fi

for type in "$@"; do
    rebuild_index "$type"
done
