use std::collections::HashMap;
use std::path::Path;
use std::process::Command;

use anyhow::{Context, Result};

use crate::commands::plan;
use crate::commands::spawn::load_task_brief;
use crate::fs::bus::OrchestratorPaths;
use crate::fs::run::RunPaths;
use crate::git::wrapper::Git;
use crate::model::config::OrchestratorConfig;
use crate::model::error::AppError;
use crate::model::task::{Classification, TaskBriefFrontmatter};

/// The outcome of merging a single writer task branch into the base branch.
#[derive(Debug)]
pub struct MergeResult {
    pub task_id: String,
    pub branch: String,
    pub success: bool,
    pub conflict: bool,
    pub test_failure: bool,
    pub commit_history: Vec<String>,
    pub message: String,
    /// Files that had merge conflicts (populated on conflict).
    pub conflicting_files: Vec<String>,
    /// Task IDs whose changed files overlap with this task's conflicting files.
    pub overlapping_tasks: Vec<String>,
    /// Files touched by this task's branch (populated on test failure).
    pub touched_files: Vec<String>,
    /// First 50 lines of test stderr (populated on test failure).
    pub test_stderr: Option<String>,
}

/// A single entry in a dry-run report.
#[derive(Debug)]
pub struct DryRunEntry {
    pub task_id: String,
    pub branch: String,
    pub changed_files: Vec<String>,
}

/// A file touched by multiple tasks — potential merge conflict.
#[derive(Debug)]
pub struct FileOverlap {
    pub file: String,
    pub task_ids: Vec<String>,
}

/// The result of a dry-run integration preview.
#[derive(Debug)]
pub struct DryRunReport {
    pub entries: Vec<DryRunEntry>,
    pub overlaps: Vec<FileOverlap>,
}

// ---------------------------------------------------------------------------
// CLI entry points
// ---------------------------------------------------------------------------

/// CLI entry: integrate completed writer branches into the base branch.
pub fn run(dry_run: bool) -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;

    if dry_run {
        return run_dry_run(&cwd);
    }

    let results = integrate_in(&cwd)?;

    if results.is_empty() {
        println!("No writer tasks to integrate.");
        return Ok(());
    }

    // Print results table
    println!("{:<8} {:<30} {:<10} MESSAGE", "TASK", "BRANCH", "STATUS");
    println!("{}", "-".repeat(72));
    for r in &results {
        let status = if r.success {
            "OK"
        } else if r.conflict {
            "CONFLICT"
        } else if r.test_failure {
            "TEST_FAIL"
        } else {
            "FAILED"
        };
        println!(
            "{:<8} {:<30} {:<10} {}",
            r.task_id, r.branch, status, r.message
        );

        if !r.commit_history.is_empty() {
            println!("  commits:");
            for line in &r.commit_history {
                println!("    {line}");
            }
        }

        if !r.conflicting_files.is_empty() {
            println!("  conflicting files:");
            for f in &r.conflicting_files {
                println!("    {f}");
            }
            if !r.overlapping_tasks.is_empty() {
                println!("  overlaps with tasks: {}", r.overlapping_tasks.join(", "));
            }
        }

        if r.test_failure && !r.touched_files.is_empty() {
            println!("  touched files:");
            for f in &r.touched_files {
                println!("    {f}");
            }
        }
    }

    let success_count = results.iter().filter(|r| r.success).count();
    let total = results.len();
    println!("\n{success_count}/{total} tasks merged successfully.");

    Ok(())
}

/// CLI entry for dry-run mode: preview merge plan without side effects.
fn run_dry_run(project_root: &Path) -> Result<()> {
    let report = dry_run_in(project_root)?;

    if report.entries.is_empty() {
        println!("[dry-run] No writer tasks to integrate.");
        return Ok(());
    }

    println!("[dry-run] Would merge {} tasks:", report.entries.len());
    for entry in &report.entries {
        println!(
            "  {} ({}) — {} files changed",
            entry.task_id,
            entry.branch,
            entry.changed_files.len()
        );
        for f in &entry.changed_files {
            println!("    {f}");
        }
    }

    if report.overlaps.is_empty() {
        println!("\n[dry-run] No potential conflicts detected.");
    } else {
        println!("\n[dry-run] Potential conflicts:");
        for overlap in &report.overlaps {
            println!(
                "  {} touched by {}",
                overlap.file,
                overlap.task_ids.join(", ")
            );
        }
    }

    Ok(())
}

// ---------------------------------------------------------------------------
// Testable implementation
// ---------------------------------------------------------------------------

