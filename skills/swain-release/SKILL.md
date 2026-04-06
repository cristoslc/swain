---
name: swain-release
description: Cut a release — detect versioning context, generate a changelog from conventional commits, bump versions, create a git tag, and optionally squash-merge to a release branch. Use when the user says "release", "cut a release", "tag a release", "bump the version", "create a changelog", "ship a version", "publish", or any variation of shipping/publishing a version. This skill is intentionally generic and works across any repo — it infers context from git history and project structure rather than assuming a specific setup. Supports the trunk+release branch model (ADR-013) when a `release` branch exists.
license: UNLICENSED
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion
metadata:
  short-description: Version bump, changelog, and git tag
  version: 1.5.1
  author: cristos
  source: swain
---
<!-- swain-model-hint: sonnet, effort: medium -->

# Release

<!-- session-check: SPEC-121 -->
Before proceeding with any state-changing operation, check for an active session:
```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null
```
If the JSON output has `"status"` other than `"active"`, inform the operator: "No active session — start one with `/swain-init`?" Proceed if they dismiss.

Cut a release by detecting the project's versioning context, generating a changelog, bumping versions, and tagging. Works across any repo by reading context from git history and project structure rather than hardcoding assumptions.

## Override file

Before starting, read `.agents/release.override.skill.md` if it exists. This is a freeform markdown file authored by the project owner whose instructions layer on top of this skill — its contents take precedence where they conflict. It can narrow defaults, specify version file locations, set tag formats, add pre/post-release steps, or anything else.

If no override exists, proceed with context detection alone.

## Workflow

### 1. Gather context

Infer the project's release conventions from what already exists. Do all of these checks up front before proposing anything to the user.

**Tag history:**
```bash
git tag --sort=-v:refname | head -20
```
From existing tags, infer:
- **Tag format** — `v1.2.3`, `1.2.3`, `name-v1.2.3`, or something else
- **Versioning scheme** — semver, calver, or custom
- **Current version** — the most recent tag that matches the detected pattern

If there are no tags at all, note that this is the first release and ask the user what format they want.

**Commits since last release:**
```bash
git log <last-tag>..HEAD --oneline --no-decorate
```
If no tags exist, use all commits (or a reasonable window — ask the user if there are hundreds).

**Version files** — scan for files that commonly hold version numbers:
```bash
# Look for common version carriers
grep -rl 'version' --include='*.json' --include='*.toml' --include='*.yaml' --include='*.yml' -l . 2>/dev/null | head -20
```
Also check for `VERSION` files, `version:` in SKILL.md frontmatter, `version` fields in `package.json`, `pyproject.toml`, `Cargo.toml`, etc. Don't modify anything yet — just catalog what exists.

### 2. Determine the bump

Parse commits since the last tag using conventional-commit prefixes to suggest a bump level:

| Commit prefix | Suggests |
|---------------|----------|
| `feat` | minor bump |
| `fix` | patch bump |
| `docs`, `chore`, `refactor`, `test`, `ci` | patch bump |
| `BREAKING CHANGE` in body, or `!` after type | major bump |

The highest-level signal wins (any breaking change = major, any feat = at least minor, otherwise patch).

If commits don't follow conventional-commit format, fall back to listing them and asking the user what bump level feels right.

### 3. Propose the release

Present the user with a release plan before executing anything. Include:

- **Current version** (from latest tag, or "first release")
- **Proposed version** (with the detected bump applied)
- **Changelog preview** (thematic narrative — see step 4)
- **Files to update** (version files found in step 1, if any)
- **Tag to create** (using the detected format)

Wait for the user to confirm, adjust the version, or abort. If the user wants a different version than what was suggested, use theirs — the suggestion is a starting point, not a mandate.

### 4. Generate the changelog

**Synthesize, don't transcribe.** The changelog is for humans reading release notes, not for `git log --oneline` with extra steps. Dozens of commits should collapse into a few coherent narratives.

Before writing, read the existing CHANGELOG.md (if any) to match the voice, density, and structure the project already uses. The changelog should read like the same person wrote every entry.

#### Template-driven changelog

