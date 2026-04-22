#!/bin/sh
# entrypoint.sh — Shadow parent directories with tmpfs to prevent
# the container from reading or writing sibling directories on the host.
#
# Docker Desktop on macOS exposes the entire host filesystem via
# VirtioFS, so even with read_only: true, the container can read
# sibling directories. This script mounts tmpfs over each ancestor
# directory of PROJECT_PATH, then re-binds the project from the
# read-only /project_source mount so only the project is accessible.
#
# Example: PROJECT_PATH=/Users/cristos/Documents/code/myproject
#   Shadowed: /Users, /Users/cristos, /Users/cristos/Documents, /Users/cryptos/Documents/code
#   Visible: /Users/cristos/Documents/code/myproject (from /project_source)
#   Blocked: /Users/cristos/Documents/code/sibling-project (does not exist)
#
# Requires: --cap-add SYS_ADMIN for mount(8) inside the container.

set -e

PROJECT_PATH="${PROJECT_PATH:-/project}"

# Walk up from PROJECT_PATH to root, collecting all ancestor directories.
ancestors=""
path="$(dirname "$PROJECT_PATH")"
while [ "$path" != "/" ] && [ "$path" != "." ]; do
    ancestors="$path $ancestors"
    path="$(dirname "$path")"
done

# Mount tmpfs over each ancestor directory, shadowing the host's
# real directory with an empty one. Sibling directories disappear.
for dir in $ancestors; do
    if [ -d "$dir" ]; then
        mount -t tmpfs tmpfs "$dir" 2>/dev/null || true
    fi
done

# The project bind mount was hidden by the parent tmpfs. Recreate
# it by bind-mounting from the read-only /project_source that Docker
# set up before the entrypoint ran.
mkdir -p "$PROJECT_PATH"
mount --bind /project_source "$PROJECT_PATH" 2>/dev/null || true

# Verify the project is accessible.
if [ ! -f "$PROJECT_PATH/.git/HEAD" ] && [ ! -d "$PROJECT_PATH/.git" ]; then
    echo "WARNING: $PROJECT_PATH does not appear to be a git repository"
fi

exec "$@"