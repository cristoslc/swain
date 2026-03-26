# Skill Folder Gitignore Hygiene

Verifies that vendored **swain** skill directories are gitignored in consumer projects. Only targets `swain/` and `swain-*/` subdirectories — consumer projects may have their own project-specific skills in `.claude/skills/` or `.agents/skills/` that should remain tracked.

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

Enumerate vendored swain skill directories that exist on disk and check whether each is covered by `.gitignore` rules:

```bash
missing=()
for base in .claude/skills .agents/skills; do
  [ -d "$base" ] || continue
  for dir in "$base"/swain "$base"/swain-*/; do
    [ -d "$dir" ] || continue
    if ! git check-ignore -q "$dir" 2>/dev/null; then
      missing+=("$dir")
    fi
  done
done
```

`git check-ignore -q` respects nested `.gitignore` files and global gitignore config — no string matching on `.gitignore` content.

## Status values

- **ok** — all vendored swain skill directories are gitignored (or none exist on disk)
- **warning** — one or more vendored swain skill directories exist but are not gitignored
- **skipped** — swain source repo detected; skill folders are intentionally tracked

## Remediation

When `missing` is non-empty, offer to append entries to the project's root `.gitignore`:

```bash
gitignore_entries="
# Vendored swain skills (managed by swain-update)
.claude/skills/swain/
.claude/skills/swain-*/
.agents/skills/swain/
.agents/skills/swain-*/
"
```

If `.gitignore` doesn't exist, create it. If it exists, append the missing entries (with a blank line separator).

### Remediation message

> Vendored swain skill folder(s) not gitignored: {list}. These contain vendored skill dependencies and should not be committed to your repository.
>
> Add gitignore entries? (yes/no)

On **yes**: append entries and report `repaired`.
On **no**: report `warning` and continue.
