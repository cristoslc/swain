mod common;

use agentrc::commands;
use tempfile::TempDir;

fn setup_active_run_with_data() -> TempDir {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "auth-refactor").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "completed", None, Some("done"), None)
        .unwrap();
    commands::worker::status::run_in(
        tmp.path(),
        "002",
        "in_progress",
        Some("testing"),
        Some("running tests"),
        None,
    )
    .unwrap();
    let paths = agentrc::fs::bus::OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    std::fs::write(
        active.orchestrator_log(),
        "[2026-04-11T14:45:00Z] Integrated 001\n[2026-04-11T14:45:30Z] Waiting on 002\n",
    )
    .unwrap();
    tmp
}

#[test]
fn resume_output_contains_run_id() {
    let tmp = setup_active_run_with_data();
    let output = commands::resume::format_resume(tmp.path()).unwrap();
    assert!(output.contains("AGENTRC ACTIVE RUN"));
    assert!(output.contains("auth-refactor"));
}

#[test]
fn resume_output_contains_task_statuses() {
    let tmp = setup_active_run_with_data();
    let output = commands::resume::format_resume(tmp.path()).unwrap();
    assert!(output.contains("001"));
    assert!(output.contains("completed"));
    assert!(output.contains("002"));
    assert!(output.contains("in_progress"));
}

#[test]
fn resume_output_contains_recent_log() {
    let tmp = setup_active_run_with_data();
    let output = commands::resume::format_resume(tmp.path()).unwrap();
    assert!(output.contains("RECENT LOG"));
    assert!(output.contains("Integrated 001"));
}

#[test]
fn resume_output_contains_sections() {
    let tmp = setup_active_run_with_data();
    let output = commands::resume::format_resume(tmp.path()).unwrap();
    assert!(output.contains("TASK STATUS"));
    assert!(output.contains("STALE HEARTBEATS"));
    assert!(output.contains("BLOCKED TASKS"));
}

#[test]
fn resume_fails_with_no_active_run() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    let result = commands::resume::format_resume(tmp.path());
    assert!(result.is_err());
}
