use std::path::PathBuf;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("config not found: {path}")]
    ConfigNotFound { path: PathBuf },

    #[error("no active run (missing .orchestrator/active symlink)")]
    NoActiveRun,

    #[error("run already active: {run_id}")]
    RunAlreadyActive { run_id: String },

    #[error("task not found: {task_id}")]
    TaskNotFound { task_id: String },

    #[error("invalid state transition: {from} -> {to}")]
    InvalidStateTransition { from: String, to: String },

    #[error("task brief parse error in {path}: {reason}")]
    TaskBriefParseError { path: PathBuf, reason: String },

    #[error("status parse error in {path}: {reason}")]
    StatusParseError { path: PathBuf, reason: String },

    #[error("dirty base branch: uncommitted changes detected")]
    DirtyBaseBranch,

    #[error("worktree already exists: {path}")]
    WorktreeExists { path: PathBuf },

    #[error("branch already exists: {branch}")]
    BranchExists { branch: String },

    #[error("tmux error: {message}")]
    TmuxError { message: String },

    #[error("git error: {message}")]
    GitError { message: String },

    #[error("max redispatch attempts ({max}) reached for task {task_id}")]
    MaxRedispatchReached { task_id: String, max: u32 },

    #[error("merge conflict in task {task_id}: {files}")]
    MergeConflict { task_id: String, files: String },

    #[error("test failure after merging task {task_id}")]
    TestFailure { task_id: String },

    #[error("orchestrator not initialized (run `agentrc init` first)")]
    NotInitialized,

    #[error("amend requires either --brief or --message")]
    AmendSourceRequired,
}
