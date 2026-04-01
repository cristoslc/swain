---
name: swain-sync
description: "Fetch upstream, merge (worktree) or rebase (tracked branch), stage all changes, enforce gitignore hygiene, run ADR compliance checking on modified artifacts, rebuild stale artifact indexes, generate a descriptive commit message from the diff, commit, and push to the current branch's upstream. Handles merge conflicts by preferring local changes for config/project files and upstream for scaffolding."
user-invocable: true
allowed-tools: Bash, Read, Edit, Write, Glob
metadata:
  short-description: Fetch, stage, commit, and push
  version: 1.5.0
  author: cristos
  license: MIT
  source: swain
---
<!-- swain-model-hint: sonnet, effort: low -->

<!-- session-check: SPEC-121 -->
Before proceeding with any state-changing operation, check for an active session:
```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null
```
If the JSON output has `"status"` other than `"active"`, inform the operator: "No active session — start one with `/swain-session`?" Proceed if they dismiss.

Run through the following steps in order without pausing for confirmation unless a decision point is explicitly marked as requiring one.

Delegate this to a sub-agent so the main conversation thread stays clean. Include the full text of these instructions in the agent prompt, since sub-agents cannot read skill files directly.

## Step 1 — Detect worktree context and fetch/rebase upstream

First, detect whether you are running in a git linked worktree:

```bash
GIT_COMMON=$(git rev-parse --git-common-dir)
GIT_DIR=$(git rev-parse --git-dir)
IN_WORKTREE=$( [ "$GIT_COMMON" != "$GIT_DIR" ] && echo "yes" || echo "no" )
REPO_ROOT=$(git rev-parse --show-toplevel)
TRUNK=$(bash "$REPO_ROOT/.agents/bin/swain-trunk.sh")
```

`IN_WORKTREE=yes` means the current directory is inside a linked worktree (e.g., `.claude/worktrees/agent-abc123`). Use this flag in Steps 3, 6, and the session bookmark step.

Next, check whether the current branch has an upstream tracking branch:

```bash
git --no-pager rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null
```

If there is an upstream, fetch and rebase to incorporate upstream changes BEFORE staging or committing:

```bash
git fetch origin
```

If there are local changes (dirty working tree), stash them first:

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git stash push -m "swain-sync: auto-stash [$BRANCH]"
git --no-pager rebase origin/$BRANCH
git stash pop
```

If the rebase has conflicts after stash pop, abort and report:

```bash
git rebase --abort  # if rebase itself conflicts
git stash pop       # recover stashed changes
```

Show the user the conflicting files and stop. Do not force-push or drop changes.

If there is no upstream (`@{u}` returns an error) **and** `IN_WORKTREE=yes`, the worktree branch has no remote tracking counterpart. Merge the trunk branch to combine the agent's changes with whatever landed since the branch was created:

```bash
git fetch origin
git merge "origin/$TRUNK" --no-edit
```

If the merge has conflicts, report them and stop. Do not attempt to auto-resolve.

If `origin` cannot be fetched, skip fetch/rebase and proceed to Step 2.

If there is no upstream **and** `IN_WORKTREE=no` (main worktree, new branch), skip this step entirely.

## Step 2 — Survey the working tree

```bash
git --no-pager status
git --no-pager diff          # unstaged changes
git --no-pager diff --cached # already-staged changes
```

If the working tree is completely clean and there is nothing to push, report that and stop.

## Step 3 — Stage changes

Identify files that look like secrets (`.env`, `*.pem`, `*_rsa`, `credentials.*`, `secrets.*`). If any are present, warn the user and exclude them from staging.

**If there are 10 or fewer changed files** (excluding secrets), stage them individually:

```bash
git add file1 file2 ...
```

**If there are more than 10 changed files**, stage everything and then unstage secrets:

```bash
git add -A
git reset HEAD -- <secret-file-1> <secret-file-2> ...
```

## Step 3.5 — Gitignore check

Before committing, verify `.gitignore` hygiene. **This step is blocking** — if relevant patterns are missing, stop and require the user to fix `.gitignore` before proceeding.

### 1. Check existence

If no `.gitignore` file exists in the repo root:

> STOP: No `.gitignore` file found. Create one before committing — without it, secrets, build artifacts, and OS files can enter git history.
> Minimal starting point: `curl -sL https://www.toptal.com/developers/gitignore/api/macos,linux,node,python > .gitignore`