The changelog is rendered from a Jinja2 template (`templates/changelog.md.j2`) fed by a JSON data file. This separates the bucketing decision (which section does a change belong in?) from the rendering (how does the markdown look?).

**Step 4a — Classify commits into four buckets.** Each commit goes into exactly one:

| Bucket | What belongs here | What does NOT belong here |
|--------|-------------------|--------------------------|
| `features` | Shipped capability that the operator can interact with today: new skills, new CLI commands, new scripts the operator invokes, bug fixes to operator-facing workflows. The test: "can the operator do something new or different because of this?" | Planning artifacts, internal quality improvements, threshold tweaks to internal tools, internal test suites, bug fixes to scripts the operator never invokes directly. |
| `roadmap` | Forward-looking previews of planned work — what's coming and why it matters to the user. Write as "X is being planned/designed because Y" not "SPEC-NNN created". Omit artifact IDs unless the reader would search for them. Skip items that are pure internal housekeeping. | Artifact state transitions ("EPIC activated", "SPEC created"), anything that shipped (that's features). |
| `research` | Trove collections, spike completions, research artifacts, evidence gathered. | Specs that resulted from research (those are roadmap). |
| `supporting` | Internal quality improvements, internal test suites, threshold changes to internal tools, bug fixes to internal scripts, dependency bumps, cross-ref enrichment, minor refactors, CI changes. | Anything the operator interacts with directly (that's features). |

The key distinction agents get wrong: **creating a SPEC or EPIC is a roadmap change, not a feature.** A feature is something the operator can use *today* because it shipped in this release. A SPEC is a plan for something that will ship *later*.

The second distinction agents get wrong: **internal improvements are supporting, not features.** Raising an internal threshold, fixing an anti-pattern in internal scripts, adding a test suite for swain's own code — these improve quality but don't give the operator a new capability. Ask: "would the operator notice this in their daily workflow?" If the answer is "only if something was broken before," it's supporting.

**Roadmap anti-pattern:** "EPIC-029 activated with 3 child SPECs (SPEC-118, SPEC-119, SPEC-120)" is noise — it describes artifact state transitions that only matter to the project maintainer. Instead write: "Trunk detection is being generalized so swain works on any branch name without configuration." The reader should understand *what's coming and why they'd care*, not which internal tracking artifacts changed state.

**Supporting anti-patterns — things that do NOT go in supporting:**
- Development process changes ("close handler reordered", "session-state tolerance added") — these are implementation details; omit them entirely.
- Artifact state transitions ("EPIC-053 approved and activated", "SPEC-220 created") — these describe planning activity, not shipped work; omit or put in roadmap.
- Untracked files that existed before the release window — only include files that changed in the diff.
- Bug fixes to operator-facing workflows — those are features, not supporting.

**Supporting includes:** dependency bumps, CI/config changes, internal refactors, cleanup of dead code, readability fixes, internal test suites, threshold changes to internal tools, bug fixes to internal scripts (scripts the operator never invokes directly).

Omit mechanical commits entirely: merge commits, lifecycle hash stamps, index refreshes, bookmark advances.

**Bucket assignment is mutually exclusive.** If something appears in features it does not appear in roadmap or supporting. If it appears in roadmap it is not in supporting. Every commit goes in exactly one bucket or is omitted.

**Step 4b — Write the changelog markdown directly.** Use the template at `templates/changelog.md.j2` as a **structure guide**, not as a render target. Write the markdown yourself following this format:

```markdown
## [0.10.0-alpha] - 2026-03-21

### Features

#### CLI Roadmap Renderer

chart.sh roadmap --cli produces deterministic, terminal-friendly
output grouped by Eisenhower quadrant with all first-degree children
nested under their parent initiative. New swain-roadmap skill wraps
it as the user-facing entry point: regenerate, open, display.

### Planned

- Session facilitation rebuild — rethinking how swain helps the operator maintain focus, make decisions, and recover context across sessions.

### Research

- Google Stitch SDK trove — 7 sources collected.

### Supporting Changes

- Dependency graph rendering switched to flowchart TD for clearer layout.
- Cross-reference enrichment across ~100 doc files.
```

**Formatting rules:**
- The Features section uses **headings only** — each feature gets an `#### Heading` with a narrative paragraph. No standalone bullets in Features. If a change is too small for its own heading, fold it into a related heading's narrative or move it to Supporting.
- Planned and Roadmap sections can mix headings and bullets — headings for major planned work with enough substance for a paragraph, bullets for one-liners.
- Research and Supporting sections are always flat bullet lists.
- Omit empty sections entirely.

#### What to omit

Merge commits, lifecycle hash stamps, index refreshes, bookmark advances, and other mechanical commits should be omitted entirely — they add noise without information. Commit-type prefixes (`feat:`, `fix:`) should be stripped from any text that makes it into the changelog.

#### Use commit prefixes for bump detection, not changelog structure

Conventional-commit types determine whether it's a major/minor/patch bump (step 2). After that, forget them — the changelog reader doesn't care that something was a `feat` vs `docs`.

**Where to put the changelog:**
- If a `CHANGELOG.md` exists, prepend the new section at the top (below any header)
- If no changelog exists, ask the user whether they want one created, and where
- If the user doesn't want a file, just output it to the conversation

### 5. Bump versions

Update version strings in the files identified in step 1. Be surgical — only change the version value, not surrounding content. For each file type:

- **package.json / composer.json**: update the `"version"` field
- **pyproject.toml / Cargo.toml**: update `version = "..."`
- **SKILL.md frontmatter**: update `version:` in YAML header
- **VERSION file**: replace contents

If a file has multiple version-like strings and it's ambiguous which one to update, ask the user rather than guessing.

### 5.5. Security gate

Before tagging, run the security scanner to catch secrets, dependency vulnerabilities, and static analysis issues. Invoke the **swain-security-check** skill (or run the scanner script directly if the skill isn't available):

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCANNER="$REPO_ROOT/.agents/bin/security-scan.sh"
if [[ -n "$SCANNER" ]]; then
  bash "$SCANNER"
fi
```

If any **critical** or **high** severity findings are reported, stop the release and present them to the user. The user can choose to:
- Fix the issues and resume
- Acknowledge the findings and proceed anyway (their call, not yours)

Medium and lower findings should be reported but do not block the release.

If the security scanner is not installed, note the gap and proceed — don't block on a missing tool.

### 5.7. README gate (SPEC-211)

Two-part hard gate that verifies README alignment and test coverage of README promises. Both must pass or be explicitly overridden before tagging.

**Skip condition:** If README.md does not exist, skip this gate — swain-doctor already flags the missing README. Do not block a release on a file that was never created.

#### Part 1: Alignment check

Read README.md and extract all claims about what the project does, who it's for, how it works, and what it supports. Compare against the current Active artifact tree (Visions, Designs, Journeys, Specs).

Surface each mismatch:
- **Stale promises** — README claims a feature or behavior that an artifact explicitly dropped or superseded.
- **Missing coverage** — an artifact describes a shipped capability the README doesn't mention.
- **Contradictions** — README and artifact disagree on behavior, audience, or scope.

Unresolved drift blocks the release. For each finding, the operator must:
1. Update the README to match reality, or
2. Update the artifact to match the README, or
3. Explicitly override — state why the drift is acceptable. The override is recorded in the release notes.

#### Part 2: Verification check

Identify README claims that imply testable behavior:

- **Install/setup claims** — "run `npm install && npm start`" implies a smoke test that the install path works.
- **CLI behavior** — "`foo init` creates a project" implies an integration test.
- **API surface** — "exports a `createWidget` function" implies an export existence test.
- **Behavioral promises** — "automatically retries on failure" implies a retry behavior test.
- **Integration claims** — "works with PostgreSQL 15+" implies a version-specific integration test.

For each untested promise, the operator chooses:
1. **Add a test** — release pauses for test creation, then re-runs the check.
2. **Remove the promise** — README is updated and the check re-runs.
3. **Accept the gap** — the gap is recorded in the release notes.

#### Override

The operator can override the full README gate with an explicit statement. The override and its reason are recorded in the release metadata (changelog or tag annotation). No silent bypass — the operator must state why they're overriding.

### 6. Commit and tag

Stage the changed files (changelog + version bumps) and commit:

```bash
git add <changed-files>
git commit -m "release: v1.5.0"
```

Then create an annotated tag:

```bash
git tag -a <tag> -m "Release <tag>"
```

Use the tag format detected in step 1 (or what the user specified).

### 6.5. Squash-merge to release branch

If a `release` branch exists (check with `git rev-parse --verify release 2>/dev/null`), squash-merge the current branch (trunk) into it:

```bash
# Detect trunk branch dynamically (EPIC-029)
REPO_ROOT=$(git rev-parse --show-toplevel)
TRUNK=$(bash "$REPO_ROOT/.agents/bin/swain-trunk.sh")
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Ensure we're on the trunk (development) branch
if [ "$CURRENT_BRANCH" != "$TRUNK" ]; then
  echo "Warning: not on $TRUNK ($CURRENT_BRANCH). Skipping release branch update."
else
  # Tag trunk first (lifecycle hashes must be reachable from trunk per ADR-012)
  # Tag was already created in step 6

  # Squash-merge trunk into release
  git checkout release
  git merge --squash "$TRUNK"
  git commit -m "release: <tag>"

  # Return to trunk
  git checkout "$TRUNK"
fi
```

If no `release` branch exists, skip this step silently — the project hasn't adopted the trunk+release model yet.

### 7. Offer to push

Ask the user if they want to push. Before pushing, always fetch and integrate upstream to avoid rejected pushes:

```bash
# Fetch upstream to detect divergence before pushing
git fetch origin

# Rebase trunk onto upstream to incorporate any changes that landed since the release was prepared
TRUNK_UPSTREAM="origin/$TRUNK"
if ! git merge-base --is-ancestor "$TRUNK_UPSTREAM" HEAD; then
  echo "Trunk has diverged from upstream. Rebasing..."
  git rebase "$TRUNK_UPSTREAM" || {
    echo "Rebase conflict — resolve before pushing."
    git rebase --abort
    exit 1
  }
fi

# If release branch was updated, rebase it too
if git rev-parse --verify release >/dev/null 2>&1; then
  RELEASE_UPSTREAM="origin/release"
  if git rev-parse --verify "$RELEASE_UPSTREAM" >/dev/null 2>&1; then
    if ! git merge-base --is-ancestor "$RELEASE_UPSTREAM" release; then
      echo "Release branch has diverged from upstream. Rebasing..."
      git checkout release
      git rebase "$RELEASE_UPSTREAM" || {
        echo "Rebase conflict on release — resolve before pushing."
        git rebase --abort
        git checkout "$TRUNK"
        exit 1
      }
      git checkout "$TRUNK"
    fi
  fi
fi
```

If a release branch was updated in step 6.5:

```bash
git push origin "$TRUNK" && git push origin release && git push origin <tag>
```

If no release branch exists, push as before:

```bash
git push && git push origin <tag>
```

Push only the specific tag — `git push --tags` tries to push every local tag and produces noisy rejections for tags that already exist on the remote.

Don't push without asking — the user may want to review first, or they may have a CI pipeline that triggers on tags.

## Edge cases

**Monorepo with multiple version streams:** If the tag history suggests per-package tags (e.g., `frontend-v1.2.0`, `api-v3.1.0`), ask the user which package they're releasing rather than assuming.

**Pre-release versions:** If the user asks for a pre-release (alpha, beta, rc), append the pre-release suffix to the version: `1.5.0-alpha.1`. Follow the existing convention if prior pre-release tags exist.

**No conventional commits:** If the commit history doesn't use conventional prefixes, don't force the grouping. Present a flat list and let the changelog be a simple bullet list of changes.

**Dirty working tree:** If there are uncommitted changes when `/swain-release` is invoked, warn the user and ask whether to proceed (changes won't be included in the release) or abort so they can commit first.

## Session bookmark

After a successful release, update the bookmark: `bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" "Released v{version}"`
