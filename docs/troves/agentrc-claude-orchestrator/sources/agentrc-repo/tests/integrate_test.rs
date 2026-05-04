mod common;

use agentrc::commands;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::git::wrapper::Git;
use tempfile::TempDir;

/// Setup: project with an active run, two completed writer tasks on separate branches
fn setup_two_writer_tasks() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "test-integrate").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());
    let base = git.current_branch().unwrap();

    // Task 001: add file-a.txt
    let wt1 = active.worktree_dir("001");
    git.create_worktree(&wt1, "orc/001-feat-a", &base).unwrap();
    std::fs::write(wt1.join("file-a.txt"), "feature a").unwrap();
    let g1 = Git::new(&wt1);
    g1.add_all().unwrap();
    g1.commit("add file-a").unwrap();

    // Task 002: add file-b.txt
    let wt2 = active.worktree_dir("002");
    git.create_worktree(&wt2, "orc/002-feat-b", &base).unwrap();
    std::fs::write(wt2.join("file-b.txt"), "feature b").unwrap();
    let g2 = Git::new(&wt2);
    g2.add_all().unwrap();
    g2.commit("add file-b").unwrap();

    // Write task briefs
    let brief1 = format!(
        "---\nid: \"001\"\nslug: feat-a\nclassification: writer\nbase_branch: {}\nbranch: orc/001-feat-a\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 001",
        base
    );
    let brief2 = format!(
        "---\nid: \"002\"\nslug: feat-b\nclassification: writer\nbase_branch: {}\nbranch: orc/002-feat-b\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 002",
        base
    );
    std::fs::write(active.task_brief("001", "feat-a"), brief1).unwrap();
    std::fs::write(active.task_brief("002", "feat-b"), brief2).unwrap();

    // Mark both completed
    commands::worker::status::run_in(tmp.path(), "001", "completed", None, None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None, None).unwrap();

    (tmp, paths)
}

/// Setup: project with two tasks that both touch the same file (for overlap detection)
fn setup_overlapping_tasks() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    // Add a file both branches will modify
    std::fs::create_dir_all(tmp.path().join("src")).unwrap();
    std::fs::write(tmp.path().join("src/main.rs"), "fn main() {}").unwrap();
    let git = Git::new(tmp.path());
    git.add_all().unwrap();
    git.commit("add main.rs").unwrap();

    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "overlap-test").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let base = git.current_branch().unwrap();

    // Task 001: modify src/main.rs and add file-a.txt
    let wt1 = active.worktree_dir("001");
    git.create_worktree(&wt1, "orc/001-mod-a", &base).unwrap();
    std::fs::write(wt1.join("src/main.rs"), "fn main() { println!(\"a\"); }").unwrap();
    std::fs::write(wt1.join("file-a.txt"), "unique to a").unwrap();
    Git::new(&wt1).add_all().unwrap();
    Git::new(&wt1).commit("task 001 changes").unwrap();

    // Task 002: modify src/main.rs and add file-b.txt
    let wt2 = active.worktree_dir("002");
    git.create_worktree(&wt2, "orc/002-mod-b", &base).unwrap();
    std::fs::write(wt2.join("src/main.rs"), "fn main() { println!(\"b\"); }").unwrap();
    std::fs::write(wt2.join("file-b.txt"), "unique to b").unwrap();
    Git::new(&wt2).add_all().unwrap();
    Git::new(&wt2).commit("task 002 changes").unwrap();

    let brief1 = format!(
        "---\nid: \"001\"\nslug: mod-a\nclassification: writer\nbase_branch: {}\nbranch: orc/001-mod-a\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 001",
        base
    );
    let brief2 = format!(
        "---\nid: \"002\"\nslug: mod-b\nclassification: writer\nbase_branch: {}\nbranch: orc/002-mod-b\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 002",
        base
    );
    std::fs::write(active.task_brief("001", "mod-a"), brief1).unwrap();
    std::fs::write(active.task_brief("002", "mod-b"), brief2).unwrap();

    commands::worker::status::run_in(tmp.path(), "001", "completed", None, None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None, None).unwrap();

    (tmp, paths)
}

