---
name: swain-sync
description: "Fetch upstream, rebase, stage all changes, generate a descriptive commit message from the diff, commit, and push to the current branch's upstream. Handles merge conflicts by preferring local changes for config/project files and upstream for scaffolding."
user-invocable: true
allowed-tools: Bash, Read, Edit
metadata:
  short-description: Fetch, stage, commit, and push
  version: 1.1.0
  author: cristos
  license: MIT
  source: swain
---

Run through the following steps in order without pausing for confirmation unless a decision point is explicitly marked as requiring one.

Delegate this to a sub-agent so the main conversation thread stays clean. Include the full text of these instructions in the agent prompt, since sub-agents cannot read skill files directly.

## Step 1 — Fetch and rebase upstream

First, check whether the current branch has an upstream tracking branch:

```bash
git --no-pager rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null
```

If there is an upstream, fetch and rebase to incorporate upstream changes BEFORE staging or committing:

```bash
git fetch origin
```

If there are local changes (dirty working tree), stash them first:

```bash
git stash push -m "swain-sync: auto-stash before rebase"
git --no-pager rebase origin/$(git rev-parse --abbrev-ref HEAD)
git stash pop
```

If the rebase has conflicts after stash pop, abort and report:

```bash
git rebase --abort  # if rebase itself conflicts
git stash pop       # recover stashed changes
```

Show the user the conflicting files and stop. Do not force-push or drop changes.

If there is no upstream (new branch), skip this step entirely.

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

## Session bookmark

After a successful push, update the bookmark: `bash "$(find . .claude .agents -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null)" "Pushed {n} commits to {branch}"`
