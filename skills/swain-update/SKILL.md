---
name: swain-update
description: "Update swain skills to the latest version. Use when the user says 'update swain', 'upgrade swain', 'pull latest swain', or wants to refresh their swain skills installation. Runs the skills package manager (npx) with a git-clone fallback, then invokes swain-doctor to reconcile governance and validate project health."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Update swain skills to latest
  version: 1.1.0
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

## Step 2 — Update via npx

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

## Step 3 — Reconcile governance

Invoke the **swain-doctor** skill. This validates governance rules, cleans up legacy skill directories (including any renamed in this release), repairs `.beads/.gitignore`, and untracks any runtime files that leaked into git. The skill is idempotent, so running it after every update is always safe.

## Step 4 — Report

List the installed swain skill directories and extract each skill's version from its `SKILL.md` frontmatter:

```bash
for skill in .claude/skills/swain-*/SKILL.md; do
  name=$(grep '^name:' "$skill" | head -1 | sed 's/name: *//')
  version=$(grep 'version:' "$skill" | head -1 | sed 's/.*version: *//')
  echo "  $name  v$version"
done
```

Show the user the list and confirm the update is complete.
