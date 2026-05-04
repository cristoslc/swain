use crate::model::task::TaskState;
use crate::tui::app::App;

/// Actions that shell out need to exit the TUI first, run, then re-enter.
/// We return the command to run so the main loop can handle terminal restore/re-init.
pub enum Action {
    None,
    Shell(Vec<String>),
}

fn is_graveyard(state: &TaskState) -> bool {
    matches!(
        state,
        TaskState::Completed | TaskState::Failed | TaskState::Aborted
    )
}

pub fn handle_key(app: &App, key: char) -> Action {
    let selected = match app.selected_status() {
        Some(s) => s,
        None => return Action::None,
    };

    let dead = is_graveyard(&selected.state);

    match key {
        // Zoom — only if pane exists and task is alive
        'z' => {
            if dead {
                return Action::None;
            }
            if let Some(ref pane_id) = selected.pane_id {
                Action::Shell(vec![
                    "tmux".into(),
                    "select-pane".into(),
                    "-t".into(),
                    pane_id.clone(),
                ])
            } else {
                Action::None
            }
        }
        // Teardown — only alive tasks
        't' => {
            if dead {
                return Action::None;
            }
            Action::Shell(vec![
                "agentrc".into(),
                "teardown".into(),
                selected.id.clone(),
                "--force".into(),
            ])
        }
        // Respawn — only failed/aborted (graveyard but not completed)
        'r' => {
            if matches!(selected.state, TaskState::Failed | TaskState::Aborted) {
                Action::Shell(vec![
                    "agentrc".into(),
                    "respawn".into(),
                    selected.id.clone(),
                ])
            } else {
                Action::None
            }
        }
        // Amend — only alive tasks with a pane
        'a' => {
            if dead {
                return Action::None;
            }
            Action::Shell(vec![
                "agentrc".into(),
                "amend".into(),
                selected.id.clone(),
                "--message".into(),
                "Brief updated by orchestrator".into(),
            ])
        }
        // Integrate + Checkpoint — global actions, always allowed
        'i' => Action::Shell(vec!["agentrc".into(), "integrate".into()]),
        'c' => Action::Shell(vec!["agentrc".into(), "checkpoint".into(), "save".into()]),
        _ => Action::None,
    }
}
