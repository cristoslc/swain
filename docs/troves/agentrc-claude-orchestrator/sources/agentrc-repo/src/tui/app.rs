use std::collections::HashMap;
use std::path::PathBuf;
use std::time::Instant;

use anyhow::{Context, Result};

use crate::commands::status::{collect_statuses, find_stale_heartbeats};
use crate::detect::{self, DetectedState};
use crate::events;
use crate::fs::bus::OrchestratorPaths;
use crate::model::config::OrchestratorConfig;
use crate::model::event::OrcEvent;
use crate::model::task::{TaskState, TaskStatus};
use crate::tmux::wrapper::Tmux;
use crate::tui::anim;

pub enum SortOrder {
    Id,
    State,
    Elapsed,
}

pub struct App {
    pub project_root: PathBuf,
    pub run_id: String,
    pub statuses: Vec<TaskStatus>,
    pub detected: HashMap<String, DetectedState>,
    pub stale_heartbeats: Vec<String>,
    pub selected: usize,
    pub sort_order: SortOrder,
    pub show_help: bool,
    pub should_quit: bool,
    pub last_refresh: Instant,
    pub config: OrchestratorConfig,
    pub orchestrator_tokens: Option<u64>,
    pub orchestrator_pane: Option<String>,
    pub anim: anim::AnimState,
    pub show_animation: bool,
    pub terminal_height: u16,
    pub show_events: bool,
    pub recent_events: Vec<OrcEvent>,
}

impl App {
    pub fn new(project_root: PathBuf) -> Result<Self> {
        let paths = OrchestratorPaths::new(&project_root);
        let config_path = paths.config();
        let config: OrchestratorConfig = if config_path.exists() {
            let content = std::fs::read_to_string(&config_path).context("failed to read config")?;
            serde_json::from_str(&content).context("failed to parse config")?
        } else {
            OrchestratorConfig::default()
        };

        let run_id = paths
            .active_run()
            .map(|r| r.run_id().to_string())
            .unwrap_or_else(|| "none".into());

        // Find orchestrator pane — look for TMUX_PANE env var from parent
        // or find the claude pane in the current window that isn't a worker
        let orchestrator_pane = std::env::var("TMUX_PANE").ok().and_then(|dashboard_pane| {
            // The dashboard pane was split from the orchestrator.
            // List panes in the same window, find the one running claude.
            let tmux = Tmux::new();
            if let Ok(panes) = tmux.list_panes_with_titles("") {
                panes
                    .into_iter()
                    .map(|(id, _)| id)
                    .find(|id| id != &dashboard_pane)
            } else {
                None
            }
        });

        let mut app = App {
            project_root,
            run_id,
            statuses: Vec::new(),
            detected: HashMap::new(),
            stale_heartbeats: Vec::new(),
            selected: 0,
            sort_order: SortOrder::Id,
            show_help: false,
            should_quit: false,
            last_refresh: Instant::now(),
            config,
            orchestrator_tokens: None,
            orchestrator_pane,
            anim: anim::AnimState::new(),
            show_animation: true,
            terminal_height: 0,
            show_events: true,
            recent_events: Vec::new(),
        };
        app.refresh();
        Ok(app)
    }

    pub fn refresh(&mut self) {
        self.statuses = collect_statuses(&self.project_root).unwrap_or_default();
        self.stale_heartbeats =
            find_stale_heartbeats(&self.project_root, self.config.heartbeat_timeout_sec)
                .unwrap_or_default();

        // Passive detection + token parsing for each task with a pane
        let tmux = Tmux::new();
        self.detected.clear();
        for s in &mut self.statuses {
            if let Some(ref pane_id) = s.pane_id {
                let scan = detect::scan_pane_full(&tmux, pane_id);
                self.detected.insert(s.id.clone(), scan.state);
                if scan.tokens.is_some() {
                    s.token_usage = scan.tokens;
                }
            }
        }

        // Scan orchestrator pane for its token usage
        if let Some(ref orc_pane) = self.orchestrator_pane {
            if let Ok(text) = tmux.capture_pane(orc_pane, 30) {
                self.orchestrator_tokens = detect::parse_tokens_from_text(&text);
            }
        }

        // Clamp selection
        if !self.statuses.is_empty() && self.selected >= self.statuses.len() {
            self.selected = self.statuses.len() - 1;
        }

        if self.show_events {
            self.recent_events = events::tail(&self.project_root, 5).unwrap_or_default();
        }

        self.last_refresh = Instant::now();

        // Update animation activity from active worker count
        self.anim.activity_level = self.active_count() as u32;
    }

    pub fn selected_status(&self) -> Option<&TaskStatus> {
        self.statuses.get(self.selected)
    }

    pub fn next(&mut self) {
        if !self.statuses.is_empty() {
            self.selected = (self.selected + 1) % self.statuses.len();
        }
    }

    pub fn previous(&mut self) {
        if !self.statuses.is_empty() {
            self.selected = if self.selected == 0 {
                self.statuses.len() - 1
            } else {
                self.selected - 1
            };
        }
    }

    pub fn cycle_sort(&mut self) {
        self.sort_order = match self.sort_order {
            SortOrder::Id => SortOrder::State,
            SortOrder::State => SortOrder::Elapsed,
            SortOrder::Elapsed => SortOrder::Id,
        };
    }

    pub fn active_count(&self) -> usize {
        self.statuses
            .iter()
            .filter(|s| {
                matches!(
                    s.state,
                    TaskState::InProgress | TaskState::Spawning | TaskState::Ready
                )
            })
            .count()
    }

