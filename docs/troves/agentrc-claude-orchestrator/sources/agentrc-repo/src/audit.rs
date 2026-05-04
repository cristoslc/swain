use std::path::Path;

use anyhow::{Context, Result};

use crate::commands::spawn::{find_task_brief, load_task_brief};
use crate::events;
use crate::fs::bus::OrchestratorPaths;
use crate::git::wrapper::Git;
use crate::model::error::AppError;
use crate::model::event::EventType;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CommitKind {
    Test,
    Impl,
    Mixed,
}

/// Classify a commit based on its changed file paths.
pub fn classify_commit(files: &[String]) -> CommitKind {
    let has_test = files.iter().any(|f| f.starts_with("tests/"));
    let has_impl = files.iter().any(|f| f.starts_with("src/"));

    match (has_test, has_impl) {
        (true, true) => CommitKind::Mixed,
        (true, false) => CommitKind::Test,
        _ => CommitKind::Impl,
    }
}

#[derive(Debug, Clone)]
pub struct TddAudit {
    pub task_id: String,
    pub total_commits: usize,
    pub test_commits: usize,
    pub impl_commits: usize,
    pub mixed_commits: usize,
    pub compliant: bool,
    pub score: String,
}

pub fn audit_tdd(project_root: &Path, task_id: &str) -> Result<TddAudit> {
    let paths = OrchestratorPaths::new(project_root);
    let run = paths.active_run().ok_or(AppError::NoActiveRun)?;

    // Load the task brief to get branch info
    let brief_path = find_task_brief(&run, task_id)?;
    let brief = load_task_brief(&brief_path)?;

    let branch = brief
        .branch
        .as_deref()
        .context("task brief has no branch field")?;
    let base = &brief.base_branch;

    // Get commits with files
    let git = Git::new(project_root);
    let commits = git.log_commits_with_files(branch, base)?;

    let total_commits = commits.len();
    let mut test_commits = 0usize;
    let mut impl_commits = 0usize;
    let mut mixed_commits = 0usize;

    for (_subject, files) in &commits {
        match classify_commit(files) {
            CommitKind::Test => test_commits += 1,
            CommitKind::Impl => impl_commits += 1,
            CommitKind::Mixed => mixed_commits += 1,
        }
    }

    let compliant = test_commits > 0;
    let score = format!("{test_commits}/{total_commits} test commits");

    // Emit TddViolation event if not compliant
    if !compliant {
        let msg = format!("TDD violation on task {task_id}: {score} — no test-first commits found");
        events::emit_warn(project_root, EventType::TddViolation, Some(task_id), &msg)?;
    }

    Ok(TddAudit {
        task_id: task_id.to_string(),
        total_commits,
        test_commits,
        impl_commits,
        mixed_commits,
        compliant,
        score,
    })
}
