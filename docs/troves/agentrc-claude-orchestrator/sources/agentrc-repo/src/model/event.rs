use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct OrcEvent {
    pub timestamp: DateTime<Utc>,
    pub event_type: EventType,
    pub task_id: Option<String>,
    pub severity: Severity,
    pub message: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EventType {
    Spawned,
    StateChange,
    Completed,
    Failed,
    MergeStarted,
    MergeSuccess,
    MergeConflict,
    MergeTestFail,
    Respawned,
    Dead,
    StaleHeartbeat,
    NeedsInput,
    RateLimited,
    CascadeSpawn,
    InputResponded,
    CheckpointSaved,
    VoltagentViolation,
    TddViolation,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Severity {
    Info,
    Warn,
    Error,
}
