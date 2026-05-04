use std::path::Path;

use anyhow::{Context, Result};

use crate::commands::spawn::load_task_brief;
use crate::fs::bus::OrchestratorPaths;
use crate::model::error::AppError;
use crate::model::task::TaskBriefFrontmatter;

/// Result of validating a task plan DAG.
#[derive(Debug)]
pub struct PlanValidation {
    pub task_count: usize,
    pub errors: Vec<String>,
}

impl PlanValidation {
    pub fn is_valid(&self) -> bool {
        self.errors.is_empty()
    }
}

/// CLI entry point for `agentrc plan validate`.
pub fn run() -> Result<()> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    let validation = validate_in(&cwd)?;

    if validation.is_valid() {
        println!("Plan valid: {} tasks, no cycles", validation.task_count);
        Ok(())
    } else {
        for err in &validation.errors {
            eprintln!("Error: {err}");
        }
        anyhow::bail!("Plan invalid: {} error(s) found", validation.errors.len())
    }
}

/// Validate the task DAG in the active run.
pub fn validate_in(project_root: &Path) -> Result<PlanValidation> {
    let paths = OrchestratorPaths::new(project_root);
    let active = paths.active_run().ok_or(AppError::NoActiveRun)?;
    let tasks_dir = active.tasks_dir();

    if !tasks_dir.is_dir() {
        return Ok(PlanValidation {
            task_count: 0,
            errors: vec!["No tasks found: tasks directory does not exist".to_string()],
        });
    }

    let mut briefs: Vec<TaskBriefFrontmatter> = Vec::new();

    for entry in std::fs::read_dir(&tasks_dir)
        .with_context(|| format!("failed to read tasks dir: {}", tasks_dir.display()))?
    {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("md") {
            continue;
        }

        match load_task_brief(&path) {
            Ok(brief) => briefs.push(brief),
            Err(e) => {
                return Err(e)
                    .with_context(|| format!("failed to parse task brief: {}", path.display()));
            }
        }
    }

    Ok(validate_briefs(&briefs))
}

/// Validate a set of task briefs for DAG correctness.
pub fn validate_briefs(briefs: &[TaskBriefFrontmatter]) -> PlanValidation {
    use std::collections::HashSet;

    let mut errors: Vec<String> = Vec::new();

    if briefs.is_empty() {
        return PlanValidation {
            task_count: 0,
            errors: vec!["No tasks found".to_string()],
        };
    }

    // Check: duplicate IDs
    let mut seen = HashSet::new();
    for brief in briefs {
        if !seen.insert(&brief.id) {
            errors.push(format!("Duplicate task ID: {}", brief.id));
        }
    }

    // Check: self-references
    for brief in briefs {
        if brief.depends_on.contains(&brief.id) {
            errors.push(format!(
                "Self-reference: task {} depends on itself",
                brief.id
            ));
        }
    }

    // Check: self-references are excluded from dep checking below
    // so skip self-refs in dep lookups

    // Check: missing dependencies
    let all_ids: HashSet<&str> = briefs.iter().map(|b| b.id.as_str()).collect();
    for brief in briefs {
        for dep in &brief.depends_on {
            if dep == &brief.id {
                continue; // already reported as self-reference
            }
            if !all_ids.contains(dep.as_str()) {
                errors.push(format!(
                    "Missing dependency: task {} depends on {}, which does not exist",
                    brief.id, dep
                ));
            }
        }
    }

    // Check: cycles (only if no structural errors so far)
    if errors.is_empty() {
        if let Some(cycle) = detect_cycle(briefs) {
            errors.push(format!("Cycle detected: {cycle}"));
        }
    }

    PlanValidation {
        task_count: briefs.len(),
        errors,
    }
}

