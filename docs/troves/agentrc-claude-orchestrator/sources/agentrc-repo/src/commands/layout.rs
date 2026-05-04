use crate::fs::bus::OrchestratorPaths;
use crate::model::config::OrchestratorConfig;
use crate::tmux::wrapper::Tmux;
use anyhow::{Context, Result};

/// An action the collate algorithm wants to perform.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CollateAction {
    /// Create a new tmux window with the given name.
    CreateWindow(String),
    /// Move a pane to a target window.
    MovePane { pane_id: String, target: String },
    /// Apply tiled layout to a window.
    Tile(String),
}

/// Pure function: compute which actions are needed to distribute `panes` across
/// windows such that each window has at most `workers_per_window` panes.
///
/// `existing_windows` lists the worker windows that already exist (e.g.
/// `["workers", "workers-2"]`). The algorithm reuses existing windows before
/// creating new ones.
pub fn compute_collation(
    panes: &[String],
    existing_windows: &[String],
    workers_per_window: u32,
) -> Vec<CollateAction> {
    let wpw = workers_per_window as usize;
    let total = panes.len();

    if total == 0 {
        return Vec::new();
    }

    let windows_needed = total.div_ceil(wpw);
    let mut actions = Vec::new();

    // Build the list of window names we'll use (reuse existing, then create new)
    let mut window_names: Vec<String> = Vec::with_capacity(windows_needed);

    // The first window is always the primary "workers" window
    if let Some(first) = existing_windows.first() {
        window_names.push(first.clone());
    } else {
        window_names.push("workers".into());
    }

    // For additional windows, reuse existing workers-N or create new ones
    for i in 2..=windows_needed {
        let name = format!("workers-{}", i);
        if !existing_windows.contains(&name) {
            actions.push(CollateAction::CreateWindow(name.clone()));
        }
        window_names.push(name);
    }

    // Distribute panes: first `wpw` stay in the first window, rest get moved
    for (idx, pane) in panes.iter().enumerate() {
        let target_window_idx = idx / wpw;
        if target_window_idx > 0 && target_window_idx < window_names.len() {
            actions.push(CollateAction::MovePane {
                pane_id: pane.clone(),
                target: window_names[target_window_idx].clone(),
            });
        }
    }

    // Tile all windows that have panes
    for name in &window_names {
        actions.push(CollateAction::Tile(name.clone()));
    }

    actions
}

/// CLI entry
pub fn run(mode: &str) -> Result<()> {
    let tmux = Tmux::new();
    match mode {
        "tile" => tile(&tmux),
        "collate" => collate(&tmux),
        _ => anyhow::bail!("unknown layout mode: {}", mode),
    }
}

fn tile(tmux: &Tmux) -> Result<()> {
    let windows = tmux.list_windows()?;
    for w in &windows {
        if w.starts_with("workers") {
            tmux.select_layout_tiled(w)?;
        }
    }
    println!("Retiled all worker windows.");
    Ok(())
}

fn load_config() -> Result<OrchestratorConfig> {
    let cwd = std::env::current_dir().context("cannot determine current directory")?;
    let paths = OrchestratorPaths::new(&cwd);
    let config_path = paths.config();
    if config_path.exists() {
        let content = std::fs::read_to_string(&config_path)
            .with_context(|| format!("failed to read config: {}", config_path.display()))?;
        serde_json::from_str(&content).context("failed to parse orchestrator config")
    } else {
        Ok(OrchestratorConfig::default())
    }
}

fn collate(tmux: &Tmux) -> Result<()> {
    let config = load_config()?;

    // Gather all worker windows and their panes
    let all_windows = tmux.list_windows()?;
    let worker_windows: Vec<String> = all_windows
        .into_iter()
        .filter(|w| w == "workers" || w.starts_with("workers-"))
        .collect();

    if worker_windows.is_empty() {
        println!("No worker windows found.");
        return Ok(());
    }

    // Collect all panes across all worker windows
    let mut all_panes = Vec::new();
    for w in &worker_windows {
        let panes = tmux.list_panes(w)?;
        all_panes.extend(panes);
    }

    // Compute what needs to happen
    let actions = compute_collation(&all_panes, &worker_windows, config.workers_per_window);

    // Execute actions
    for action in &actions {
        match action {
            CollateAction::CreateWindow(name) => {
                tmux.new_window(name)
                    .with_context(|| format!("failed to create window {}", name))?;
            }
            CollateAction::MovePane { pane_id, target } => {
                tmux.move_pane(pane_id, target)
                    .with_context(|| format!("failed to move pane {} to {}", pane_id, target))?;
            }
            CollateAction::Tile(window) => {
                tmux.select_layout_tiled(window)
                    .with_context(|| format!("failed to tile window {}", window))?;
            }
        }
    }

    let window_count = actions
        .iter()
        .filter(|a| matches!(a, CollateAction::Tile(_)))
        .count();
    println!(
        "Collated {} panes across {} window(s).",
        all_panes.len(),
        window_count
    );
    Ok(())
}
