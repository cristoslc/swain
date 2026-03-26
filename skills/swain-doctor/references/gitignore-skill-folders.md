# Skill Folder Gitignore Hygiene

Verifies that vendored skill folders (`.claude/skills/`, `.agents/skills/`) are gitignored in consumer projects. Skips the check when the project is swain itself (skill source is tracked).

## Self-detection

Before running the gitignore check, determine whether the current project is the swain source repo:

```bash
remote_url="$(git remote get-url origin 2>/dev/null || true)"
if [[ "$remote_url" == *"cristoslc/swain"* ]]; then
  echo "skipped"  # Swain source repo — skill folders are tracked
  return
fi
```

If detected as swain: status `skipped`, message: "Swain source repo — skill folders are tracked."

## Detection

For each skill folder path, check whether it is covered by `.gitignore` rules:

```bash
SKILL_PATHS=(".claude/skills/" ".agents/skills/")
missing=()
for path in "${SKILL_PATHS[@]}"; do
  # Only check if the folder actually exists on disk
  if [[ -d "$path" ]] && ! git check-ignore -q "$path" 2>/dev/null; then
    missing+=("$path")
  fi
done
```

`git check-ignore -q` respects nested `.gitignore` files and global gitignore config — no string matching on `.gitignore` content.

## Status values

- **ok** — all existing skill folders are gitignored (or no skill folders exist on disk)
- **warning** — one or more skill folders exist but are not gitignored
- **skipped** — swain source repo detected; skill folders are intentionally tracked

## Remediation

When `missing` is non-empty, offer to append entries to the project's root `.gitignore`:

```bash
gitignore_entries="
# Vendored swain skills (managed by swain-update)
"
for path in "${missing[@]}"; do
  gitignore_entries+="$path
"
done
```

If `.gitignore` doesn't exist, create it. If it exists, append the missing entries (with a blank line separator).

### Remediation message

> Skill folder(s) not gitignored: `.claude/skills/`, `.agents/skills/`. These contain vendored skill dependencies and should not be committed to your repository.
>
> Add gitignore entries? (yes/no)

On **yes**: append entries and report `repaired`.
On **no**: report `warning` and continue.
