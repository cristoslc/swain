---
name: swain-update
description: "Update swain skills to the latest version. Use when the user says 'update swain', 'upgrade swain', 'pull latest swain', or wants to refresh their swain skills installation. Runs the skills package manager (npx) with a git-clone fallback, then invokes swain-doctor to reconcile governance and validate project health."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Update swain skills to latest
  version: 1.2.0
  author: cristos
  license: MIT
  source: swain
---

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

## Step 3 — Update via npx

Run the skills package manager to pull the latest swain skills:

```bash
npx skills add cristoslc/swain --all
```

The `--all` flag (`--skill '*' --agent '*' -y`) ensures non-interactive execution by skipping confirmation prompts.

If `npx` fails (command not found, network error, or non-zero exit), fall back to a direct git clone:

```bash
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/cristoslc/swain.git "$tmp/swain"
cp -r "$tmp/swain/skills/"* .claude/skills/
rm -rf "$tmp"
```

## Step 4 — Reconcile governance

Invoke the **swain-doctor** skill. This validates governance rules, cleans up legacy skill directories (including any renamed in this release), repairs `.beads/.gitignore`, and untracks any runtime files that leaked into git. The skill is idempotent, so running it after every update is always safe.

## Step 5 — Restore guidance

If files were backed up in Step 2:

1. List the backed-up files with their paths
2. For each, explain the situation:
   - **User-added config files** (e.g., `config/yazi/yazi.toml`): Suggest moving to `.agents/config/<skill-name>/` or `swain.settings.json` where they'll survive future updates
   - **Patched scripts**: Show the diff between the backup and the new version. If the upstream version includes the fix, confirm the patch is no longer needed. If not, offer to re-apply the patch.
3. Remind the user: "To avoid this in future, store customizations in `.agents/config/` or `swain.settings.json` — these survive updates."

## Step 6 — Report

List the installed swain skill directories and extract each skill's version from its `SKILL.md` frontmatter:

```bash
for skill in .claude/skills/swain-*/SKILL.md; do
  name=$(grep '^name:' "$skill" | head -1 | sed 's/name: *//')
  version=$(grep 'version:' "$skill" | head -1 | sed 's/.*version: *//')
  echo "  $name  v$version"
done
```

Show the user the list and confirm the update is complete.

If backups were created in Step 2, also show: "Backed up N modified files to `.agents/update-backup/<date>/`. See Step 5 for restore guidance."
