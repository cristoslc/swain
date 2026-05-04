mod common;

use agentrc::commands::amend;
use agentrc::commands::spawn;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::model::task::{TaskState, TaskStatus};
use tempfile::TempDir;

/// Set up a run with a task brief and initial status file.
fn setup_run_with_task() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    agentrc::commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    agentrc::commands::run::create_in(tmp.path(), "test-run").unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let brief = r#"---
id: "001"
slug: add-login
classification: writer
worktree: .orchestrator/active/worktrees/001
base_branch: HEAD
branch: orc/001-add-login
pane_id: "%99"
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task 001: Add login

Build the login page.
"#;
    std::fs::write(active.task_brief("001", "add-login"), brief).unwrap();

    // Write initial status with pane_id
    spawn::write_initial_status(tmp.path(), "001").unwrap();
    let status_file = active.status_file("001");
    let content = std::fs::read_to_string(&status_file).unwrap();
    let mut status: TaskStatus = serde_json::from_str(&content).unwrap();
    status.pane_id = Some("%99".to_string());
    status.state = TaskState::InProgress;
    let json = serde_json::to_string_pretty(&status).unwrap();
    std::fs::write(&status_file, json).unwrap();

    (tmp, paths)
}

fn read_status(paths: &OrchestratorPaths, task_id: &str) -> TaskStatus {
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file(task_id)).unwrap();
    serde_json::from_str(&content).unwrap()
}

fn read_brief(paths: &OrchestratorPaths, task_id: &str, slug: &str) -> String {
    let active = paths.active_run().unwrap();
    std::fs::read_to_string(active.task_brief(task_id, slug)).unwrap()
}

// ── Test 1: Amend with --brief replaces body, preserves system frontmatter ──

#[test]
fn amend_with_brief_replaces_body_preserves_frontmatter() {
    let (tmp, paths) = setup_run_with_task();

    // Write a replacement brief file
    let new_brief = r#"---
id: "001"
slug: add-login
classification: writer
base_branch: HEAD
depends_on: []
created_at: 2020-01-01T00:00:00Z
---

# Task 001: Updated task

New body content.
"#;
    let new_brief_path = tmp.path().join("updated-brief.md");
    std::fs::write(&new_brief_path, new_brief).unwrap();

    amend::run_in(
        tmp.path(),
        "001",
        Some(new_brief_path.to_str().unwrap()),
        None,
    )
    .unwrap();

    let content = read_brief(&paths, "001", "add-login");

    // Body should be replaced
    assert!(
        content.contains("New body content."),
        "body should be replaced with new content"
    );
    assert!(
        !content.contains("Build the login page."),
        "old body should be gone"
    );

    // System frontmatter fields should be preserved from the ORIGINAL brief
    assert!(content.contains("pane_id:"), "pane_id should be preserved");
    assert!(
        content.contains("%99"),
        "pane_id value should be preserved from original"
    );
    assert!(
        content.contains("worktree:"),
        "worktree should be preserved"
    );
    assert!(
        content.contains("2026-04-11"),
        "created_at should be preserved from original"
    );
}

// ── Test 2: Amend with --message appends amendment section ──

#[test]
fn amend_with_message_appends_amendment_section() {
    let (tmp, paths) = setup_run_with_task();

    amend::run_in(tmp.path(), "001", None, Some("Change scope to include X")).unwrap();

    let content = read_brief(&paths, "001", "add-login");

    // Original content preserved
    assert!(
        content.contains("Build the login page."),
        "original body should still be present"
    );

    // Amendment appended
    assert!(
        content.contains("## Amendment"),
        "should have Amendment heading"
    );
    assert!(
        content.contains("Change scope to include X"),
        "should contain amendment text"
    );
}

// ── Test 3: Redispatch count incremented ──

