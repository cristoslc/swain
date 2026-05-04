use agentrc::model::error::AppError;

#[test]
fn app_error_displays_correctly() {
    let err = AppError::ConfigNotFound {
        path: "/tmp/.orchestrator/config.json".into(),
    };
    assert_eq!(
        err.to_string(),
        "config not found: /tmp/.orchestrator/config.json"
    );
}

#[test]
fn app_error_no_active_run() {
    let err = AppError::NoActiveRun;
    assert_eq!(
        err.to_string(),
        "no active run (missing .orchestrator/active symlink)"
    );
}

#[test]
fn app_error_invalid_state_transition() {
    let err = AppError::InvalidStateTransition {
        from: "completed".into(),
        to: "in_progress".into(),
    };
    let msg = err.to_string();
    assert!(
        msg.contains("completed"),
        "should contain 'completed': {msg}"
    );
    assert!(
        msg.contains("in_progress"),
        "should contain 'in_progress': {msg}"
    );
}

#[test]
fn app_error_max_redispatch_reached() {
    let err = AppError::MaxRedispatchReached {
        task_id: "003".into(),
        max: 2,
    };
    assert_eq!(
        err.to_string(),
        "max redispatch attempts (2) reached for task 003"
    );
}

#[test]
fn app_error_merge_conflict() {
    let err = AppError::MergeConflict {
        task_id: "001".into(),
        files: "src/main.rs".into(),
    };
    assert_eq!(err.to_string(), "merge conflict in task 001: src/main.rs");
}

#[test]
fn app_error_not_initialized() {
    let err = AppError::NotInitialized;
    let msg = err.to_string();
    assert_eq!(
        msg,
        "orchestrator not initialized (run `agentrc init` first)"
    );
    assert!(
        msg.contains("agentrc init"),
        "should include init hint: {msg}"
    );
}

// ── Part A: OrchestratorConfig ──────────────────────────────────────────────

use agentrc::model::config::OrchestratorConfig;

#[test]
fn config_default_values() {
    let config = OrchestratorConfig::default();
    assert_eq!(config.max_workers, 12);
    assert_eq!(config.workers_per_window, 4);
    assert_eq!(config.heartbeat_interval_sec, 30);
    assert_eq!(config.heartbeat_timeout_sec, 120);
    assert_eq!(config.max_redispatch_attempts, 2);
    assert!(config.test_command.is_none());
    assert!(config.worker_claude_args.is_empty());
}

#[test]
fn config_json_roundtrip() {
    let config = OrchestratorConfig {
        project_root: "/home/eric/Code/foo".into(),
        base_branch: "main".into(),
        max_workers: 8,
        workers_per_window: 4,
        heartbeat_interval_sec: 30,
        heartbeat_timeout_sec: 120,
        max_redispatch_attempts: 2,
        test_command: Some("cargo test".into()),
        worker_claude_args: vec!["--model".into(), "sonnet".into()],
    };
    let json = serde_json::to_string_pretty(&config).unwrap();
    let deserialized: OrchestratorConfig = serde_json::from_str(&json).unwrap();
    assert_eq!(
        deserialized.project_root.to_str().unwrap(),
        "/home/eric/Code/foo"
    );
    assert_eq!(deserialized.test_command.as_deref(), Some("cargo test"));
    assert_eq!(deserialized.max_workers, 8);
}

// ── Part B: TaskState, Classification, TaskStatus, TaskBriefFrontmatter ─────

use agentrc::model::task::{
    Classification, PhaseEntry, TaskBriefFrontmatter, TaskState, TaskStatus,
};

#[test]
fn task_state_serializes_as_lowercase() {
    let state = TaskState::InProgress;
    let json = serde_json::to_string(&state).unwrap();
    assert_eq!(json, "\"in_progress\"");
}

#[test]
fn task_state_deserializes_from_lowercase() {
    let state: TaskState = serde_json::from_str("\"in_progress\"").unwrap();
    assert_eq!(state, TaskState::InProgress);
}

#[test]
fn classification_serializes_as_lowercase() {
    let c = Classification::Writer;
    let json = serde_json::to_string(&c).unwrap();
    assert_eq!(json, "\"writer\"");
}

#[test]
fn task_status_json_roundtrip() {
    let status = TaskStatus {
        id: "001".into(),
        pane_id: Some("%12".into()),
        pane_title: None,
        state: TaskState::InProgress,
        phase: Some("implementing".into()),
        started_at: Some(chrono::Utc::now()),
        updated_at: chrono::Utc::now(),
        last_message: Some("tests passing".into()),
        result_path: None,
        branch: Some("orc/001-add-login".into()),
        redispatch_count: 0,
        phase_history: vec![],
        token_usage: None,
    };
    let json = serde_json::to_string_pretty(&status).unwrap();
    let deserialized: TaskStatus = serde_json::from_str(&json).unwrap();
    assert_eq!(deserialized.id, "001");
    assert_eq!(deserialized.state, TaskState::InProgress);
    assert_eq!(deserialized.phase.as_deref(), Some("implementing"));
}

#[test]
fn task_state_valid_transitions() {
    assert!(TaskState::Spawning.can_transition_to(&TaskState::Ready));
    assert!(TaskState::Ready.can_transition_to(&TaskState::InProgress));
    assert!(TaskState::InProgress.can_transition_to(&TaskState::Completed));
    assert!(TaskState::InProgress.can_transition_to(&TaskState::Failed));
    assert!(TaskState::InProgress.can_transition_to(&TaskState::Blocked));
    assert!(TaskState::Blocked.can_transition_to(&TaskState::InProgress));
    assert!(!TaskState::Completed.can_transition_to(&TaskState::InProgress));
    assert!(!TaskState::Failed.can_transition_to(&TaskState::InProgress));
}

