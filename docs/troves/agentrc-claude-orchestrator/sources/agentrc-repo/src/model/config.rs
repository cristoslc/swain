use serde::{Deserialize, Serialize};
use std::path::PathBuf;

fn default_max_workers() -> u32 {
    12
}

fn default_workers_per_window() -> u32 {
    4
}

fn default_heartbeat_interval_sec() -> u64 {
    30
}

fn default_heartbeat_timeout_sec() -> u64 {
    120
}

fn default_max_redispatch_attempts() -> u32 {
    2
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrchestratorConfig {
    pub project_root: PathBuf,

    #[serde(default = "default_base_branch")]
    pub base_branch: String,

    #[serde(default = "default_max_workers")]
    pub max_workers: u32,

    #[serde(default = "default_workers_per_window")]
    pub workers_per_window: u32,

    #[serde(default = "default_heartbeat_interval_sec")]
    pub heartbeat_interval_sec: u64,

    #[serde(default = "default_heartbeat_timeout_sec")]
    pub heartbeat_timeout_sec: u64,

    #[serde(default = "default_max_redispatch_attempts")]
    pub max_redispatch_attempts: u32,

    #[serde(default)]
    pub test_command: Option<String>,

    #[serde(default)]
    pub worker_claude_args: Vec<String>,
}

fn default_base_branch() -> String {
    "main".into()
}

impl Default for OrchestratorConfig {
    fn default() -> Self {
        Self {
            project_root: PathBuf::from("."),
            base_branch: default_base_branch(),
            max_workers: default_max_workers(),
            workers_per_window: default_workers_per_window(),
            heartbeat_interval_sec: default_heartbeat_interval_sec(),
            heartbeat_timeout_sec: default_heartbeat_timeout_sec(),
            max_redispatch_attempts: default_max_redispatch_attempts(),
            test_command: None,
            worker_claude_args: Vec::new(),
        }
    }
}
