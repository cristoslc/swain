#!/usr/bin/env bash
# detect-worktree-links.sh — find worktree-specific relative path links
# Usage: detect-worktree-links.sh [--repo-root PATH] [--worktree-root PATH] <files|dir...>
#
# Output: file:line: target [REASON]  (one line per finding, stdout)
# Exit 0: no suspicious links found
# Exit 1: one or more suspicious links found
# Exit 2: usage error
#
# REASON codes:
#   ESCAPES_REPO           — markdown relative link resolves outside repo root
#   HARDCODED_WORKTREE_PATH — absolute path matching a known worktree pattern
#   SYMLINK_ESCAPE         — symlink target resolves outside repo root
#   SYMLINK_LOOP           — symlink loop detected (warning, non-fatal)

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
REPO_ROOT=""
WORKTREE_ROOT=""
FINDINGS=0
FILES=()

# ── Arg parsing ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo-root)
            REPO_ROOT="${2:?--repo-root requires a path}"
            shift 2
            ;;
        --worktree-root)
            WORKTREE_ROOT="${2:?--worktree-root requires a path}"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        --)
            shift
            FILES+=("$@")
            break
            ;;
        -*)
            echo "detect-worktree-links: unknown option: $1" >&2
            usage
            ;;
        *)
            FILES+=("$1")
            shift
            ;;
    esac
done

usage() {
    cat >&2 <<'EOF'
Usage: detect-worktree-links.sh [--repo-root PATH] [--worktree-root PATH] <files|dir...>

Find worktree-specific relative path links in committed files.

Options:
  --repo-root PATH      Repository root (default: git rev-parse --show-toplevel)
  --worktree-root PATH  Worktree root (default: same as --repo-root)

Output: file:line: link-target [REASON]
Exit 0: no suspicious links
Exit 1: suspicious links found
Exit 2: usage error
EOF
    exit 2
}