#[test]
fn task_brief_frontmatter_from_yaml() {
    let yaml = r#"
id: "001"
slug: add-login-endpoint
classification: writer
worktree: .orchestrator/active/worktrees/001
base_branch: main
branch: orc/001-add-login-endpoint
pane_id: null
depends_on: []
created_at: 2026-04-11T14:30:00Z
"#;
    let brief: TaskBriefFrontmatter = serde_yaml::from_str(yaml).unwrap();
    assert_eq!(brief.id, "001");
    assert_eq!(brief.slug, "add-login-endpoint");
    assert_eq!(brief.classification, Classification::Writer);
    assert!(brief.pane_id.is_none());
    assert!(brief.depends_on.is_empty());
}

#[test]
fn task_brief_frontmatter_reader_no_worktree() {
    let yaml = r#"
id: "002"
slug: review-deps
classification: reader
base_branch: main
depends_on: []
created_at: 2026-04-11T14:30:00Z
"#;
    let brief: TaskBriefFrontmatter = serde_yaml::from_str(yaml).unwrap();
    assert_eq!(brief.classification, Classification::Reader);
    assert!(brief.worktree.is_none());
    assert!(brief.branch.is_none());
}

// ── Phase history ───────────────────────────────────────────────────────────

#[test]
fn backward_compat_old_status_json_without_phase_history() {
    // Old-format JSON without the phase_history field should deserialize with empty vec
    let json = r#"{
        "id": "001",
        "pane_id": null,
        "state": "in_progress",
        "phase": "testing",
        "started_at": "2026-04-12T10:00:00Z",
        "updated_at": "2026-04-12T10:05:00Z",
        "last_message": "running tests",
        "result_path": null,
        "branch": null,
        "redispatch_count": 0
    }"#;
    let status: TaskStatus = serde_json::from_str(json).unwrap();
    assert!(status.phase_history.is_empty());
    assert_eq!(status.id, "001");
    assert_eq!(status.state, TaskState::InProgress);
}

#[test]
fn phase_entry_serializes_correctly() {
    let entry = PhaseEntry {
        phase: "testing".into(),
        entered_at: chrono::DateTime::parse_from_rfc3339("2026-04-12T10:00:00Z")
            .unwrap()
            .with_timezone(&chrono::Utc),
    };
    let json = serde_json::to_string(&entry).unwrap();
    assert!(json.contains("testing"));
    assert!(json.contains("2026-04-12"));
}

#[test]
fn status_with_phase_history_roundtrips() {
    let status = TaskStatus {
        id: "001".into(),
        pane_id: None,
        pane_title: None,
        state: TaskState::InProgress,
        phase: Some("testing".into()),
        started_at: Some(chrono::Utc::now()),
        updated_at: chrono::Utc::now(),
        last_message: None,
        result_path: None,
        branch: None,
        redispatch_count: 0,
        phase_history: vec![
            PhaseEntry {
                phase: "spawning".into(),
                entered_at: chrono::Utc::now(),
            },
            PhaseEntry {
                phase: "testing".into(),
                entered_at: chrono::Utc::now(),
            },
        ],
        token_usage: None,
    };
    let json = serde_json::to_string_pretty(&status).unwrap();
    let deserialized: TaskStatus = serde_json::from_str(&json).unwrap();
    assert_eq!(deserialized.phase_history.len(), 2);
    assert_eq!(deserialized.phase_history[0].phase, "spawning");
    assert_eq!(deserialized.phase_history[1].phase, "testing");
}

// ── Pane title backward compat ──────────────────────────────────────────────

#[test]
fn pane_title_backward_compat_old_status_json() {
    // Old-format JSON without pane_title field should deserialize with None
    let json = r#"{
        "id": "001",
        "pane_id": "%28",
        "state": "in_progress",
        "phase": "testing",
        "started_at": "2026-04-12T10:00:00Z",
        "updated_at": "2026-04-12T10:05:00Z",
        "last_message": "running tests",
        "result_path": null,
        "branch": null,
        "redispatch_count": 0
    }"#;
    let status: TaskStatus = serde_json::from_str(json).unwrap();
    assert!(status.pane_title.is_none());
    assert_eq!(status.pane_id.as_deref(), Some("%28"));
}

#[test]
fn pane_title_roundtrips_when_present() {
    let status = TaskStatus {
        id: "001".into(),
        pane_id: Some("%28".into()),
        pane_title: Some("orc:001:add-login".into()),
        state: TaskState::InProgress,
        phase: Some("implementing".into()),
        started_at: Some(chrono::Utc::now()),
        updated_at: chrono::Utc::now(),
        last_message: None,
        result_path: None,
        branch: None,
        redispatch_count: 0,
        phase_history: vec![],
        token_usage: None,
    };
    let json = serde_json::to_string_pretty(&status).unwrap();
    let deserialized: TaskStatus = serde_json::from_str(&json).unwrap();
    assert_eq!(
        deserialized.pane_title.as_deref(),
        Some("orc:001:add-login")
    );
}

// ── Part C: RunMetadata ─────────────────────────────────────────────────────

use agentrc::model::run::RunMetadata;

#[test]
fn run_metadata_generates_id_from_slug() {
    let meta = RunMetadata::new("auth-refactor");
    assert!(meta.id.contains("auth-refactor"));
    assert!(meta.id.starts_with("20"));
    assert!(meta.id.contains('T'));
}

#[test]
fn run_metadata_id_is_filesystem_safe() {
    let meta = RunMetadata::new("fix weird/bug:thing");
    assert!(!meta.id.contains(':'));
    assert!(!meta.id.contains('/'));
    assert!(!meta.id.contains(' '));
}
