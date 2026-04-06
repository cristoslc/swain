---
name: swain-update
description: "Update swain skills to the latest version. Use when the user says 'update swain', 'upgrade swain', 'pull latest swain', 'reinstall swain', 'refresh skills', or wants to update their swain skills installation. Uses npx to pull the latest swain release from GitHub, with a git-clone fallback, then invokes swain-doctor to reconcile governance and validate project health."
user-invocable: true
allowed-tools: Bash, Read, Glob
metadata:
  short-description: Update swain skills to latest
  version: 1.4.0
  author: cristos
  license: MIT
  source: swain
---
<!-- swain-model-hint: sonnet, effort: low -->

# Update Swain

Update the local installation of swain skills to the latest version, then reconcile governance configuration.

## Step 1 — Detect current installation

Check whether `.claude/skills/` contains any `swain-*` directories:

```bash
ls -d .claude/skills/swain-* 2>/dev/null
```

If no swain skill directories are found, inform the user this appears to be a fresh install rather than an update, then continue anyway — the steps below work for both cases.

## Step 2 — Backup local modifications

Before overwriting skill directories, check for user modifications that should be preserved.

### Detect modified files

Compare local skill files against the installed version's git origin:

```bash
# Create a temporary reference copy
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/cristoslc/swain.git "$tmp/swain" 2>/dev/null

# Find locally modified files
modified_files=()
for skill_dir in .claude/skills/swain-*/; do
  skill_name=$(basename "$skill_dir")
  ref_dir="$tmp/swain/skills/$skill_name"
  [ -d "$ref_dir" ] || continue

  while IFS= read -r file; do
    rel="${file#$skill_dir}"
    ref_file="$ref_dir/$rel"
    if [ -f "$ref_file" ]; then
      if ! diff -q "$file" "$ref_file" >/dev/null 2>&1; then
        modified_files+=("$file")
      fi
    else
      # File exists locally but not in upstream — user-added file
      modified_files+=("$file")
    fi
  done < <(find "$skill_dir" -type f)
done
```

### Backup modified files

If modified files are found:

1. Create a backup directory: `.agents/update-backup/<ISO-date>/`
2. Copy each modified file preserving directory structure
3. Inform the user: "Found N locally modified files — backed up to `.agents/update-backup/<date>/`"
4. List the modified files

If no modified files are found, skip and continue.

The reference clone from this step can be reused as the fallback source in Step 3.

## Step 3 — Detect installed agent platforms

Before installing, detect which agent platforms are present on the system. This avoids creating dotfolder stubs for every supported platform (see [GitHub issue #21](https://github.com/cristoslc/swain/issues/21)).

Read the agent platform data from `references/agent-platforms.json`. Each entry in the `agents` array has a `name` (skills CLI identifier), an optional `command` (CLI binary), and a `detection` path (HOME config directory). A platform is detected if either check succeeds. Entries in `always_include` are added unconditionally.

```bash
SKILL_DIR="$(find . .claude skills -path '*/swain-update/references' -print -quit 2>/dev/null | sed 's|/references$||')"
detected_agents=()

# Always-include platforms (we're running inside claude-code)
for name in $(jq -r '.always_include[]' "$SKILL_DIR/references/agent-platforms.json"); do
  detected_agents+=("$name")
done

# Detect remaining platforms via command -v or HOME dotfolder
while IFS= read -r entry; do
  name=$(echo "$entry" | jq -r '.name')
  cmd=$(echo "$entry" | jq -r '.command // empty')
  det=$(echo "$entry" | jq -r '.detection // empty')

  # Skip always-include (already added)
  for ai in "${detected_agents[@]}"; do [[ "$ai" == "$name" ]] && continue 2; done

  found=false
  if [[ -n "$cmd" ]] && command -v "$cmd" &>/dev/null; then
    found=true
  fi
  if [[ -n "$det" ]] && ! $found; then
    det_expanded=$(echo "$det" | sed "s|~|$HOME|g")
    det_expanded=$(eval echo "$det_expanded" 2>/dev/null)
    [[ -d "$det_expanded" ]] && found=true
  fi

  $found && detected_agents+=("$name")
done < <(jq -c '.agents[]' "$SKILL_DIR/references/agent-platforms.json")
```

Build the `-a` flags from detected agents:

```bash
agent_flags=""
for agent in "${detected_agents[@]}"; do
  agent_flags="$agent_flags -a $agent"
done
```

Tell the user which platforms were detected:
> Detected N agent platform(s): claude-code, codex, gemini-cli, ...

## Step 4 — Update via npx

Run the skills package manager with only the detected agents:

```bash
npx skills add cristoslc/swain $agent_flags -s '*' -y
```

This installs all skills (`-s '*'`) for only the detected platforms, skipping confirmation (`-y`). No dotfolder stubs are created for platforms that aren't installed.

If `npx` fails (command not found, network error, or non-zero exit), fall back to a direct git clone:

```bash
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/cristoslc/swain.git "$tmp/swain"
# Detect skill install location
INSTALL_DIR=$(find . -maxdepth 2 -name "swain-doctor" -type d -print -quit 2>/dev/null | sed 's|/swain-doctor$||')
INSTALL_DIR="${INSTALL_DIR:-.claude/skills}"
cp -r "$tmp/swain/skills/"* "$INSTALL_DIR/"
rm -rf "$tmp"
```

## Step 5 — Reconcile governance

Invoke the **swain-doctor** skill. This validates governance rules, cleans up legacy skill directories (including any renamed in this release), validates `.tickets/`, and untracks any runtime files that leaked into git. The skill is idempotent, so running it after every update is always safe.

## Step 6 — Restore guidance

If files were backed up in Step 2:

1. List the backed-up files with their paths
2. For each, explain the situation:
   - **User-added config files** (e.g., `config/yazi/yazi.toml`): Suggest moving to `.agents/config/<skill-name>/` or `swain.settings.json` where they'll survive future updates
   - **Patched scripts**: Show the diff between the backup and the new version. If the upstream version includes the fix, confirm the patch is no longer needed. If not, offer to re-apply the patch.
3. Remind the user: "To avoid this in future, store customizations in `.agents/config/` or `swain.settings.json` — these survive updates."

## Step 7 — Report

Display the current release version (from the latest git tag):

```bash
release_tag=$(git tag --sort=-v:refname | head -1)
echo "swain ${release_tag:-(unreleased)}"
```

Then list the installed swain skill directories and extract each skill's version from its `SKILL.md` frontmatter:

```bash
for skill in .claude/skills/swain-*/SKILL.md; do
  name=$(grep '^name:' "$skill" | head -1 | sed 's/name: *//')
  version=$(grep 'version:' "$skill" | head -1 | sed 's/.*version: *//')
  echo "  $name  v$version"
done
```

Show the user the list and confirm the update is complete.

If backups were created in Step 2, also show: "Backed up N modified files to `.agents/update-backup/<date>/`. See Step 5 for restore guidance."
