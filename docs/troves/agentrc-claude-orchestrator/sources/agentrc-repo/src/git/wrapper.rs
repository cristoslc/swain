use anyhow::{bail, Context, Result};
use std::path::{Path, PathBuf};
use std::process::Command;

/// Typed wrapper around git CLI commands.
pub struct Git {
    repo_path: PathBuf,
}

impl Git {
    /// Create a new Git wrapper for the repository at `repo_path`.
    pub fn new(repo_path: &Path) -> Self {
        Self {
            repo_path: repo_path.to_path_buf(),
        }
    }

    /// Run a git command with the given args in the context of this repo.
    /// Returns trimmed stdout on success, or an error with stderr on failure.
    fn run_git(&self, args: &[&str]) -> Result<String> {
        let output = Command::new("git")
            .arg("-C")
            .arg(&self.repo_path)
            .args(args)
            .output()
            .context("failed to execute git")?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            bail!(
                "git {} failed (exit {}): {}",
                args.join(" "),
                output.status,
                stderr.trim()
            );
        }

        let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
        Ok(stdout)
    }

    /// Returns true if the working tree is clean (no uncommitted changes).
    pub fn is_clean(&self) -> Result<bool> {
        let output = self.run_git(&["status", "--porcelain"])?;
        Ok(output.is_empty())
    }

    /// Returns the name of the current branch.
    pub fn current_branch(&self) -> Result<String> {
        self.run_git(&["rev-parse", "--abbrev-ref", "HEAD"])
    }

    /// Checkout the given branch.
    pub fn checkout(&self, branch: &str) -> Result<()> {
        self.run_git(&["checkout", branch])?;
        Ok(())
    }

    /// Create a new worktree at `path` on a new branch `branch` starting from `base`.
    pub fn create_worktree(&self, path: &Path, branch: &str, base: &str) -> Result<()> {
        let path_str = path.to_str().context("worktree path is not valid UTF-8")?;
        self.run_git(&["worktree", "add", path_str, "-b", branch, base])?;
        Ok(())
    }

    /// Create a worktree checked out on an existing branch.
    pub fn create_worktree_from_branch(&self, path: &Path, branch: &str) -> Result<()> {
        let path_str = path.to_str().context("worktree path is not valid UTF-8")?;
        self.run_git(&["worktree", "add", path_str, branch])?;
        Ok(())
    }

    /// Remove the worktree at `path` (forcefully).
    pub fn remove_worktree(&self, path: &Path) -> Result<()> {
        let path_str = path.to_str().context("worktree path is not valid UTF-8")?;
        self.run_git(&["worktree", "remove", path_str, "--force"])?;
        Ok(())
    }

    /// List worktree paths by parsing `git worktree list --porcelain`.
    pub fn list_worktrees(&self) -> Result<Vec<String>> {
        let output = self.run_git(&["worktree", "list", "--porcelain"])?;
        let paths = output
            .lines()
            .filter_map(|line| line.strip_prefix("worktree "))
            .map(|s| s.to_string())
            .collect();
        Ok(paths)
    }

    /// Get the commit hash for a ref.
    pub fn rev_parse(&self, rev: &str) -> Result<String> {
        self.run_git(&["rev-parse", "--short", rev])
    }

    /// Returns true if a branch with the given name exists.
    pub fn branch_exists(&self, branch: &str) -> Result<bool> {
        let refspec = format!("refs/heads/{}", branch);
        match self.run_git(&["rev-parse", "--verify", &refspec]) {
            Ok(_) => Ok(true),
            Err(_) => Ok(false),
        }
    }

    /// Merge the given branch with --no-ff.
    pub fn merge_no_ff(&self, branch: &str) -> Result<()> {
        let msg = format!("Merge branch '{branch}'");
        self.run_git(&["merge", "--no-ff", branch, "-m", &msg])?;
        Ok(())
    }

    /// Abort an in-progress merge.
    pub fn merge_abort(&self) -> Result<()> {
        self.run_git(&["merge", "--abort"])?;
        Ok(())
    }

    /// Reset the current branch hard by `count` commits.
    pub fn reset_hard_head(&self, count: u32) -> Result<()> {
        let refspec = format!("HEAD~{count}");
        self.run_git(&["reset", "--hard", &refspec])?;
        Ok(())
    }

    /// Stage all changes.
    pub fn add_all(&self) -> Result<()> {
        self.run_git(&["add", "-A"])?;
        Ok(())
    }

    /// Create a commit with the given message.
    pub fn commit(&self, message: &str) -> Result<()> {
        self.run_git(&["commit", "-m", message])?;
        Ok(())
    }

    /// Return the last `count` log entries in oneline format for the given ref.
    pub fn log_oneline(&self, ref_name: &str, count: usize) -> Result<Vec<String>> {
        let count_arg = format!("-{count}");
        let output = self.run_git(&["log", "--oneline", &count_arg, ref_name])?;
        let lines = output.lines().map(|s| s.to_string()).collect();
        Ok(lines)
    }

    /// Return oneline log of commits in `branch` that are not in `base`.
    pub fn log_branch_commits(&self, branch: &str, base: &str) -> Result<Vec<String>> {
        let range = format!("{base}..{branch}");
        let output = self.run_git(&["log", "--oneline", &range])?;
        let lines = output.lines().map(|s| s.to_string()).collect();
        Ok(lines)
    }

    /// Show the files changed in a given commit.
    pub fn show_files_changed(&self, commit: &str) -> Result<Vec<String>> {
        let output = self.run_git(&["show", "--name-only", "--format=", commit])?;
        let files = output
            .lines()
            .filter(|l| !l.is_empty())
            .map(|s| s.to_string())
            .collect();
        Ok(files)
    }

    /// Return files changed between `base` and `branch` (`git diff --name-only base..branch`).
    pub fn changed_files(&self, base: &str, branch: &str) -> Result<Vec<String>> {
        let range = format!("{base}..{branch}");
        let output = self.run_git(&["diff", "--name-only", &range])?;
        let files = output
            .lines()
            .filter(|l| !l.is_empty())
            .map(|s| s.to_string())
            .collect();
        Ok(files)
    }

    /// Return files with unresolved merge conflicts (`git diff --name-only --diff-filter=U`).
    pub fn conflicting_files(&self) -> Result<Vec<String>> {
        let output = self.run_git(&["diff", "--name-only", "--diff-filter=U"])?;
        let files = output
            .lines()
            .filter(|l| !l.is_empty())
            .map(|s| s.to_string())
            .collect();
        Ok(files)
    }

    /// Return commits between `base` and `branch` with their changed files.
    /// Each entry is `(commit_subject, Vec<file_path>)`.
    pub fn log_commits_with_files(
        &self,
        branch: &str,
        base: &str,
    ) -> Result<Vec<(String, Vec<String>)>> {
        let range = format!("{base}..{branch}");
        let output = self.run_git(&["log", "--format=%H %s", "--name-only", &range])?;

        let mut result: Vec<(String, Vec<String>)> = Vec::new();
        let mut current_subject: Option<String> = None;
        let mut current_files: Vec<String> = Vec::new();

        for line in output.lines() {
            if line.is_empty() {
                continue;
            }
            // Lines starting with a commit hash (40 hex chars + space + subject)
            // vs file paths
            if line.len() > 41
                && line.chars().take(40).all(|c| c.is_ascii_hexdigit())
                && line.as_bytes()[40] == b' '
            {
                // Push previous commit if any
                if let Some(subject) = current_subject.take() {
                    result.push((subject, std::mem::take(&mut current_files)));
                }
                current_subject = Some(line[41..].to_string());
            } else {
                current_files.push(line.to_string());
            }
        }
        // Push the last commit
        if let Some(subject) = current_subject {
            result.push((subject, current_files));
        }

        Ok(result)
    }

    /// Detect the default branch: prefer "main", then "master", then current branch.
    pub fn detect_default_branch(&self) -> Result<String> {
        if self.branch_exists("main")? {
            return Ok("main".to_string());
        }
        if self.branch_exists("master")? {
            return Ok("master".to_string());
        }
        self.current_branch()
    }
}