/// Detect a cycle in the dependency graph using Kahn's algorithm.
///
/// Returns `None` if no cycle, or `Some("A → B → C → A")` describing the cycle.
fn detect_cycle(briefs: &[TaskBriefFrontmatter]) -> Option<String> {
    use std::collections::{HashMap, HashSet, VecDeque};

    let ids: Vec<&str> = briefs.iter().map(|b| b.id.as_str()).collect();
    let id_set: HashSet<&str> = ids.iter().copied().collect();

    // Build in-degree map and adjacency list
    // Edge direction: dep -> dependent (dep must come before dependent)
    let mut in_degree: HashMap<&str, usize> = HashMap::new();
    let mut dependents: HashMap<&str, Vec<&str>> = HashMap::new();

    for &id in &ids {
        in_degree.insert(id, 0);
        dependents.entry(id).or_default();
    }

    for brief in briefs {
        for dep in &brief.depends_on {
            if id_set.contains(dep.as_str()) {
                *in_degree.get_mut(brief.id.as_str()).unwrap() += 1;
                dependents
                    .get_mut(dep.as_str())
                    .unwrap()
                    .push(brief.id.as_str());
            }
        }
    }

    // Kahn's: start with zero in-degree nodes
    let mut queue: VecDeque<&str> = VecDeque::new();
    for (&id, &deg) in &in_degree {
        if deg == 0 {
            queue.push_back(id);
        }
    }

    let mut processed = 0usize;
    while let Some(id) = queue.pop_front() {
        processed += 1;
        if let Some(deps) = dependents.get(id) {
            for &dep in deps {
                let deg = in_degree.get_mut(dep).unwrap();
                *deg -= 1;
                if *deg == 0 {
                    queue.push_back(dep);
                }
            }
        }
    }

    if processed == ids.len() {
        return None; // no cycle
    }

    // Cycle exists — trace it for a readable error message
    // Collect nodes still in the cycle (in-degree > 0)
    let remaining: HashSet<&str> = in_degree
        .iter()
        .filter(|(_, &deg)| deg > 0)
        .map(|(&id, _)| id)
        .collect();

    // Build adjacency for remaining nodes only (depends_on edges)
    let brief_map: HashMap<&str, &TaskBriefFrontmatter> =
        briefs.iter().map(|b| (b.id.as_str(), b)).collect();

    // Walk the cycle starting from the smallest remaining ID (deterministic)
    let mut sorted_remaining: Vec<&str> = remaining.iter().copied().collect();
    sorted_remaining.sort();
    let start = sorted_remaining[0];

    let mut path = vec![start];
    let mut current = start;

    loop {
        let brief = brief_map[current];
        // Follow a dependency edge that stays within the cycle
        let next = brief
            .depends_on
            .iter()
            .find(|d| remaining.contains(d.as_str()))
            .unwrap();

        if next.as_str() == start {
            path.push(start);
            break;
        }
        path.push(next.as_str());
        current = next.as_str();
    }

    Some(path.join(" \u{2192} "))
}

/// Topological sort for task briefs based on `depends_on`.
///
/// Uses Kahn's algorithm: emit tasks whose dependencies have all been emitted,
/// with id as tiebreaker. Shared between `plan validate` and `integrate`.
pub fn topo_sort(tasks: &mut Vec<TaskBriefFrontmatter>) {
    let ids: Vec<String> = tasks.iter().map(|t| t.id.clone()).collect();
    let mut sorted: Vec<TaskBriefFrontmatter> = Vec::with_capacity(tasks.len());
    let mut remaining: Vec<TaskBriefFrontmatter> = std::mem::take(tasks);

    remaining.sort_by(|a, b| a.id.cmp(&b.id));

    let mut emitted: Vec<String> = Vec::new();

    while !remaining.is_empty() {
        let mut ready_indices: Vec<usize> = Vec::new();
        for (i, task) in remaining.iter().enumerate() {
            let deps_satisfied = task
                .depends_on
                .iter()
                .all(|dep| emitted.contains(dep) || !ids.contains(dep));
            if deps_satisfied {
                ready_indices.push(i);
            }
        }

        if ready_indices.is_empty() {
            // Cycle or unresolvable — append rest by id order
            remaining.sort_by(|a, b| a.id.cmp(&b.id));
            sorted.append(&mut remaining);
            break;
        }

        for &idx in ready_indices.iter().rev() {
            let task = remaining.remove(idx);
            emitted.push(task.id.clone());
            sorted.push(task);
        }
    }

    *tasks = sorted;
}
