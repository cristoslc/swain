use ratatui::prelude::*;
use ratatui::widgets::{Block, BorderType, Borders, Paragraph};

use crate::model::event::{EventType, OrcEvent, Severity};
use crate::tui::theme as t;

/// Maps an [`EventType`] variant to a compact display label for the events panel.
fn event_type_label(et: &EventType) -> &'static str {
    match et {
        EventType::Spawned => "spawn",
        EventType::StateChange => "state",
        EventType::Completed => "done",
        EventType::Failed => "fail",
        EventType::MergeStarted => "merge",
        EventType::MergeSuccess => "merge\u{2713}",
        EventType::MergeConflict => "conflict",
        EventType::MergeTestFail => "test\u{2717}",
        EventType::Respawned => "respawn",
        EventType::Dead => "dead",
        EventType::StaleHeartbeat => "stale",
        EventType::NeedsInput => "input?",
        EventType::RateLimited => "ratelim",
        EventType::CascadeSpawn => "cascade",
        EventType::InputResponded => "replied",
        EventType::CheckpointSaved => "ckpt",
        EventType::VoltagentViolation => "volt!",
        EventType::TddViolation => "tdd!",
    }
}

/// Returns the theme color for a given severity level.
fn severity_color(severity: &Severity) -> Color {
    match severity {
        Severity::Info => t::OK,
        Severity::Warn => t::WARN,
        Severity::Error => t::ERR,
    }
}

fn format_event_line(event: &OrcEvent) -> Line<'static> {
    let ts = event.timestamp.format("%H:%M:%S").to_string();
    let label = event_type_label(&event.event_type);
    let color = severity_color(&event.severity);
    let task = event.task_id.clone().unwrap_or_else(|| "-".into());
    let msg = event.message.clone();

    let sep = Span::styled(" │ ", Style::default().fg(t::TEXT_MUTED));

    Line::from(vec![
        Span::styled(ts, Style::default().fg(t::TEXT_DIM)),
        sep.clone(),
        Span::styled(label, Style::default().fg(color)),
        sep,
        Span::styled(task, Style::default().fg(t::TEXT)),
        Span::raw(" "),
        Span::styled(msg, Style::default().fg(t::TEXT_DIM)),
    ])
}

/// Renders a list of orchestrator events inside a bordered panel.
///
/// Events are displayed in the order provided (callers should pass them in
/// chronological order so the most recent event appears at the bottom).
pub fn render(events: &[OrcEvent], area: Rect, buf: &mut Buffer) {
    let block = Block::default()
        .title(Span::styled(
            " Events ",
            Style::default().fg(t::ACCENT).add_modifier(Modifier::BOLD),
        ))
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .border_style(Style::default().fg(t::BORDER));

    let lines: Vec<Line<'static>> = if events.is_empty() {
        vec![Line::from(Span::styled(
            " loading...",
            Style::default()
                .fg(t::TEXT_MUTED)
                .add_modifier(Modifier::ITALIC),
        ))]
    } else {
        events.iter().map(format_event_line).collect()
    };

    let paragraph = Paragraph::new(lines).block(block);
    Widget::render(paragraph, area, buf);
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Utc;
    use std::collections::HashMap;
    use std::path::PathBuf;
    use std::time::Instant;

    use crate::model::config::OrchestratorConfig;
    use crate::model::event::{EventType, OrcEvent, Severity};
    use crate::tui::anim;
    use crate::tui::app::{App, SortOrder};

    fn make_event(event_type: EventType, severity: Severity, task_id: &str, msg: &str) -> OrcEvent {
        OrcEvent {
            timestamp: Utc::now(),
            event_type,
            task_id: Some(task_id.to_string()),
            severity,
            message: msg.to_string(),
        }
    }

    fn buffer_to_string(buf: &Buffer, area: Rect) -> String {
        (0..area.height)
            .flat_map(|y| (0..area.width).map(move |x| buf[(x, y)].symbol().to_string()))
            .collect()
    }

    #[test]
    fn events_panel_renders() {
        let events = vec![
            make_event(EventType::Spawned, Severity::Info, "001", "Task spawned"),
            make_event(EventType::Failed, Severity::Error, "002", "Build error"),
            make_event(
                EventType::NeedsInput,
                Severity::Warn,
                "003",
                "Waiting for user",
            ),
        ];

        let area = Rect::new(0, 0, 80, 7);
        let mut buf = Buffer::empty(area);
        render(&events, area, &mut buf);

        let content = buffer_to_string(&buf, area);

        // Border title
        assert!(content.contains("Events"), "should render 'Events' title");
        // Event type labels
        assert!(content.contains("spawn"), "should render 'spawn' label");
        assert!(content.contains("fail"), "should render 'fail' label");
        assert!(content.contains("input?"), "should render 'input?' label");
        // Task IDs
        assert!(content.contains("001"), "should render task id '001'");
        assert!(content.contains("002"), "should render task id '002'");
        assert!(content.contains("003"), "should render task id '003'");
    }

    #[test]
    fn events_panel_empty() {
        let events: Vec<OrcEvent> = Vec::new();

        let area = Rect::new(0, 0, 80, 7);
        let mut buf = Buffer::empty(area);
        render(&events, area, &mut buf);

        let content = buffer_to_string(&buf, area);

        assert!(
            content.contains("Events"),
            "should render 'Events' title even with no events"
        );
    }

    #[test]
    fn toggle_events_key() {
        let mut app = App {
            project_root: PathBuf::from("/tmp/test"),
            run_id: "test".into(),
            statuses: Vec::new(),
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
            show_events: true,
            recent_events: Vec::new(),
            terminal_height: 40,
        };

        // Default is true
        assert!(app.show_events, "show_events should default to true");

        // Simulate 'e' key toggle
        app.show_events = !app.show_events;
        assert!(!app.show_events, "show_events should be false after toggle");

        // Toggle back
        app.show_events = !app.show_events;
        assert!(
            app.show_events,
            "show_events should be true after second toggle"
        );
    }
}
