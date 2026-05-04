mod common;

use agentrc::commands;
use agentrc::commands::worker;
use agentrc::fs::bus::OrchestratorPaths;
use agentrc::git::wrapper::Git;
use agentrc::model::task::TaskState;
use tempfile::TempDir;

/// Full lifecycle: init → run create → write brief → simulate worker → status → integrate
#[test]
fn e2e_single_writer_lifecycle() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());

    // 1. Init
    commands::init::run_in(tmp.path(), None, false).unwrap();

    // 2. Create run
    commands::run::create_in(tmp.path(), "e2e-test").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());
    let base = git.current_branch().unwrap();

    // 3. Write task brief
    let brief = format!(
        "---\nid: \"001\"\nslug: add-feature\nclassification: writer\nworktree: {}\nbase_branch: {}\nbranch: orc/001-add-feature\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 001: Add feature\n\n## Scope\nAdd a new file.\n",
        active.worktree_dir("001").display(),
        base,
    );
    std::fs::write(active.task_brief("001", "add-feature"), brief).unwrap();

    // 4. Create worktree (normally done by spawn)
    commands::spawn::setup_worktree(
        tmp.path(),
        &paths,
        "001",
        "add-feature",
        "orc/001-add-feature",
        &base,
    )
    .unwrap();
    commands::spawn::write_initial_status(tmp.path(), "001").unwrap();

    // 5. Simulate worker: status → note → write code → commit → done
    worker::status::run_in(
        tmp.path(),
        "001",
        "in_progress",
        Some("implementing"),
        Some("starting"),
        None,
    )
    .unwrap();

    worker::note::run_in(tmp.path(), "001", "Writing feature code").unwrap();

    // Write code in worktree
    let wt = active.worktree_dir("001");
    std::fs::write(wt.join("feature.txt"), "new feature").unwrap();
    let wt_git = Git::new(&wt);
    wt_git.add_all().unwrap();
    wt_git.commit("add feature.txt").unwrap();

    // Write result and complete
    let result_content = "# Result\nFeature added successfully.\n";
    let result_tmp = tmp.path().join("result.md");
    std::fs::write(&result_tmp, result_content).unwrap();
    worker::done::run_in(tmp.path(), "001", Some(result_tmp.to_str().unwrap())).unwrap();

    // 6. Check status
    let statuses = commands::status::collect_statuses(tmp.path()).unwrap();
    assert_eq!(statuses.len(), 1);
    assert_eq!(statuses[0].state, TaskState::Completed);

    // 7. Integrate
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 1);
    assert!(results[0].success);

    // Feature file should now be in project root
    assert!(tmp.path().join("feature.txt").exists());

    // 8. Resume shows the run
    let resume = commands::resume::format_resume(tmp.path()).unwrap();
    assert!(resume.contains("001"));
    assert!(resume.contains("completed"));

    // 9. Teardown
    commands::teardown::teardown_task(tmp.path(), "001", false).unwrap();
    assert!(!active.worktree_dir("001").exists());
}

#[test]
fn e2e_two_independent_writers() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "two-writers").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());
    let base = git.current_branch().unwrap();

    // Two independent writer tasks
    for (id, slug, filename) in [("001", "feat-a", "a.txt"), ("002", "feat-b", "b.txt")] {
        let brief = format!(
            "---\nid: \"{}\"\nslug: {}\nclassification: writer\nbase_branch: {}\nbranch: orc/{}-{}\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task {}",
            id, slug, base, id, slug, id,
        );
        std::fs::write(active.task_brief(id, slug), brief).unwrap();

        // Setup worktree
        let branch = format!("orc/{}-{}", id, slug);
        commands::spawn::setup_worktree(tmp.path(), &paths, id, slug, &branch, &base).unwrap();
        commands::spawn::write_initial_status(tmp.path(), id).unwrap();

        // Simulate worker
        worker::status::run_in(tmp.path(), id, "in_progress", None, None, None).unwrap();
        let wt = active.worktree_dir(id);
        std::fs::write(wt.join(filename), format!("content of {}", filename)).unwrap();
        let wt_git = Git::new(&wt);
        wt_git.add_all().unwrap();
        wt_git.commit(&format!("add {}", filename)).unwrap();
        worker::done::run_in(tmp.path(), id, None).unwrap();
    }

    // Integrate both
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 2);
    assert!(results.iter().all(|r| r.success));

    // Both files present
    assert!(tmp.path().join("a.txt").exists());
    assert!(tmp.path().join("b.txt").exists());

    // Teardown all
    commands::teardown::teardown_all(tmp.path(), false).unwrap();
}

