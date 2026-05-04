use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::fmt;
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct PhaseEntry {
    pub phase: String,
    pub entered_at: DateTime<Utc>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TaskState {
    Spawning,
    Ready,
    InProgress,
    Blocked,
    Completed,
    Failed,
    Aborted,
}

impl TaskState {
    pub fn can_transition_to(&self, target: &TaskState) -> bool {
        matches!(
            (self, target),
            (TaskState::Spawning, TaskState::Ready)
                | (TaskState::Spawning, TaskState::Failed)
                | (TaskState::Spawning, TaskState::Aborted)
                | (TaskState::Ready, TaskState::InProgress)
                | (TaskState::Ready, TaskState::Aborted)
                | (TaskState::InProgress, TaskState::Completed)
                | (TaskState::InProgress, TaskState::Failed)
                | (TaskState::InProgress, TaskState::Blocked)
                | (TaskState::InProgress, TaskState::Aborted)
                | (TaskState::Blocked, TaskState::InProgress)
                | (TaskState::Blocked, TaskState::Aborted)
                | (TaskState::Blocked, TaskState::Failed)
        )
    }
}

impl fmt::Display for TaskState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TaskState::Spawning => write!(f, "spawning"),
            TaskState::Ready => write!(f, "ready"),
            TaskState::InProgress => write!(f, "in_progress"),
            TaskState::Blocked => write!(f, "blocked"),
            TaskState::Completed => write!(f, "completed"),
            TaskState::Failed => write!(f, "failed"),
            TaskState::Aborted => write!(f, "aborted"),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Classification {
    Reader,
    Writer,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskStatus {
    pub id: String,
    pub pane_id: Option<String>,
    #[serde(default)]
    pub pane_title: Option<String>,
    pub state: TaskState,
    pub phase: Option<String>,
    pub started_at: Option<DateTime<Utc>>,
    pub updated_at: DateTime<Utc>,
    pub last_message: Option<String>,
    pub result_path: Option<PathBuf>,
    pub branch: Option<String>,
    #[serde(default)]
    pub redispatch_count: u32,
    #[serde(default)]
    pub phase_history: Vec<PhaseEntry>,
    #[serde(default)]
    pub token_usage: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskBriefFrontmatter {
    pub id: String,
    pub slug: String,
    pub classification: Classification,
    pub worktree: Option<PathBuf>,
    pub base_branch: String,
    pub branch: Option<String>,
    pub pane_id: Option<String>,
    #[serde(default)]
    pub depends_on: Vec<String>,
    pub created_at: DateTime<Utc>,
}
