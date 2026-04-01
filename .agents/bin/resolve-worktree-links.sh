#!/usr/bin/env bash
# resolve-worktree-links.sh — rewrite worktree-specific path links in-place
# Usage:
#   resolve-worktree-links.sh [--repo-root PATH] [--worktree-root PATH] <files|dir...>
#   detect-worktree-links.sh ... | resolve-worktree-links.sh --repo-root PATH --from-stdin
#
# Output: file:line: FIXED old -> new  OR  file:line: UNRESOLVABLE old
# Exit 0: all links resolved (or no issues)
# Exit 1: one or more UNRESOLVABLE links remain
# Exit 2: usage error

set -euo pipefail

REPO_ROOT=""
WORKTREE_ROOT=""
FROM_STDIN=false
FILES=()
UNRESOLVABLE=0

DETECT_SCRIPT="$(dirname "$0")/detect-worktree-links.sh"

usage() {
    cat >&2 <<'EOF'
Usage:
  resolve-worktree-links.sh [--repo-root PATH] [--worktree-root PATH] <files|dir...>
  detect-worktree-links.sh ... | resolve-worktree-links.sh --repo-root PATH --from-stdin

Rewrite worktree-specific path links in-place.

Exit 0: all resolved (or no issues)
Exit 1: UNRESOLVABLE links remain
Exit 2: usage error
EOF
    exit 2
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo-root)    REPO_ROOT="${2:?}"; shift 2 ;;
        --worktree-root) WORKTREE_ROOT="${2:?}"; shift 2 ;;
        --from-stdin)   FROM_STDIN=true; shift ;;
        -h|--help)      usage ;;
        -*)             echo "resolve-worktree-links: unknown option: $1" >&2; usage ;;
        *)              FILES+=("$1"); shift ;;
    esac
done