#[test]
fn e2e_reader_plus_writer() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "reader-writer").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());
    let base = git.current_branch().unwrap();

    // Writer task
    let brief_w = format!(
        "---\nid: \"001\"\nslug: impl\nclassification: writer\nbase_branch: {}\nbranch: orc/001-impl\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Writer task",
        base,
    );
    std::fs::write(active.task_brief("001", "impl"), brief_w).unwrap();
    commands::spawn::setup_worktree(tmp.path(), &paths, "001", "impl", "orc/001-impl", &base)
        .unwrap();
    commands::spawn::write_initial_status(tmp.path(), "001").unwrap();
    worker::status::run_in(tmp.path(), "001", "in_progress", None, None, None).unwrap();
    let wt = active.worktree_dir("001");
    std::fs::write(wt.join("impl.txt"), "implementation").unwrap();
    Git::new(&wt).add_all().unwrap();
    Git::new(&wt).commit("implement").unwrap();
    worker::done::run_in(tmp.path(), "001", None).unwrap();

    // Reader task — only writes notes and result, no code changes
    let brief_r = format!(
        "---\nid: \"002\"\nslug: review\nclassification: reader\nbase_branch: {}\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Reader task",
        base,
    );
    std::fs::write(active.task_brief("002", "review"), brief_r).unwrap();
    commands::spawn::write_initial_status(tmp.path(), "002").unwrap();
    worker::status::run_in(tmp.path(), "002", "in_progress", None, None, None).unwrap();
    worker::note::run_in(tmp.path(), "002", "Reviewed the codebase").unwrap();
    worker::done::run_in(tmp.path(), "002", None).unwrap();

    // Integrate — only writer merges, reader is skipped
    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 1); // Only writer
    assert!(results[0].success);
    assert!(tmp.path().join("impl.txt").exists());

    // Both tasks show as completed
    let statuses = commands::status::collect_statuses(tmp.path()).unwrap();
    assert_eq!(statuses.len(), 2);
    assert!(statuses.iter().all(|s| s.state == TaskState::Completed));
}

#[test]
fn e2e_dependent_tasks_merge_in_order() {
    let tmp = TempDir::new().unwrap();
    common::init_test_repo(tmp.path());
    commands::init::run_in(tmp.path(), None, false).unwrap();
    commands::run::create_in(tmp.path(), "deps-test").unwrap();

    let paths = OrchestratorPaths::new(tmp.path());
    let active = paths.active_run().unwrap();
    let git = Git::new(tmp.path());
    let base = git.current_branch().unwrap();

    // Task 002 depends on 001
    let brief1 = format!(
        "---\nid: \"001\"\nslug: base-feat\nclassification: writer\nbase_branch: {}\nbranch: orc/001-base-feat\ndepends_on: []\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 001",
        base,
    );
    let brief2 = format!(
        "---\nid: \"002\"\nslug: derived-feat\nclassification: writer\nbase_branch: {}\nbranch: orc/002-derived-feat\ndepends_on: [\"001\"]\ncreated_at: 2026-04-11T14:30:00Z\n---\n# Task 002",
        base,
    );
    std::fs::write(active.task_brief("001", "base-feat"), brief1).unwrap();
    std::fs::write(active.task_brief("002", "derived-feat"), brief2).unwrap();

    // Both tasks add different files (no conflict despite dependency)
    for (id, slug, filename) in [
        ("001", "base-feat", "base.txt"),
        ("002", "derived-feat", "derived.txt"),
    ] {
        let branch = format!("orc/{}-{}", id, slug);
        commands::spawn::setup_worktree(tmp.path(), &paths, id, slug, &branch, &base).unwrap();
        commands::spawn::write_initial_status(tmp.path(), id).unwrap();
        worker::status::run_in(tmp.path(), id, "in_progress", None, None, None).unwrap();
        let wt = active.worktree_dir(id);
        std::fs::write(wt.join(filename), format!("{} content", filename)).unwrap();
        Git::new(&wt).add_all().unwrap();
        Git::new(&wt).commit(&format!("add {}", filename)).unwrap();
        worker::done::run_in(tmp.path(), id, None).unwrap();
    }

    let results = commands::integrate::integrate_in(tmp.path()).unwrap();
    assert_eq!(results.len(), 2);
    assert!(results.iter().all(|r| r.success));
    // 001 should be merged before 002 (dependency order)
    assert_eq!(results[0].task_id, "001");
    assert_eq!(results[1].task_id, "002");
    assert!(tmp.path().join("base.txt").exists());
    assert!(tmp.path().join("derived.txt").exists());
}