if [[ ${#FILES[@]} -eq 0 ]]; then
    usage
fi

# ── Resolve roots ─────────────────────────────────────────────────────────────
if [[ -z "$REPO_ROOT" ]]; then
    REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
        echo "detect-worktree-links: not a git repository" >&2
        exit 2
    }
fi
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"  # normalize

if [[ -z "$WORKTREE_ROOT" ]]; then
    WORKTREE_ROOT="$REPO_ROOT"
fi
WORKTREE_ROOT="$(cd "$WORKTREE_ROOT" && pwd)"

# ── Helpers ───────────────────────────────────────────────────────────────────
emit() {
    local file="$1" line="$2" target="$3" reason="$4"
    echo "${file}:${line}: ${target} [${reason}]"
    FINDINGS=$((FINDINGS + 1))
}

# Pure-bash path normalizer — resolves . and .. without requiring paths to exist.
# Works on macOS where realpath -m fails when the path goes above /.
# Returns the normalized absolute path on stdout.
normalize_path() {
    local base="$1" rel="$2"
    local parts=()
    local IFS=/

    # Start from base (must be absolute)
    read -ra parts <<< "$base"

    # Walk each component of rel
    local comp
    for comp in $rel; do
        case "$comp" in
            ''|'.') ;;           # skip empty and .
            '..') [ ${#parts[@]} -gt 0 ] && unset 'parts[${#parts[@]}-1]' ;;
            *) parts+=("$comp") ;;
        esac
    done

    # Rebuild
    local result="/"
    local p
    for p in "${parts[@]}"; do
        [[ -z "$p" ]] && continue
        result="${result%/}/$p"
    done
    echo "$result"
}

# Resolve a relative link from a given directory; check if it escapes REPO_ROOT
check_relative_link() {
    local file="$1" lineno="$2" target="$3" from_dir="$4"

    # Skip anchors and URLs
    case "$target" in
        http://*|https://*|ftp://*|mailto:*|"#"*) return ;;
    esac

    local resolved
    resolved="$(normalize_path "$from_dir" "$target")"

    # Does the resolved path start with REPO_ROOT?
    case "$resolved" in
        "$REPO_ROOT"/*|"$REPO_ROOT") ;;  # within repo — fine
        *)
            emit "$file" "$lineno" "$target" "ESCAPES_REPO"
            ;;
    esac
}

# ── Scanners ─────────────────────────────────────────────────────────────────

scan_markdown() {
    local file="$1"
    local lineno=0

    while IFS= read -r rawline; do
        lineno=$((lineno + 1))
        # Extract markdown link targets: [text](target)
        # Use grep to find all link targets on this line
        local targets
        targets=$(echo "$rawline" | grep -oE '\]\([^)]+\)' | sed 's/^\](//;s/)$//' || true)
        while IFS= read -r target; do
            [[ -z "$target" ]] && continue
            # Skip URLs and anchors
            case "$target" in
                http://*|https://*|ftp://*|mailto:*|"#"*) continue ;;
            esac
            # Strip title: [link](path "title") → path
            target="${target%% *}"
            # Strip fragment: path#anchor → path
            target="${target%%#*}"
            [[ -z "$target" ]] && continue

            local from_dir
            from_dir="$(dirname "$(realpath -m "$file" 2>/dev/null || echo "$file")")"
            check_relative_link "$file" "$lineno" "$target" "$from_dir"
        done <<< "$targets"
    done < "$file"
}

scan_script() {
    local file="$1"
    local lineno=0

    # Patterns that indicate a hardcoded worktree path
    local patterns=(
        '/tmp/worktree[-_]'
        '\.claude/worktrees/'
        '\.git/worktrees/'
    )
    # Also flag if the repo root absolute path is baked in
    local repo_root_pattern
    repo_root_pattern=$(printf '%s' "$REPO_ROOT" | sed 's|[/.]|\\&|g')

    while IFS= read -r rawline; do
        lineno=$((lineno + 1))
        for pat in "${patterns[@]}"; do
            if echo "$rawline" | grep -qE "$pat"; then
                local matched
                matched=$(echo "$rawline" | grep -oE "['\"]?[^'\" ]*(${pat})[^'\" ]*['\"]?" | head -1 || echo "(pattern: $pat)")
                emit "$file" "$lineno" "$matched" "HARDCODED_WORKTREE_PATH"
                break
            fi
        done
        # Check for baked-in absolute repo root
        if echo "$rawline" | grep -qF "$REPO_ROOT"; then
            # Exclude the script itself referencing its own root via git command
            if ! echo "$rawline" | grep -qE 'git rev-parse|REPO_ROOT=|repo.root'; then
                emit "$file" "$lineno" "$REPO_ROOT" "HARDCODED_WORKTREE_PATH"
            fi
        fi
    done < "$file"
}

scan_symlink() {
    local file="$1"
    local target
    target=$(readlink "$file" 2>/dev/null) || return

    case "$target" in
        # Absolute symlink
        /*)
            case "$target" in
                "$REPO_ROOT"*) ;;  # within repo — fine
                *)
                    emit "$file" "0" "$target" "SYMLINK_ESCAPE"
                    ;;
            esac
            ;;
        # Relative symlink — resolve from symlink's directory
        *)
            local link_dir
            link_dir="$(dirname "$(realpath -m "$file" 2>/dev/null || echo "$file")")"
            local resolved
            # Detect symlink loops
            if ! resolved="$(cd "$link_dir" 2>/dev/null && realpath "$target" 2>/dev/null)"; then
                emit "$file" "0" "$target" "SYMLINK_LOOP"
                return
            fi
            case "$resolved" in
                "$REPO_ROOT"*) ;;  # within repo — fine
                *)
                    emit "$file" "0" "$target" "SYMLINK_ESCAPE"
                    ;;
            esac
            ;;
    esac
}

# ── File walker ───────────────────────────────────────────────────────────────
process_file() {
    local file="$1"
    # Check symlink before -e (broken symlinks fail -e but are valid scan targets)
    if [[ -L "$file" ]]; then
        scan_symlink "$file"
        return
    fi

    [[ -e "$file" ]] || { echo "detect-worktree-links: warning: $file not found" >&2; return; }
    [[ -f "$file" ]] || return

    case "$file" in
        *.md)   scan_markdown "$file" ;;
        *.sh)   scan_script "$file" ;;
    esac
}

process_path() {
    local path="$1"
    if [[ -d "$path" ]] && [[ ! -L "$path" ]]; then
        while IFS= read -r -d '' f; do
            process_file "$f"
        done < <(find "$path" \( -name "*.md" -o -name "*.sh" -o -type l \) -print0 2>/dev/null)
    else
        process_file "$path"
    fi
}

# ── Main ─────────────────────────────────────────────────────────────────────
for arg in "${FILES[@]}"; do
    process_path "$arg"
done

if [[ "$FINDINGS" -gt 0 ]]; then
    exit 1
fi
exit 0