/// Preview the merge plan without making any changes.
///
/// Walks the merge order (same topo sort), lists changed files per branch,
/// and detects files modified by multiple tasks.
pub fn dry_run_in(project_root: &Path) -> Result<DryRunReport> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let config = load_config(&paths, &active)?;
    let tasks = collect_writer_tasks_ordered(&active)?;

    if tasks.is_empty() {
        return Ok(DryRunReport {
            entries: Vec::new(),
            overlaps: Vec::new(),
        });
    }

    let git = Git::new(project_root);

    // Build entries with changed files per task
    let mut entries = Vec::new();
    // Map: file -> list of task_ids that touch it
    let mut file_to_tasks: HashMap<String, Vec<String>> = HashMap::new();

    for task in &tasks {
        let branch = task
            .branch
            .as_deref()
            .unwrap_or_else(|| panic!("writer task {} has no branch", task.id));

        let changed_files = git
            .changed_files(&config.base_branch, branch)
            .unwrap_or_default();

        for f in &changed_files {
            file_to_tasks
                .entry(f.clone())
                .or_default()
                .push(task.id.clone());
        }

        entries.push(DryRunEntry {
            task_id: task.id.clone(),
            branch: branch.to_string(),
            changed_files,
        });
    }

    // Find overlaps (files touched by 2+ tasks)
    let mut overlaps: Vec<FileOverlap> = file_to_tasks
        .into_iter()
        .filter(|(_, ids)| ids.len() > 1)
        .map(|(file, task_ids)| FileOverlap { file, task_ids })
        .collect();
    overlaps.sort_by(|a, b| a.file.cmp(&b.file));

    Ok(DryRunReport { entries, overlaps })
}

/// Integrate all completed writer task branches into the base branch.
///
/// 1. Get active run paths, load config (from snapshot or main config).
/// 2. Collect writer tasks from briefs (parse frontmatter, filter by Writer).
/// 3. Sort by dependency order (topological: no-deps first, then dependents, id tiebreaker).
/// 4. If no writer tasks, return empty vec.
/// 5. Checkout base_branch.
/// 6. For each writer task:
///    a. Get commit history via `git log_branch_commits(branch, base_branch)`.
///    b. Attempt `git merge_no_ff(branch)`.
///    c. On success: if test_command configured, run tests. If tests fail, reset, mark test_failure.
///    d. On failure: `git merge_abort()`, mark conflict with diagnostics.
/// 7. Return results.
pub fn integrate_in(project_root: &Path) -> Result<Vec<MergeResult>> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;

    // Load config: prefer run snapshot, fall back to project config
    let config = load_config(&paths, &active)?;

    // Collect and sort writer tasks
    let tasks = collect_writer_tasks_ordered(&active)?;
    if tasks.is_empty() {
        return Ok(Vec::new());
    }

    let git = Git::new(project_root);

    // Pre-compute changed files per task for cross-referencing on conflict
    let mut task_changed_files: HashMap<String, Vec<String>> = HashMap::new();
    for task in &tasks {
        if let Some(branch) = task.branch.as_deref() {
            let files = git
                .changed_files(&config.base_branch, branch)
                .unwrap_or_default();
            task_changed_files.insert(task.id.clone(), files);
        }
    }

    // Checkout base branch
    git.checkout(&config.base_branch)
        .with_context(|| format!("failed to checkout base branch '{}'", config.base_branch))?;

    let log_path = active.integration_log();
    let mut results = Vec::new();

    for task in &tasks {
        let branch = task
            .branch
            .as_deref()
            .unwrap_or_else(|| panic!("writer task {} has no branch", task.id));

        // Get commit history for TDD review
        let commit_history = git
            .log_branch_commits(branch, &config.base_branch)
            .unwrap_or_default();

        // Attempt merge
        let _ = crate::events::emit_info(
            project_root,
            crate::model::event::EventType::MergeStarted,
            &task.id,
            &format!("starting merge of branch '{branch}'"),
        );
        match git.merge_no_ff(branch) {
            Ok(()) => {
                // Merge succeeded — run tests if configured
                if let Some(ref test_cmd) = config.test_command {
                    let test_result = run_tests_with_output(project_root, test_cmd);
                    if !test_result.success {
                        // Collect touched files for diagnostics
                        let touched_files = task_changed_files
                            .get(&task.id)
                            .cloned()
                            .unwrap_or_default();

                        // Capture stderr (first 50 lines)
                        let test_stderr = test_result.stderr.map(|s| truncate_lines(&s, 50));

                        // Log diagnostics
                        append_log(
                            &log_path,
                            &format!(
                                "[test-fail] Task {} ({}): tests failed after merge. Touched files: {}. Stderr: {}",
                                task.id,
                                branch,
                                touched_files.join(", "),
                                test_stderr.as_deref().unwrap_or("(none)")
                            ),
                        );

                        // Test failure: roll back the merge commit
                        let _ = git.reset_hard_head(1);
                        results.push(MergeResult {
                            task_id: task.id.clone(),
                            branch: branch.to_string(),
                            success: false,
                            conflict: false,
                            test_failure: true,
                            commit_history,
                            message: "tests failed after merge".to_string(),
                            conflicting_files: Vec::new(),
                            overlapping_tasks: Vec::new(),
                            touched_files,
                            test_stderr,
                        });
                        let _ = crate::events::emit_warn(
                            project_root,
                            crate::model::event::EventType::MergeTestFail,
                            Some(&task.id),
                            &format!("tests failed after merging '{branch}'"),
                        );
                        continue;
                    }
                }

                results.push(MergeResult {
                    task_id: task.id.clone(),
                    branch: branch.to_string(),
                    success: true,
                    conflict: false,
                    test_failure: false,
                    commit_history,
                    message: "merged successfully".to_string(),
                    conflicting_files: Vec::new(),
                    overlapping_tasks: Vec::new(),
                    touched_files: Vec::new(),
                    test_stderr: None,
                });
                let _ = crate::events::emit_info(
                    project_root,
                    crate::model::event::EventType::MergeSuccess,
                    &task.id,
                    &format!("merged branch '{branch}' successfully"),
                );
            }
            Err(_) => {
                // Merge failed — get conflicting files before aborting
                let conflicting_files = git.conflicting_files().unwrap_or_default();

                // Cross-reference: which other tasks touched these conflicting files?
                let overlapping_tasks: Vec<String> = task_changed_files
                    .iter()
                    .filter(|(id, _)| *id != &task.id)
                    .filter(|(_, files)| files.iter().any(|f| conflicting_files.contains(f)))
                    .map(|(id, _)| id.clone())
                    .collect();

                // Log conflict diagnostics
                append_log(
                    &log_path,
                    &format!(
                        "[conflict] Conflict merging {}: {} conflicts with changes from {}",
                        branch,
                        conflicting_files.join(", "),
                        if overlapping_tasks.is_empty() {
                            "(unknown)".to_string()
                        } else {
                            overlapping_tasks.join(", ")
                        }
                    ),
                );

                let _ = git.merge_abort();
                results.push(MergeResult {
                    task_id: task.id.clone(),
                    branch: branch.to_string(),
                    success: false,
                    conflict: true,
                    test_failure: false,
                    commit_history,
                    message: format!("merge conflict on branch '{branch}'"),
                    conflicting_files,
                    overlapping_tasks,
                    touched_files: Vec::new(),
                    test_stderr: None,
                });
                let _ = crate::events::emit_warn(
                    project_root,
                    crate::model::event::EventType::MergeConflict,
                    Some(&task.id),
                    &format!("merge conflict on branch '{branch}'"),
                );
            }
        }
    }

    Ok(results)
}

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------