**Stop execution.** Do not commit.

### 2. Detect relevant patterns

Check which patterns are *relevant* to this repo, based on what actually exists on disk:

| Pattern | Relevant if |
|---------|-------------|
| `.env` | `.env.example` exists, OR any untracked/tracked `.env` or `.env.*` file is present (excluding `.env.example`), OR `dotenv` appears in `package.json` or `requirements.txt` |
| `node_modules/` | `package.json` exists in the repo root or any subdirectory |
| `__pycache__/` | any `*.py` file exists in the repo |
| `*.pyc` | same as `__pycache__/` |
| `.DS_Store` | repo is on macOS (`uname` returns `Darwin`) |

For each relevant pattern, check if `.gitignore` contains it (exact match or substring). Collect missing ones.

### 3. Decide whether to block

- If **no relevant patterns are missing**: this step is silent. Continue to Step 3.7.
- If **any relevant patterns are missing**: stop and report:

  > STOP: `.gitignore` is missing patterns relevant to this repo:
  >   - `.env` — `.env.example` found; without this, a local `.env` file could be committed
  >   - `node_modules/` — `package.json` found
  >
  > Add the missing patterns before committing:
  >   echo ".env" >> .gitignore
  >   echo "node_modules/" >> .gitignore
  >
  > To permanently suppress a specific pattern check (intentional omission), add a comment to `.gitignore`:
  >   # swain-sync: allow .env

  **Stop execution.** Do not commit until the user resolves this.

### 4. Skip logic

If `.gitignore` contains `# swain-sync: allow <pattern>` for a given pattern, treat that pattern as intentionally omitted and do not flag it.

## Step 3.7 — ADR compliance check

If modified files include any swain artifacts (`docs/spec/`, `docs/epic/`, `docs/vision/`, `docs/research/`, `docs/journey/`, `docs/persona/`, `docs/runbook/`, `docs/design/`, `docs/train/`), run an ADR compliance check against each modified artifact:

```bash
bash "$REPO_ROOT/.agents/bin/adr-check.sh" <artifact-path>
```

For each artifact with findings (exit code 1 = advisory RELEVANT findings, exit code 2 = actionable DEAD_REF or STALE findings), collect the output and present a single consolidated warning after all checks complete:

> ADR compliance: N artifact(s) have findings that may need attention.
> <condensed findings summary>

This step is **advisory** — it warns but never blocks the commit. Continue to Step 4 regardless.

If the `adr-check.sh` script is not found or fails with exit code 3, skip silently — the check is only available in repos with swain-design installed.

## Step 3.8 — Design drift check

Run `design-check.sh` with no arguments (scan all active DESIGNs) to detect design-to-code drift:

```bash
bash "$REPO_ROOT/.agents/bin/design-check.sh" 2>/dev/null
```

For each DESIGN with findings (STALE or BROKEN `sourcecode-refs`), collect the output and present a single consolidated warning after the check completes:

> Design drift: N DESIGN(s) have stale or broken sourcecode-refs.
> <condensed findings summary>

This step is **advisory** — it warns but never blocks the commit. Continue to Step 4 regardless.

If the `design-check.sh` script is not found or fails with exit code 2, skip silently — the check is only available in repos with swain-design installed.

## Step 3.9 — Artifact number collision check

Run `detect-duplicate-numbers.sh` to find duplicate artifact numbers introduced by merges or concurrent worktree work:

```bash
bash "$REPO_ROOT/.agents/bin/detect-duplicate-numbers.sh" 2>/dev/null
```

If collisions are found (exit code 1), this step is **blocking** — do not commit until resolved:

> Artifact number collision detected:
> <collision output>
>
> Auto-fix available: run `fix-collisions.sh` to renumber the newer artifact(s).
> Or run `fix-collisions.sh --dry-run` to preview changes first.

Offer to run `fix-collisions.sh` automatically. If the operator accepts, run it, stage the changes, and continue to Step 4. If the operator declines, **stop execution** — do not commit with duplicate numbers.

