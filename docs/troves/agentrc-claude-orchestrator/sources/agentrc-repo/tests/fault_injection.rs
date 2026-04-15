mod common;

use agentrc::commands;
use agentrc::commands::worker;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::git::wrapper::Git;
use agentrc::model::task::TaskState;
use tempfile::TempDir;

#[test]
fn fault_worker_reports_failure() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "fault-test").unwrap();
    worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    worker::status::run_in(
        tmp.path(),
        "001",
        "failed",
        None,
        Some("compilation error"),
        None,
    )
    .unwrap();
    let statuses = commands::status::collect_statuses(tmp.path()).unwrap();
    assert_eq!(statuses[0].state, TaskState::Failed);
    assert_eq!(
        statuses[0].last_message.as_deref(),
        Some("compilation error")
    );
}

#[test]
fn fault_teardown_refuses_in_progress_task() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "fault-test").unwrap();
    worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    let result = commands::teardown::teardown_task(tmp.path(), "001", false);
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("in_progress"));
}

#[test]
fn fault_integrate_conflict_detected() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(tmp.path().join("shared.txt"), "original").unwrap();
    let git = Git::new(tmp.path());
    git.add_all().unwrap();
    git.commit("add shared").unwrap();
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "conflict-fault").unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let base = git.current_branch().unwrap();
    for (id, slug, content) in [("001", "change-a", "AAA"), ("002", "change-b", "BBB")] {
        let brief = format!(
            "---\nid: \"{}\"\nslug: {}\nclassification: writer\nbase_branch: {}\nbranch: orc/{}-{}\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task {}",
            id, slug, base, id, slug, id,
        );
        std::fs::write(active.task_brief(id, slug), brief).unwrap();
        let branch = format!("orc/{}-{}", id, slug);
        commands::spawn::setup_worktree(tmp.path(), &paths, id, slug, &branch, &base).unwrap();
        let wt = active.worktree_dir(id);
        std::fs::write(wt.join("shared.txt"), content).unwrap();
        Git::new(&wt).add_all().unwrap();
        Git::new(&wt)
            .commit(&format!("change shared to {}", content))
            .unwrap();
        worker::status::run_in(tmp.path(), id, "completed", None, None, None).unwrap();
    }
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert!(results[0].success);
    assert!(results[1].conflict);
}

#[test]
fn fault_worker_status_invalid_state() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "test").unwrap();
    let result = worker::status::run_in(tmp.path(), "001", "banana", None, None, None);
    assert!(result.is_err());
    assert!(result
        .unwrap_err()
        .to_string()
        .contains("invalid task state"));
}

#[test]
fn fault_double_run_create() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "first").unwrap();
    let result = commands::run::create_in(tmp.path(), "second");
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("already active"));
}

#[test]
fn fault_resume_no_active_run() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    let result = commands::resume::format_resume(tmp.path());
    assert!(result.is_err());
}

#[test]
fn fault_stale_heartbeat_detection() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "stale-hb").unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    worker::heartbeat::tick(tmp.path(), "001").unwrap();
    let hb = active.heartbeat_file("001");
    let old = std::time::SystemTime::now() - std::time::Duration::from_secs(300);
    filetime::set_file_mtime(&hb, filetime::FileTime::from_system_time(old)).unwrap();
    let stale = commands::status::find_stale_heartbeats(tmp.path(), 120).unwrap();
    assert!(stale.contains(&"001".to_string()));
}

#[test]
fn fault_archive_no_active_run() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    let result = commands::run::archive_in(tmp.path());
    assert!(result.is_err());
}

#[test]
fn fault_status_no_active_run() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    let result = commands::status::collect_statuses(tmp.path());
    assert!(result.is_err());
}

#[test]
fn fault_worker_note_no_active_run() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    let result = worker::note::run_in(tmp.path(), "001", "test note");
    assert!(result.is_err());
}
