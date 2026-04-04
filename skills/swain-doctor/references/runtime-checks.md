# Runtime Checks

Procedural checks for memory directory, settings, script permissions, .agents directory, status cache, and SSH alias readiness.

## Memory directory

The Claude Code memory directory stores `status-cache.json` and `stage-status.json`. Skills that write to this directory will fail silently or error if it doesn't exist. Note: `session.json` is stored at `.agents/session.json` (per-project, gitignored) — not in the memory directory.

### Step 1 — Compute the correct path

The directory slug is derived from the **full absolute repo path**, not just the project name:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
_PROJECT_SLUG=$(echo "$REPO_ROOT" | tr '/' '-')
MEMORY_DIR="$HOME/.claude/projects/${_PROJECT_SLUG}/memory"
```

### Step 2 — Create if missing

```bash
if [[ ! -d "$MEMORY_DIR" ]]; then
  mkdir -p "$MEMORY_DIR"
fi
```

If created, tell the user:
> Created memory directory at `$MEMORY_DIR`. This is where swain-session stores its caches.

If it already exists, this step is silent.

### Step 3 — Validate existing cache files

If the memory directory exists, check that any existing JSON files in it are valid:

```bash
for f in "$MEMORY_DIR"/*.json; do
  [[ -f "$f" ]] || continue
  if ! jq empty "$f" 2>/dev/null; then
    echo "warning: $f is corrupt JSON — removing"
    rm "$f"
  fi
done
```

Report any files that were removed due to corruption. This prevents skills from reading garbage data.

**Requires:** `jq` (skip this step if jq is not available — warn instead).

## Settings validation

Swain uses a two-tier settings model. Malformed JSON in either file causes silent failures across multiple skills (swain-session).

### Check project settings

If `swain.settings.json` does not exist in the repo root, create it with an empty object:

```bash
if [[ ! -f swain.settings.json ]]; then
  echo '{}' > swain.settings.json
fi
```

If created, report **repaired**:
> Created `swain.settings.json` with empty defaults. All settings have built-in defaults.

If `swain.settings.json` exists, validate it:

```bash
jq empty swain.settings.json 2>/dev/null
```

If this fails, warn:
> `swain.settings.json` contains invalid JSON. Skills will fall back to defaults. Fix the file or delete it to use defaults.

### Check user settings

If `${XDG_CONFIG_HOME:-$HOME/.config}/swain/settings.json` exists:

```bash
jq empty "${XDG_CONFIG_HOME:-$HOME/.config}/swain/settings.json" 2>/dev/null
```

If this fails, warn:
> User settings file contains invalid JSON. Skills will fall back to project defaults. Fix the file or delete it.

**Requires:** `jq` (skip these checks if jq is not available).

## Script permissions

All shell and Python scripts in the installed skill tree, usually `.agents/skills/*/scripts/`, must be executable. Skills invoke these via `.agents/bin/` or by direct path, and Python helpers may be run directly, so the executable bit still matters.

### Check and repair

```bash
find .agents/skills -type f \( -path '*/scripts/*.sh' -o -path '*/scripts/*.py' \) ! -perm -u+x
```

If any files are found without the executable bit:

```bash
chmod +x <files...>
```

Tell the user:
> Fixed executable permissions on N script(s).

If all scripts are already executable, this step is silent.

## SSH alias readiness

Repos that ran `swain-keys --provision` switch `origin` to a project-specific SSH alias such as `git@github.com-swain:owner/repo.git`. The alias targets `ssh.github.com:443` so it works in environments where GitHub SSH on port 22 is blocked. Sandboxes and fresh runtimes often have a different `HOME`, so the repo can point at an alias that does not exist locally even though git signing is configured.

### Detection and repair

Use the helper:

```bash
bash scripts/ssh-readiness.sh --repair
```

The helper is a no-op for repos that do not use a `github.com-<project>` alias remote.

For alias remotes, it checks:

- `ssh` is available on `PATH`
- `~/.ssh/config` exists and includes `config.d/*`
- `~/.ssh/config.d/<project>.conf` exists
- the alias config defines `Host github.com-<project>`
- the alias `IdentityFile` exists locally

### Repair behavior

`--repair` only performs safe local fixes:

- creates `~/.ssh/` and `~/.ssh/config.d/`
- creates or patches `~/.ssh/config` to include `config.d/*`
- creates `~/.ssh/config.d/<project>.conf` when the default key `~/.ssh/<project>_signing` already exists

It does **not** generate keys or install packages. If the key is missing, report:

> SSH alias is configured but the local key is missing. Run `swain-keys --provision` in this runtime.

If `ssh` is missing, warn and provide an install hint. Do not install automatically during doctor.

## .agents directory

The `.agents/` directory stores per-project configuration for swain skills:
- `execution-tracking.vars.json` — swain-do first-run config
- `specwatch.log` — swain-design stale reference log
- `trovewatch.log` — swain-search pool refresh log

### Check and create

```bash
if [[ ! -d ".agents" ]]; then
  mkdir -p ".agents"
fi
```

If created, tell the user:
> Created `.agents/` directory for skill configuration storage.

If it already exists, this step is silent.

## Status cache bootstrap

If the memory directory exists but `status-cache.json` does not, and the status script is available, seed an initial cache so that consumers have data on first use.

```bash
STATUS_SCRIPT="$REPO_ROOT/.agents/bin/swain-status.sh"
if [[ -f "$STATUS_SCRIPT" && ! -f "$MEMORY_DIR/status-cache.json" ]]; then
  bash "$STATUS_SCRIPT" --json > /dev/null 2>&1 || true
fi
```

If the cache was created, tell the user:
> Seeded initial status cache. The MOTD and status dashboard now have data.

If the script is not available or the cache already exists, this step is silent. If the script fails, ignore — the cache will be created on the next `swain-roadmap` invocation.