If the script is not found, skip silently — the check is only available in repos with swain-design installed.

## Step 4 — Generate a commit message

Read the staged diff (`git --no-pager diff --cached`) and write a commit message that:

- Opens with a **conventional-commit prefix** matching the dominant change type:
  - `feat` — new feature or capability
  - `fix` — bug fix
  - `docs` — documentation only
  - `chore` — tooling, deps, config with no behavior change
  - `refactor` — restructuring without behavior change
  - `test` — test additions or fixes
- Includes a concise imperative-mood subject line (≤ 72 chars).
- Adds a short body (2–5 lines) summarising *why*, not just *what*, when the diff is non-trivial.
- Appends a `Co-Authored-By` trailer identifying the model that generated the commit. Use the model name from your system prompt (e.g., `Claude Opus 4.6`, `Gemini 2.5 Pro`). If you can't determine the model name, use `AI Assistant` as a fallback.

Example shape:
```
feat(terraform): add Cloudflare DNS module for hub provisioning

Operators can now point DNS at Cloudflare without migrating their zone.
Module is activated by dns_provider=cloudflare and requires only
CLOUDFLARE_API_TOKEN — no other provider credentials are validated.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

## Step 4.5 — Pre-commit hook check

Check if pre-commit hooks are configured:

```bash
test -f .pre-commit-config.yaml && command -v pre-commit >/dev/null 2>&1 && echo "hooks-configured" || echo "no-hooks"
```

If `no-hooks`, emit a one-time warning (do not repeat if the same session already warned):
> WARN: No pre-commit hooks configured. Run `/swain-init` to set up security scanning.

Continue to Step 5 regardless — hooks are recommended but not required.

## Step 5 — Commit

```bash
git --no-pager commit -m "$(cat <<'EOF'
<generated message here>
EOF
)"
```

Use a heredoc so multi-line messages survive the shell without escaping issues.

**IMPORTANT:** Never use `--no-verify`. If pre-commit hooks are installed, they MUST run. There is no bypass.

If the commit fails because a pre-commit hook rejected it:

1. Parse the output to identify which hook(s) failed and what was found
2. Present findings clearly:
   > Pre-commit hook failed:
   >   gitleaks: 2 findings (describe what was flagged)
   >
   > Fix the findings and run `/swain-sync` again.
   > Suppress false positives: add to `.gitleaksignore`
3. **Stop execution** — do not push. Do not retry automatically.

## Step 6 — Push

**If `IN_WORKTREE=yes`:** fetch and integrate upstream changes, then push the worktree's commits directly to `trunk` (the development branch):

```bash
# Always fetch and merge trunk before the first push attempt.
# This prevents avoidable rejections when trunk moved since the worktree was created.
git fetch origin
git merge "origin/$TRUNK" --no-edit || {
  echo "Merge conflict with upstream trunk. Resolve before pushing."
  git merge --abort
  exit 1
}

# Link safety — scan changed files for worktree-specific path links (SPEC-216/217/218)
# Runs after merge, before push, so any auto-fixes land in the same push.
DETECT_SCRIPT="$(git rev-parse --show-toplevel)/.agents/bin/detect-worktree-links.sh"
RESOLVE_SCRIPT="$(git rev-parse --show-toplevel)/.agents/bin/resolve-worktree-links.sh"
if [ -x "$DETECT_SCRIPT" ]; then
  MERGE_BASE=$(git merge-base HEAD "origin/$TRUNK" 2>/dev/null || true)
  CHANGED_FILES=$([ -n "$MERGE_BASE" ] && git diff --name-only "$MERGE_BASE" HEAD 2>/dev/null || true)
  if [ -n "$CHANGED_FILES" ]; then
    if ! echo "$CHANGED_FILES" | xargs "$DETECT_SCRIPT" --repo-root "$(git rev-parse --show-toplevel)" > /dev/null 2>&1; then
      echo "[link-safety] Found suspicious links. Resolving automatically..."
      if ! echo "$CHANGED_FILES" | xargs "$RESOLVE_SCRIPT" --repo-root "$(git rev-parse --show-toplevel)"; then
        echo "[link-safety] UNRESOLVABLE links remain — merge aborted. Fix before pushing."
        exit 1
      fi
      git add -u
      ORIG_MSG=$(git log -1 --pretty=%B)
      git commit --amend -m "$ORIG_MSG

