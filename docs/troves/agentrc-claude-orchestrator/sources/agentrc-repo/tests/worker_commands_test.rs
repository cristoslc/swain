mod common;

use std::time::Duration;

use agentrc::commands::worker;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::model::task::{TaskState, TaskStatus};
use tempfile::TempDir;

fn setup_active_run() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    agentrc::commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    agentrc::commands::run::create_in(tmp.path(), "test-run").unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    (tmp, paths)
}

#[test]
fn worker_status_creates_initial_status_file() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "spawning", None, None, None).unwrap();
    let active = paths.active_run().unwrap();
    let status_file = active.status_file("001");
    assert!(status_file.exists());
    let content = std::fs::read_to_string(&status_file).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.id, "001");
    assert_eq!(status.state, TaskState::Spawning);
}

#[test]
fn worker_status_updates_existing_status() {
    let (tmp, _paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "spawning", None, None, None).unwrap();
    worker::status::run_in(
        tmp.path(),
        "001",
        "in_progress",
        Some("implementing"),
        Some("writing tests"),
        None,
    )
    .unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.state, TaskState::InProgress);
    assert_eq!(status.phase.as_deref(), Some("implementing"));
    assert_eq!(status.last_message.as_deref(), Some("writing tests"));
}

#[test]
fn worker_status_validates_state_string() {
    let (tmp, _) = setup_active_run();
    let result = worker::status::run_in(tmp.path(), "001", "invalid_state", None, None, None);
    assert!(result.is_err());
}

#[test]
fn worker_status_sets_started_at_on_first_in_progress() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "spawning", None, None, None).unwrap();
    worker::status::run_in(tmp.path(), "001", "ready", None, None, None).unwrap();
    worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert!(status.started_at.is_some());
}

#[test]
fn worker_note_creates_file_on_first_note() {
    let (tmp, paths) = setup_active_run();
    worker::note::run_in(tmp.path(), "001", "Starting task").unwrap();
    let active = paths.active_run().unwrap();
    let notes = std::fs::read_to_string(active.notes_file("001")).unwrap();
    assert!(notes.contains("Starting task"));
}

#[test]
fn worker_note_appends_with_timestamp() {
    let (tmp, paths) = setup_active_run();
    worker::note::run_in(tmp.path(), "001", "First note").unwrap();
    worker::note::run_in(tmp.path(), "001", "Second note").unwrap();
    let active = paths.active_run().unwrap();
    let notes = std::fs::read_to_string(active.notes_file("001")).unwrap();
    assert!(notes.contains("First note"));
    assert!(notes.contains("Second note"));
    assert!(notes.contains("202")); // ISO timestamp
    let entry_count = notes.matches("[20").count();
    assert_eq!(entry_count, 2);
}

#[test]
fn worker_result_writes_from_file() {
    let (tmp, paths) = setup_active_run();
    let result_src = tmp.path().join("my-result.md");
    std::fs::write(&result_src, "# Result\n\nAll tests pass.").unwrap();
    worker::result::run_in(tmp.path(), "001", Some(result_src.to_str().unwrap()), false).unwrap();
    let active = paths.active_run().unwrap();
    let result = std::fs::read_to_string(active.result_file("001")).unwrap();
    assert!(result.contains("# Result"));
    assert!(result.contains("All tests pass."));
}

#[test]
fn worker_result_fails_if_file_not_found() {
    let (tmp, _) = setup_active_run();
    let result = worker::result::run_in(tmp.path(), "001", Some("/nonexistent.md"), false);
    assert!(result.is_err());
}

#[test]
fn worker_result_requires_file_or_stdin() {
    let (tmp, _) = setup_active_run();
    let result = worker::result::run_in(tmp.path(), "001", None, false);
    assert!(result.is_err());
}

#[test]
fn worker_heartbeat_creates_alive_file() {
    let (tmp, paths) = setup_active_run();
    worker::heartbeat::tick(tmp.path(), "001").unwrap();
    let active = paths.active_run().unwrap();
    assert!(active.heartbeat_file("001").exists());
}

#[test]
fn worker_heartbeat_updates_mtime() {
    let (tmp, paths) = setup_active_run();
    worker::heartbeat::tick(tmp.path(), "001").unwrap();
    let active = paths.active_run().unwrap();
    let hb_file = active.heartbeat_file("001");
    let mtime1 = std::fs::metadata(&hb_file).unwrap().modified().unwrap();
    std::thread::sleep(Duration::from_millis(50));
    worker::heartbeat::tick(tmp.path(), "001").unwrap();
    let mtime2 = std::fs::metadata(&hb_file).unwrap().modified().unwrap();
    assert!(mtime2 > mtime1);
}

#[test]
fn worker_done_sets_completed_and_writes_result() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    let result_src = tmp.path().join("result.md");
    std::fs::write(&result_src, "# Done\nAll good.").unwrap();
    worker::done::run_in(tmp.path(), "001", Some(result_src.to_str().unwrap())).unwrap();
    let active = paths.active_run().unwrap();
    let status_content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&status_content).unwrap();
    assert_eq!(status.state, TaskState::Completed);
    assert!(status.result_path.is_some());
    let result = std::fs::read_to_string(active.result_file("001")).unwrap();
    assert!(result.contains("All good."));
}

#[test]
fn worker_done_without_result_file() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    worker::done::run_in(tmp.path(), "001", None).unwrap();
    let active = paths.active_run().unwrap();
    let status_content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&status_content).unwrap();
    assert_eq!(status.state, TaskState::Completed);
}

// ── Phase history ───────────────────────────────────────────────────────────

#[test]
fn worker_status_appends_phase_history_entry() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "spawning", None, None, None).unwrap();
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.phase_history.len(), 1);
    assert_eq!(status.phase_history[0].phase, "spawning");
}

#[test]
fn worker_status_preserves_phase_history_across_updates() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "spawning", None, None, None).unwrap();
    worker::status::run_in(
        tmp.path(),
        "001",
        "in_progress",
        Some("testing"),
        None,
        None,
    )
    .unwrap();
    worker::status::run_in(tmp.path(), "001", "completed", Some("done"), None, None).unwrap();
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.phase_history.len(), 3);
    assert_eq!(status.phase_history[0].phase, "spawning");
    assert_eq!(status.phase_history[1].phase, "testing");
    assert_eq!(status.phase_history[2].phase, "done");
}

#[test]
fn worker_status_uses_state_name_when_no_phase() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(tmp.path(), "001", "spawning", None, None, None).unwrap();
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    // When no phase is provided, the state name is used as the phase label
    assert_eq!(status.phase_history[0].phase, "spawning");
}

#[test]
fn worker_status_uses_phase_when_provided() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(
        tmp.path(),
        "001",
        "in_progress",
        Some("implementing"),
        None,
        None,
    )
    .unwrap();
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.phase_history[0].phase, "implementing");
}

#[test]
fn worker_status_records_token_usage() {
    let (tmp, paths) = setup_active_run();
    worker::status::run_in(
        tmp.path(),
        "001",
        "in_progress",
        Some("coding"),
        Some("working"),
        Some(12400),
    )
    .unwrap();
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.token_usage, Some(12400));
}
