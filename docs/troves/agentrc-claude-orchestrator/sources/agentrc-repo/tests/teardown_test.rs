mod common;

use agentrc::commands;
use agentrc::fs::bus::OrchestratorPaths;
use tempfile::TempDir;

fn setup_with_worktree() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = agentrc::git::wrapper::Git::new(tmp.path());
    let wt_path = active.worktree_dir("001");
    git.create_worktree(&wt_path, "orc/001-test", "HEAD")
        .unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "completed", None, None, None).unwrap();
    (tmp, paths)
}

#[test]
fn teardown_removes_worktree() {
    let (tmp, paths) = setup_with_worktree();
    let active = paths.active_run().unwrap();
    assert!(active.worktree_dir("001").exists());
    commands::teardown::teardown_task(tmp.path(), "001", false).unwrap();
    assert!(!active.worktree_dir("001").exists());
}

#[test]
fn teardown_refuses_non_completed_task() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    let result = commands::teardown::teardown_task(tmp.path(), "001", false);
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("in_progress"));
}

#[test]
fn teardown_allows_failed_task() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "failed", None, None, None).unwrap();
    let result = commands::teardown::teardown_task(tmp.path(), "001", false);
    assert!(result.is_ok());
}

#[test]
fn teardown_force_overrides_state_check() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    let result = commands::teardown::teardown_task(tmp.path(), "001", true);
    assert!(result.is_ok());
}

#[test]
fn teardown_all_tears_down_completed_tasks() {
    let (tmp, paths) = setup_with_worktree();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None, None).unwrap();
    commands::teardown::teardown_all(tmp.path(), false).unwrap();
    let active = paths.active_run().unwrap();
    assert!(!active.worktree_dir("001").exists());
}

#[test]
fn teardown_all_skips_in_progress_tasks() {
    let (tmp, _paths) = setup_with_worktree();
    commands::worker::status::run_in(tmp.path(), "002", "in_progress", None, None, None).unwrap();
    commands::teardown::teardown_all(tmp.path(), false).unwrap();
    // 001 (completed) should be torn down, 002 (in_progress) should be skipped
    // No assertion on 002's worktree since it has none, just verify no error
}