[link-safety: auto-resolved worktree path links]"
    fi
  fi
fi

MAX_RETRIES=3
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_RETRIES ]; do
  git push origin "HEAD:$TRUNK" && break
  ATTEMPT=$((ATTEMPT + 1))
  if [ $ATTEMPT -lt $MAX_RETRIES ]; then
    echo "Push rejected (attempt $ATTEMPT/$MAX_RETRIES). Fetching and re-merging..."
    git fetch origin
    git merge "origin/$TRUNK" --no-edit || {
      echo "Merge conflict during retry. Reporting to operator."
      git merge --abort
      break
    }
    # Run tests on the merged result before retrying push
    # (project-specific test command — detect from project structure)
  fi
done

if [ $ATTEMPT -ge $MAX_RETRIES ]; then
  echo "Push failed after $MAX_RETRIES attempts. Reporting to operator."
fi
```

If the push is rejected due to branch protection rules or required reviews (check the rejection message), fall back to opening a PR instead:

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
SUBJECT=$(git log -1 --pretty=format:'%s')
BODY=$(git log -1 --pretty=format:'%b')
gh pr create --base "$TRUNK" --head "$BRANCH" --title "$SUBJECT" --body "$BODY"
```

Report the PR URL. Do not retry the push. Proceed to worktree pruning below.

After a successful push or PR creation, clean up the worktree — but only if swain-sync created it. Worktrees entered via `EnterWorktree` (branch name matches `worktree-*`) must be left for `ExitWorktree` to clean up, since `ExitWorktree` properly restores the session's CWD before removal. Removing them here would leave the parent session's CWD pointing at a deleted directory, causing ENOENT on all subsequent hook spawns (SPEC-127).

```bash
WORKTREE_PATH=$(pwd)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
MAIN_REPO=$(git rev-parse --git-common-dir | sed 's|/.git$||')

case "$BRANCH" in worktree-*)
  # SPEC-127: Worktree entered via EnterWorktree — do NOT remove.
  # ExitWorktree handles cleanup and CWD restoration.
  echo "Worktree branch '$BRANCH' entered via EnterWorktree — skipping removal (ExitWorktree will clean up)."
  ;;
*)
  # SPEC-100: Restore CWD *before* removal — otherwise the session is stuck
  # in a deleted directory and all subsequent commands (hooks, git, etc.) fail.
  cd "$MAIN_REPO" || cd "$HOME"
  git -C "$MAIN_REPO" worktree remove --force "$WORKTREE_PATH" 2>/dev/null || true
  git -C "$MAIN_REPO" worktree prune 2>/dev/null || true
  ;;
esac
```

**If `IN_WORKTREE=no`** (main worktree, normal case):

```bash
git push          # or: git push -u origin HEAD (if no upstream)
```

If push fails due to divergent history (shouldn't happen after Step 1 rebase, but as a safety net):

```bash
git --no-pager pull --rebase
git push
```

## Step 7 — Verify

Run `git --no-pager status` and `git --no-pager log --oneline -3` to verify the push landed and show the user the final state. Do not prompt for confirmation — just report the result.

## Index rebuild (SPEC-047)

Before committing (after staging, before Step 5), check whether any artifact index files (`list-*.md`) are stale. If the rebuild script exists, run it for each artifact type that had changes staged:

```bash
REBUILD_SCRIPT="$REPO_ROOT/.agents/bin/rebuild-index.sh"
if [[ -x "$REBUILD_SCRIPT" ]]; then
    # Detect which types had staged changes
    for type in spec epic spike adr persona runbook design vision journey train; do
        if git diff --cached --name-only | grep -q "^docs/$type/"; then
            bash "$REBUILD_SCRIPT" "$type"
            git add "docs/$type/list-${type}.md" 2>/dev/null || true
        fi
    done
fi
```

This ensures the index is current when the session's commits land.

## Session bookmark

After a successful push, update the bookmark. Use `$REPO_ROOT` (set in Step 1) as the search root so this works from both main and linked worktrees:

```bash
bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" "Pushed {n} commits to {branch}"
```