if [[ "$FROM_STDIN" == false && ${#FILES[@]} -eq 0 ]]; then
    usage
fi

# Resolve roots
if [[ -z "$REPO_ROOT" ]]; then
    REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
        echo "resolve-worktree-links: not a git repository" >&2; exit 2
    }
fi
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
[[ -z "$WORKTREE_ROOT" ]] && WORKTREE_ROOT="$REPO_ROOT"

# ── Path helpers (same normalize_path as detector) ────────────────────────────
normalize_path() {
    local base="$1" rel="$2"
    local parts=() IFS=/
    read -ra parts <<< "$base"
    local comp
    for comp in $rel; do
        case "$comp" in
            ''|'.') ;;
            '..') [ ${#parts[@]} -gt 0 ] && unset 'parts[${#parts[@]}-1]' ;;
            *) parts+=("$comp") ;;
        esac
    done
    local result="/" p
    for p in "${parts[@]}"; do [[ -z "$p" ]] && continue; result="${result%/}/$p"; done
    echo "$result"
}

# Compute the relative path from $from_dir to $target_abs (both must be under REPO_ROOT)
relative_path() {
    local from="$1" to="$2"
    # Strip leading /
    local from_parts to_parts common_len rel
    IFS='/' read -ra from_parts <<< "${from#/}"
    IFS='/' read -ra to_parts   <<< "${to#/}"

    # Find common prefix length
    common_len=0
    local i
    for ((i=0; i<${#from_parts[@]} && i<${#to_parts[@]}; i++)); do
        [[ "${from_parts[$i]}" == "${to_parts[$i]}" ]] && common_len=$((i+1)) || break
    done

    # Build rel: go up from from to common, then down to to
    rel=""
    local up=$(( ${#from_parts[@]} - common_len ))
    for ((i=0; i<up; i++)); do rel="${rel}../"; done
    for ((i=common_len; i<${#to_parts[@]}; i++)); do rel="${rel}${to_parts[$i]}/"; done
    rel="${rel%/}"
    [[ -z "$rel" ]] && rel="."
    echo "$rel"
}

# ── Resolvers ─────────────────────────────────────────────────────────────────

# Fix a markdown link in a file at a given line
fix_markdown_link() {
    local file="$1" lineno="$2" old_target="$3"
    local from_dir
    from_dir="$(dirname "$(cd "$(dirname "$file")" && pwd)/$(basename "$file")")"

    local resolved
    resolved="$(normalize_path "$from_dir" "$old_target")"

    # The resolved path is outside REPO_ROOT — try to find the filename under REPO_ROOT
    local basename_target
    basename_target="$(basename "$old_target")"
    local found
    found="$(find "$REPO_ROOT" -name "$basename_target" -not -path "*/.git/*" 2>/dev/null | head -1)"

    if [[ -z "$found" ]]; then
        echo "${file}:${lineno}: UNRESOLVABLE ${old_target}"
        UNRESOLVABLE=$((UNRESOLVABLE + 1))
        return
    fi

    # Compute new relative path from file's dir to found target
    local new_rel
    new_rel="$(relative_path "$from_dir" "$found")"

    # Rewrite the line in-place (escape for sed)
    local old_esc new_esc
    old_esc="$(printf '%s' "$old_target" | sed 's|[[\.*^$()+?{}|/]|\\&|g')"
    new_esc="$(printf '%s' "$new_rel" | sed 's|[&/]|\\&|g')"

    # Use python for reliable in-place edit (sed -i differs between macOS/Linux)
    python3 - "$file" "$lineno" "$old_target" "$new_rel" <<'PYEOF'
import sys
path, lineno, old, new = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
with open(path) as f:
    lines = f.readlines()
lines[lineno-1] = lines[lineno-1].replace(f']({old})', f']({new})', 1)
with open(path, 'w') as f:
    f.writelines(lines)
PYEOF

    echo "${file}:${lineno}: FIXED ${old_target} -> ${new_rel}"
}

# ── Parse findings and dispatch ───────────────────────────────────────────────
process_finding() {
    local finding="$1"
    # Format: file:line: target [REASON]
    local file lineno target reason
    # Parse: everything before first colon is file, then line, then rest
    file="${finding%%:*}"
    local rest="${finding#*:}"
    lineno="${rest%%:*}"
    rest="${rest#*: }"
    reason="${rest##*[}"
    reason="${reason%]}"
    target="${rest% \[*}"

    case "$reason" in
        ESCAPES_REPO)
            fix_markdown_link "$file" "$lineno" "$target"
            ;;
        SYMLINK_ESCAPE)
            # For symlinks, try to recreate pointing within repo
            local link_target
            link_target="$(readlink "$file" 2>/dev/null || echo "")"
            local basename_t
            basename_t="$(basename "$link_target")"
            local found
            found="$(find "$REPO_ROOT" -name "$basename_t" -not -path "*/.git/*" 2>/dev/null | head -1)"
            if [[ -z "$found" ]]; then
                echo "${file}:${lineno}: UNRESOLVABLE ${target}"
                UNRESOLVABLE=$((UNRESOLVABLE + 1))
                return
            fi
            local link_dir
            link_dir="$(dirname "$(cd "$(dirname "$file")" && pwd)/$(basename "$file")")"
            local new_rel
            new_rel="$(relative_path "$link_dir" "$found")"
            ln -sf "$new_rel" "$file"
            echo "${file}:${lineno}: FIXED ${target} -> ${new_rel}"
            ;;
        HARDCODED_WORKTREE_PATH)
            # Can't safely auto-rewrite script paths — mark UNRESOLVABLE
            echo "${file}:${lineno}: UNRESOLVABLE ${target}"
            UNRESOLVABLE=$((UNRESOLVABLE + 1))
            ;;
        SYMLINK_LOOP)
            echo "${file}:${lineno}: UNRESOLVABLE ${target} (symlink loop)"
            UNRESOLVABLE=$((UNRESOLVABLE + 1))
            ;;
    esac
}

# ── Main ──────────────────────────────────────────────────────────────────────
if [[ "$FROM_STDIN" == true ]]; then
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        process_finding "$line"
    done
else
    # Run detector on the file set, then process each finding
    set +e
    FINDINGS=$("$DETECT_SCRIPT" --repo-root "$REPO_ROOT" --worktree-root "$WORKTREE_ROOT" "${FILES[@]}" 2>/dev/null)
    DETECT_EXIT=$?
    set -e

    if [[ $DETECT_EXIT -eq 0 ]]; then
        exit 0  # nothing to do
    fi

    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        process_finding "$line"
    done <<< "$FINDINGS"

    # Verify idempotency: re-run detector; if still findings remain that we touched, they're UNRESOLVABLE
    set +e
    "$DETECT_SCRIPT" --repo-root "$REPO_ROOT" "${FILES[@]}" >/dev/null 2>&1
    RECHECK=$?
    set -e
    if [[ $RECHECK -ne 0 && $UNRESOLVABLE -eq 0 ]]; then
        # Detector still finds something we thought we fixed
        UNRESOLVABLE=1
    fi
fi

[[ $UNRESOLVABLE -gt 0 ]] && exit 1 || exit 0
