mod common;

use agentrc::commands;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::git::wrapper::Git;
use tempfile::TempDir;

fn setup_in_progress_task(tmp: &TempDir) -> OrchestratorPaths {
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());

    // Create worktree with a commit on the branch
    let wt_path = active.worktree_dir("001");
    git.create_worktree(&wt_path, "orc/001-test-task", "HEAD")
        .unwrap();
    std::fs::write(wt_path.join("work.txt"), "some work").unwrap();
    let _ = std::process::Command::new("git")
        .args(["add", "work.txt"])
        .current_dir(&wt_path)
        .output();
    let _ = std::process::Command::new("git")
        .args(["commit", "-m", "work in progress"])
        .current_dir(&wt_path)
        .output();

    // Write brief
    let brief_content = "---\nid: \"001\"\nslug: test-task\nclassification: writer\nbase_branch: master\nbranch: orc/001-test-task\npane_id: null\ndepends_on: []\ncreated_at: 2026-04-12T00:00:00Z\n---\n\n# Task 001\n";
    std::fs::write(active.tasks_dir().join("001-test-task.md"), brief_content).unwrap();

    commands::worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();

    paths
}

#[test]
fn respawn_validates_in_progress_state() {
    let tmp = TempDir::new().unwrap();
    let _paths = setup_in_progress_task(&tmp);

    // Should succeed for in_progress task
    let result = commands::respawn::validate_respawn(tmp.path(), "001");
    assert!(result.is_ok());
}

#[test]
fn respawn_rejects_completed_task() {
    let tmp = TempDir::new().unwrap();
    let _paths = setup_in_progress_task(&tmp);
    commands::worker::status::run_in(tmp.path(), "001", "completed", None, None, None).unwrap();

    let result = commands::respawn::validate_respawn(tmp.path(), "001");
    assert!(result.is_err());
}

#[test]
fn respawn_rejects_missing_branch() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), Some("cargo test"), false).unwrap();
    commands::run::create_in(tmp.path(), "test-run").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();

    // Write brief pointing to a branch that doesn't exist
    let brief_content = "---\nid: \"001\"\nslug: test-task\nclassification: writer\nbase_branch: master\nbranch: orc/001-nonexistent\npane_id: null\ndepends_on: []\ncreated_at: 2026-04-12T00:00:00Z\n---\n\n# Task 001\n";
    std::fs::write(active.tasks_dir().join("001-test-task.md"), brief_content).unwrap();

    commands::worker::status::run_in(tmp.path(), "001", "failed", None, None, None).unwrap();

    // No branch exists
    let result = commands::respawn::validate_respawn(tmp.path(), "001");
    assert!(result.is_err());
}

#[test]
fn respawn_generates_resume_seed() {
    let seed =
        commands::respawn::generate_resume_seed("001", "path/to/brief.md", "orc/001-test", 3);
    assert!(seed.contains("resuming work"));
    assert!(seed.contains("001"));
    assert!(seed.contains("3 commits"));
    assert!(seed.contains("git log"));
}