#[test]
fn integrate_merges_independent_tasks() {
    let (tmp, _) = setup_two_writer_tasks();
    let result = commands::integrate::integrate_in(tmp.path());
    assert!(result.is_ok());
    assert!(tmp.path().join("file-a.txt").exists());
    assert!(tmp.path().join("file-b.txt").exists());
}

#[test]
fn integrate_returns_merge_results() {
    let (tmp, _) = setup_two_writer_tasks();
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 2);
    assert!(results.iter().all(|r| r.success));
}

#[test]
fn integrate_surfaces_commit_history() {
    let (tmp, _) = setup_two_writer_tasks();
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert!(!results[0].commit_history.is_empty());
}

/// Setup conflicting tasks: both modify the same file
fn setup_conflicting_tasks() -> (TempDir, OrchestratorPaths) {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    std::fs::write(tmp.path().join("shared.txt"), "original").unwrap();
    let git = Git::new(tmp.path());
    git.add_all().unwrap();
    git.commit("add shared file").unwrap();

    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "conflict-test").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let base = git.current_branch().unwrap();

    // Task 001 modifies shared.txt
    let wt1 = active.worktree_dir("001");
    git.create_worktree(&wt1, "orc/001-change-a", &base)
        .unwrap();
    std::fs::write(wt1.join("shared.txt"), "version A").unwrap();
    Git::new(&wt1).add_all().unwrap();
    Git::new(&wt1).commit("change to version A").unwrap();

    // Task 002 modifies shared.txt differently (depends on 001)
    let wt2 = active.worktree_dir("002");
    git.create_worktree(&wt2, "orc/002-change-b", &base)
        .unwrap();
    std::fs::write(wt2.join("shared.txt"), "version B").unwrap();
    Git::new(&wt2).add_all().unwrap();
    Git::new(&wt2).commit("change to version B").unwrap();

    let brief1 = format!(
        "---\nid: \"001\"\nslug: change-a\nclassification: writer\nbase_branch: {}\nbranch: orc/001-change-a\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 001",
        base
    );
    let brief2 = format!(
        "---\nid: \"002\"\nslug: change-b\nclassification: writer\nbase_branch: {}\nbranch: orc/002-change-b\ndepends_on: [\"001\"]\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 002",
        base
    );
    std::fs::write(active.task_brief("001", "change-a"), brief1).unwrap();
    std::fs::write(active.task_brief("002", "change-b"), brief2).unwrap();

    commands::worker::status::run_in(tmp.path(), "001", "completed", None, None, None).unwrap();
    commands::worker::status::run_in(tmp.path(), "002", "completed", None, None, None).unwrap();

    (tmp, paths)
}

#[test]
fn integrate_detects_merge_conflict() {
    let (tmp, _) = setup_conflicting_tasks();
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert!(results[0].success); // First merge succeeds
    assert!(!results[1].success); // Second conflicts
    assert!(results[1].conflict);
}

#[test]
fn integrate_no_writer_tasks() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "empty-run").unwrap();

    // Only a reader task
    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let brief = "---\nid: \"001\"\nslug: review\nclassification: reader\nbase_branch: main\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Review";
    std::fs::write(active.task_brief("001", "review"), brief).unwrap();

    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert!(results.is_empty()); // No writer tasks to merge
}

// ===========================================================================
// Dry-run tests
// ===========================================================================

#[test]
fn dry_run_clean_merge_plan() {
    // Two tasks touching different files → reports clean merge plan, no overlaps
    let (tmp, _) = setup_two_writer_tasks();
    let report = commands::integrate::dry_run_in(tmp.path()).unwrap();
    assert_eq!(report.entries.len(), 2);
    assert!(report.overlaps.is_empty(), "no overlaps expected");
    // Each entry should list its changed files
    assert!(!report.entries[0].changed_files.is_empty());
    assert!(!report.entries[1].changed_files.is_empty());
}

#[test]
fn dry_run_detects_file_overlap() {
    // Two tasks both touching src/main.rs → warns about potential conflict
    let (tmp, _) = setup_overlapping_tasks();
    let report = commands::integrate::dry_run_in(tmp.path()).unwrap();
    assert_eq!(report.entries.len(), 2);
    assert!(!report.overlaps.is_empty(), "should detect overlap");
    // Check that src/main.rs is identified as overlapping between 001 and 002
    let overlap = &report.overlaps[0];
    assert_eq!(overlap.file, "src/main.rs");
    assert!(overlap.task_ids.contains(&"001".to_string()));
    assert!(overlap.task_ids.contains(&"002".to_string()));
}

