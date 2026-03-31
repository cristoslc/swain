# Platform Dotfolder Cleanup

The `npx skills add --all` command creates dotfolder stubs (e.g., `.windsurf/`, `.cursor/`) for agent platforms that are not installed. These directories only contain symlinks back to `.agents/skills/` and clutter the working tree.

Read platform data from `references/platform-dotfolders.json`. Each entry has a `project_dotfolder` name and one or both detection strategies: `command` (CLI binary name) and `detection` (HOME config directory path).

## Step 1 — Autodetect installed platforms

Iterate over the `platforms` array. A platform is **installed** if either check succeeds:

1. If the entry has a `command` field → `command -v <command> &>/dev/null`
2. If the entry has a `detection` field → expand the path (replace `~` with `$HOME`, evaluate env var defaults) and check whether the directory exists.

Always consider `.claude` installed (never a cleanup candidate).

```bash
installed_dotfolders=(".claude")
while IFS= read -r entry; do
  dotfolder=$(echo "$entry" | jq -r '.project_dotfolder')
  cmd=$(echo "$entry" | jq -r '.command // empty')
  det=$(echo "$entry" | jq -r '.detection // empty')

  found=false
  if [[ -n "$cmd" ]] && command -v "$cmd" &>/dev/null; then
    found=true
  fi
  if [[ -n "$det" ]] && ! $found; then
    det_expanded=$(echo "$det" | sed "s|~|$HOME|g")
    det_expanded=$(eval echo "$det_expanded" 2>/dev/null)
    [[ -d "$det_expanded" ]] && found=true
  fi

  $found && installed_dotfolders+=("$dotfolder")
done < <(jq -c '.platforms[]' "SKILL_DIR/references/platform-dotfolders.json")
```

*(Replace `SKILL_DIR` with the actual path to this skill's directory.)*

**Requires:** `jq`. If unavailable, skip and warn.

## Step 2 — Build cleanup candidates

Every platform entry whose `project_dotfolder` is NOT in `installed_dotfolders` is a candidate.

## Step 3 — Remove installer stubs

For each candidate:

1. Check whether the directory exists in the project root. Skip if not.
2. Verify it is installer-generated — should contain only a `skills/` subdirectory:
   ```bash
   entries=$(ls -A "<dotfolder>" 2>/dev/null | wc -l)
   if [[ "$entries" -le 1 ]] && [[ -d "<dotfolder>/skills" || "$entries" -eq 0 ]]; then
     rm -rf <dotfolder>  # Safe — installer stub
   fi
   ```
3. If the directory contains other content → skip and warn: "contains user content beyond installer symlinks."
4. Report: "Removed N platform dotfolder(s) created by `npx skills add`."