/// Load orchestrator config: prefer the run-level snapshot, fall back to project config.
fn load_config(paths: &OrchestratorPaths, run_paths: &RunPaths) -> Result<OrchestratorConfig> {
    let snapshot = run_paths.config_snapshot();
    let config_path = if snapshot.is_file() {
        snapshot
    } else {
        paths.config()
    };

    let content = std::fs::read_to_string(&config_path)
        .with_context(|| format!("failed to read config: {}", config_path.display()))?;
    let config: OrchestratorConfig =
        serde_json::from_str(&content).context("failed to parse orchestrator config")?;
    Ok(config)
}

/// Read all task briefs in the active run, filter to writer classification,
/// and sort by dependency order (topological: no-deps first, then dependents,
/// id as tiebreaker).
fn collect_writer_tasks_ordered(run_paths: &RunPaths) -> Result<Vec<TaskBriefFrontmatter>> {
    let tasks_dir = run_paths.tasks_dir();
    if !tasks_dir.is_dir() {
        return Ok(Vec::new());
    }

    let mut writers: Vec<TaskBriefFrontmatter> = Vec::new();

    for entry in std::fs::read_dir(&tasks_dir)
        .with_context(|| format!("failed to read tasks dir: {}", tasks_dir.display()))?
    {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("md") {
            continue;
        }

        match load_task_brief(&path) {
            Ok(brief) if brief.classification == Classification::Writer => {
                writers.push(brief);
            }
            Ok(_) => {} // reader task, skip
            Err(e) => {
                eprintln!(
                    "WARNING: skipping {}: {e}",
                    path.file_name().unwrap_or_default().to_string_lossy()
                );
            }
        }
    }

    // Topological sort: tasks with no depends_on first, then those that depend on others.
    // Within each group, sort by id for deterministic ordering.
    plan::topo_sort(&mut writers);

    Ok(writers)
}

struct TestOutput {
    success: bool,
    stderr: Option<String>,
}

/// Run the configured test command and capture both success status and stderr.
fn run_tests_with_output(project_root: &Path, test_cmd: &str) -> TestOutput {
    let output = Command::new("sh")
        .arg("-c")
        .arg(test_cmd)
        .current_dir(project_root)
        .output();

    match output {
        Ok(o) => TestOutput {
            success: o.status.success(),
            stderr: if o.status.success() {
                None
            } else {
                Some(String::from_utf8_lossy(&o.stderr).to_string())
            },
        },
        Err(e) => TestOutput {
            success: false,
            stderr: Some(format!("failed to execute test command: {e}")),
        },
    }
}

/// Truncate a string to at most `max_lines` lines.
fn truncate_lines(s: &str, max_lines: usize) -> String {
    let lines: Vec<&str> = s.lines().take(max_lines).collect();
    lines.join("\n")
}

/// Append a line to the integration log file.
fn append_log(log_path: &std::path::Path, message: &str) {
    use std::io::Write;
    if let Ok(mut f) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(log_path)
    {
        let _ = writeln!(f, "{message}");
    }
}