#[test]
fn amend_increments_redispatch_count() {
    let (tmp, paths) = setup_run_with_task();

    let status_before = read_status(&paths, "001");
    assert_eq!(status_before.redispatch_count, 0);

    amend::run_in(tmp.path(), "001", None, Some("First amendment")).unwrap();

    let status_after = read_status(&paths, "001");
    assert_eq!(status_after.redispatch_count, 1);
}

// ── Test 4: Max redispatch exceeded ──

#[test]
fn amend_errors_when_max_redispatch_exceeded() {
    let (tmp, paths) = setup_run_with_task();

    // Set redispatch_count to the max (default max_redispatch_attempts = 2)
    let active = paths.active_run().unwrap();
    let status_file = active.status_file("001");
    let content = std::fs::read_to_string(&status_file).unwrap();
    let mut status: TaskStatus = serde_json::from_str(&content).unwrap();
    status.redispatch_count = 2;
    let json = serde_json::to_string_pretty(&status).unwrap();
    std::fs::write(&status_file, json).unwrap();

    let result = amend::run_in(tmp.path(), "001", None, Some("Too many amendments"));

    assert!(result.is_err());
    let err_msg = result.unwrap_err().to_string();
    assert!(
        err_msg.contains("max redispatch"),
        "error should mention max redispatch: {err_msg}"
    );
}

// ── Test 5: Pane notification (tmux send-keys called) ──
// NOTE: We can't test actual tmux send-keys in unit tests without a running
// tmux server. Instead we verify the amend succeeds when pane_id is set,
// and the actual tmux notification is a best-effort operation.
// The integration is tested by the fact that amend doesn't error when pane_id exists.

#[test]
fn amend_succeeds_when_pane_is_set() {
    let (tmp, _paths) = setup_run_with_task();

    // Task has pane_id "%99" — amend should succeed (send-keys is best-effort)
    let result = amend::run_in(tmp.path(), "001", None, Some("Update with pane alive"));

    assert!(
        result.is_ok(),
        "amend should succeed even with pane_id set: {:?}",
        result.err()
    );
}

// ── Test 6: No pane (completed task) — amend succeeds without send-keys ──

#[test]
fn amend_succeeds_without_pane() {
    let (tmp, paths) = setup_run_with_task();

    // Remove pane_id from status
    let active = paths.active_run().unwrap();
    let status_file = active.status_file("001");
    let content = std::fs::read_to_string(&status_file).unwrap();
    let mut status: TaskStatus = serde_json::from_str(&content).unwrap();
    status.pane_id = None;
    let json = serde_json::to_string_pretty(&status).unwrap();
    std::fs::write(&status_file, json).unwrap();

    let result = amend::run_in(tmp.path(), "001", None, Some("Amendment without pane"));

    assert!(
        result.is_ok(),
        "amend should succeed without pane_id: {:?}",
        result.err()
    );

    // Verify the brief was still amended
    let brief = read_brief(&paths, "001", "add-login");
    assert!(brief.contains("Amendment without pane"));
}

// ── Test 7: Missing task — returns TaskNotFound ──

#[test]
fn amend_errors_for_nonexistent_task() {
    let (tmp, _paths) = setup_run_with_task();

    let result = amend::run_in(tmp.path(), "999", None, Some("This task doesn't exist"));

    assert!(result.is_err());
    let err_msg = result.unwrap_err().to_string();
    assert!(
        err_msg.contains("task not found") || err_msg.contains("999"),
        "error should indicate task not found: {err_msg}"
    );
}

// ── Test 8: Neither flag provided — returns AmendSourceRequired ──

#[test]
fn amend_errors_when_neither_flag_provided() {
    let (tmp, _paths) = setup_run_with_task();

    let result = amend::run_in(tmp.path(), "001", None, None);

    assert!(result.is_err());
    let err_msg = result.unwrap_err().to_string();
    assert!(
        err_msg.contains("--brief") || err_msg.contains("--message"),
        "error should mention --brief or --message: {err_msg}"
    );
}