    pub fn completed_count(&self) -> usize {
        self.statuses
            .iter()
            .filter(|s| s.state == TaskState::Completed)
            .count()
    }

    pub fn failed_count(&self) -> usize {
        self.statuses
            .iter()
            .filter(|s| matches!(s.state, TaskState::Failed | TaskState::Aborted))
            .count()
    }

    pub fn total_tokens(&self) -> u64 {
        self.statuses.iter().filter_map(|s| s.token_usage).sum()
    }

    pub fn handle_click(&mut self, _col: u16, row: u16) {
        // Map screen Y to a status index.
        // We iterate statuses in render order (active first, then graveyard)
        // and check which table region the click falls into.
        //
        // Rather than computing exact layout offsets (fragile), just map
        // based on position relative to the full status list. Count active
        // vs graveyard and use simple heuristics.

        let active_count = self
            .statuses
            .iter()
            .filter(|s| {
                !matches!(
                    s.state,
                    TaskState::Completed | TaskState::Failed | TaskState::Aborted
                )
            })
            .count();
        let graveyard_count = self.statuses.len() - active_count;

        use crate::tui::ui::anim_height;
        let anim_h = anim_height(self.show_animation, self.terminal_height);

        // Workers table data starts after: header(3) + anim + workers_border(1) + column_header(1)
        let workers_data_y = 3 + anim_h + 1 + 1;

        // Try active region first
        if row >= workers_data_y && (row - workers_data_y) < active_count as u16 {
            self.selected = (row - workers_data_y) as usize;
            return;
        }

        // Graveyard data starts after workers box. Estimate: workers box height
        // is the area between workers_data_y and the graveyard box.
        // The graveyard box has border(1) + header(1) before data rows.
        if graveyard_count > 0 {
            // Walk backward from the bottom: detail(4) + keys(1) = 5 from bottom,
            // then graveyard data rows, then graveyard header(1) + border(1)
            let terminal_h = self.terminal_height;
            let graveyard_box_bottom = terminal_h.saturating_sub(5); // above detail+keys
            let graveyard_data_end = graveyard_box_bottom.saturating_sub(1); // inside bottom border
            let graveyard_data_start = graveyard_data_end.saturating_sub(graveyard_count as u16);

            if row >= graveyard_data_start && row < graveyard_data_end {
                let gy_index = (row - graveyard_data_start) as usize;
                self.selected = active_count + gy_index;
                return;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::event::OrcEvent;
    use crate::model::task::{TaskState, TaskStatus};
    use chrono::Utc;

    /// Create a minimal App for testing without file I/O.
    fn test_app(statuses: Vec<TaskStatus>) -> App {
        App {
            project_root: PathBuf::from("/tmp/test"),
            run_id: "test".into(),
            statuses,
            detected: HashMap::new(),
            stale_heartbeats: Vec::new(),
            selected: 0,
            sort_order: SortOrder::Id,
            show_help: false,
            should_quit: false,
            last_refresh: Instant::now(),
            config: OrchestratorConfig::default(),
            orchestrator_tokens: None,
            orchestrator_pane: None,
            anim: anim::AnimState::new(),
            show_animation: true,
            terminal_height: 40,
            show_events: true,
            recent_events: Vec::new(),
        }
    }

    fn make_status(id: &str, state: TaskState) -> TaskStatus {
        TaskStatus {
            id: id.to_string(),
            pane_id: None,
            pane_title: None,
            state,
            phase: None,
            started_at: None,
            updated_at: Utc::now(),
            last_message: None,
            result_path: None,
            branch: None,
            redispatch_count: 0,
            phase_history: Vec::new(),
            token_usage: None,
        }
    }

    #[test]
    fn click_selects_row() {
        let mut app = test_app(vec![
            make_status("001", TaskState::InProgress),
            make_status("002", TaskState::InProgress),
            make_status("003", TaskState::InProgress),
        ]);
        // terminal_height=40, show_animation=true -> anim_height=12
        // data_start_y = 3 + 12 + 1 + 1 = 17

        app.handle_click(5, 17);
        assert_eq!(app.selected, 0);

        app.handle_click(5, 18);
        assert_eq!(app.selected, 1);

        app.handle_click(5, 19);
        assert_eq!(app.selected, 2);

        // Above data area -- no change
        app.handle_click(5, 10);
        assert_eq!(app.selected, 2);

        // Beyond row count -- no change
        app.handle_click(5, 50);
        assert_eq!(app.selected, 2);
    }

    #[test]
    fn click_with_animation_off() {
        let mut app = test_app(vec![
            make_status("001", TaskState::InProgress),
            make_status("002", TaskState::InProgress),
        ]);
        app.show_animation = false;
        // anim_height=0, data_start_y = 3 + 0 + 1 + 1 = 5

        app.handle_click(5, 5);
        assert_eq!(app.selected, 0);

        app.handle_click(5, 6);
        assert_eq!(app.selected, 1);
    }

    #[test]
    fn click_ignores_graveyard_rows() {
        let mut app = test_app(vec![
            make_status("001", TaskState::InProgress),
            make_status("002", TaskState::Completed), // graveyard
            make_status("003", TaskState::InProgress),
        ]);
        // Only 2 active rows (001 and 003)
        app.show_animation = false;
        // data_start_y = 5

        app.handle_click(5, 5);
        assert_eq!(app.selected, 0);

        app.handle_click(5, 6);
        assert_eq!(app.selected, 1);

        // Row index 2 is beyond active count
        app.handle_click(5, 7);
        assert_eq!(app.selected, 1); // unchanged
    }
}
