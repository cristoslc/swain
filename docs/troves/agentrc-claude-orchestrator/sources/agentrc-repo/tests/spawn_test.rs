mod common;

use agentrc::commands::spawn;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::model::task::TaskState;
use tempfile::TempDir;

fn setup_run_with_writer_task() -> (TempDir, OrchestratorPaths) {
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
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task 001: Add login
"#;
    std::fs::write(active.task_brief("001", "add-login"), brief).unwrap();
    (tmp, paths)
}

fn setup_run_with_reader_task() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    agentrc::commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    agentrc::commands::run::create_in(tmp.path(), "test-run").unwrap();
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let brief = r#"---
id: "002"
slug: review-deps
classification: reader
base_branch: HEAD
depends_on: []
created_at: 2026-04-11T14:30:00Z
---

# Task 002: Review deps
"#;
    std::fs::write(active.task_brief("002", "review-deps"), brief).unwrap();
    (tmp, paths)
}

#[test]
fn spawn_parses_task_brief() {
    let (_tmp, paths) = setup_run_with_writer_task();
    let active = paths.active_run().unwrap();
    let brief = spawn::load_task_brief(active.task_brief("001", "add-login")).unwrap();
    assert_eq!(brief.id, "001");
    assert_eq!(brief.slug, "add-login");
}

#[test]
fn spawn_creates_worktree_for_writer() {
    let (tmp, paths) = setup_run_with_writer_task();
    spawn::setup_worktree(
        tmp.path(),
        &paths,
        "001",
        "add-login",
        "orc/001-add-login",
        "HEAD",
    )
    .unwrap();
    let active = paths.active_run().unwrap();
    let wt = active.worktree_dir("001");
    assert!(wt.exists());
    assert!(wt.join("README.md").exists());
}

#[test]
fn spawn_skips_worktree_for_reader() {
    let (_tmp, paths) = setup_run_with_reader_task();
    let active = paths.active_run().unwrap();
    assert!(!active.worktree_dir("002").exists());
}

#[test]
fn spawn_sets_initial_status() {
    let (tmp, paths) = setup_run_with_writer_task();
    spawn::write_initial_status(tmp.path(), "001").unwrap();
    let active = paths.active_run().unwrap();
    let content = std::fs::read_to_string(active.status_file("001")).unwrap();
    let status: agentrc::model::task::TaskStatus = serde_json::from_str(&content).unwrap();
    assert_eq!(status.state, TaskState::Spawning);
}

#[test]
fn spawn_generates_seed_prompt() {
    let seed = spawn::generate_seed_prompt("001", ".orchestrator/active/tasks/001-add-login.md");
    assert!(seed.contains("001"));
    assert!(seed.contains("001-add-login.md"));
    assert!(seed.contains("agentrc worker"));
}

#[test]
fn spawn_finds_task_brief_by_id() {
    let (_tmp, paths) = setup_run_with_writer_task();
    let active = paths.active_run().unwrap();
    let found = spawn::find_task_brief(&active, "001").unwrap();
    assert!(found.to_str().unwrap().contains("001-add-login.md"));
}