#[test]
fn dry_run_has_no_side_effects() {
    // After dry-run, no branches merged, base branch unchanged
    let (tmp, _) = setup_two_writer_tasks();
    let git = Git::new(tmp.path());
    let branch_before = git.current_branch().unwrap();
    let log_before = git.log_oneline(&branch_before, 5).unwrap();

    let _report = commands::integrate::dry_run_in(tmp.path()).unwrap();

    // Branch should be the same
    let branch_after = git.current_branch().unwrap();
    assert_eq!(branch_before, branch_after);
    // Commit log should be unchanged
    let log_after = git.log_oneline(&branch_after, 5).unwrap();
    assert_eq!(log_before, log_after);
    // Files from branches should NOT exist on base
    assert!(!tmp.path().join("file-a.txt").exists());
    assert!(!tmp.path().join("file-b.txt").exists());
}

#[test]
fn dry_run_empty_no_tasks() {
    // No completed writer tasks → reports nothing to merge
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "empty-run").unwrap();

    let report = commands::integrate::dry_run_in(tmp.path()).unwrap();
    assert!(report.entries.is_empty());
    assert!(report.overlaps.is_empty());
}

#[test]
fn conflict_diagnostics_includes_file_names() {
    // Real merge conflict → MergeResult includes conflicting file names and overlapping tasks
    let (tmp, _) = setup_overlapping_tasks();
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 2);

    // Find the successful and conflicting results (order depends on topo sort)
    let success = results
        .iter()
        .find(|r| r.success)
        .expect("one should succeed");
    let conflict = results
        .iter()
        .find(|r| r.conflict)
        .expect("one should conflict");

    // The conflicting result should include file names
    assert!(
        !conflict.conflicting_files.is_empty(),
        "should report conflicting files"
    );
    assert!(conflict
        .conflicting_files
        .contains(&"src/main.rs".to_string()));

    // Should identify the other task as overlapping
    assert!(
        !conflict.overlapping_tasks.is_empty(),
        "should identify overlapping tasks"
    );
    assert!(
        conflict.overlapping_tasks.contains(&success.task_id),
        "overlapping_tasks should contain the successful task's id"
    );
}

#[test]
fn test_failure_diagnostics_includes_stderr() {
    // Post-merge test failure → MergeResult includes touched files and stderr snippet
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "test-fail-run").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());
    let base = git.current_branch().unwrap();

    // Write a config with a test command that always fails
    let config = serde_json::json!({
        "project_root": tmp.path(),
        "base_branch": base,
        "test_command": "echo 'test error output' >&2 && exit 1"
    });
    std::fs::write(active.config_snapshot(), config.to_string()).unwrap();

    // Task 001: add a file
    let wt1 = active.worktree_dir("001");
    git.create_worktree(&wt1, "orc/001-test-fail", &base)
        .unwrap();
    std::fs::write(wt1.join("feature.txt"), "new feature").unwrap();
    Git::new(&wt1).add_all().unwrap();
    Git::new(&wt1).commit("add feature").unwrap();

    let brief = format!(
        "---\nid: \"001\"\nslug: test-fail\nclassification: writer\nbase_branch: {}\nbranch: orc/001-test-fail\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 001",
        base
    );
    std::fs::write(active.task_brief("001", "test-fail"), brief).unwrap();
    commands::worker::status::run_in(tmp.path(), "001", "completed", None, None, None).unwrap();

    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 1);
    assert!(!results[0].success);
    assert!(results[0].test_failure);
    // Should include touched files
    assert!(
        !results[0].touched_files.is_empty(),
        "should report touched files on test failure"
    );
    // Should include stderr snippet
    assert!(
        results[0].test_stderr.is_some(),
        "should capture test stderr"
    );
    assert!(results[0]
        .test_stderr
        .as_ref()
        .unwrap()
        .contains("test error output"));
}
