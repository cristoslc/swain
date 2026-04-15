mod common;

use agentrc::commands::run as run_cmd;
use agentrc::fs::bus::OrchestratorPaths;
use tempfile::TempDir;

fn setup_initialized_project() -> TempDir {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    agentrc::commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    tmp
}

#[test]
fn run_create_makes_run_dir_and_active_symlink() {
    let tmp = setup_initialized_project();
    let paths = OrchestratorPaths::new(tmp.path());
    run_cmd::create_in(tmp.path(), "auth-refactor").unwrap();
    assert!(paths.active().symlink_metadata().is_ok());
    let active = paths.active_run().unwrap();
    assert!(active.tasks_dir().is_dir());
    assert!(active.status_dir().is_dir());
    assert!(active.heartbeats_dir().is_dir());
    assert!(active.notes_dir().is_dir());
    assert!(active.results_dir().is_dir());
    assert!(active.worktrees_dir().is_dir());
    assert!(active.config_snapshot().is_file());
}

#[test]
fn run_create_fails_if_already_active() {
    let tmp = setup_initialized_project();
    run_cmd::create_in(tmp.path(), "first-run").unwrap();
    let result = run_cmd::create_in(tmp.path(), "second-run");
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("already active"));
}

#[test]
fn run_list_shows_runs() {
    let tmp = setup_initialized_project();
    run_cmd::create_in(tmp.path(), "first-run").unwrap();
    run_cmd::archive_in(tmp.path()).unwrap();
    run_cmd::create_in(tmp.path(), "second-run").unwrap();
    let runs = run_cmd::list_in(tmp.path()).unwrap();
    assert_eq!(runs.len(), 2);
}

#[test]
fn run_archive_removes_active_symlink() {
    let tmp = setup_initialized_project();
    let paths = OrchestratorPaths::new(tmp.path());
    run_cmd::create_in(tmp.path(), "test-run").unwrap();
    assert!(paths.active_run().is_some());
    run_cmd::archive_in(tmp.path()).unwrap();
    assert!(paths.active_run().is_none());
}

#[test]
fn run_archive_fails_if_no_active_run() {
    let tmp = setup_initialized_project();
    let result = run_cmd::archive_in(tmp.path());
    assert!(result.is_err());
}

#[test]
fn run_list_marks_active_run() {
    let tmp = setup_initialized_project();
    run_cmd::create_in(tmp.path(), "my-run").unwrap();
    let runs = run_cmd::list_in(tmp.path()).unwrap();
    assert_eq!(runs.len(), 1);
    assert!(runs[0].active);
}
