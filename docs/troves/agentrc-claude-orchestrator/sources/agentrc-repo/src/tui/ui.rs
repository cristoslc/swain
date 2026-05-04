use ratatui::prelude::*;
use ratatui::widgets::Paragraph;

use crate::tui::anim;
use crate::tui::app::App;
use crate::tui::theme as t;
use crate::tui::widgets;

fn key_badge(key: &str, label: &str) -> Vec<Span<'static>> {
    vec![
        Span::styled(
            format!(" {key} "),
            Style::default()
                .fg(t::TEXT)
                .bg(t::BORDER)
                .add_modifier(Modifier::BOLD),
        ),
        Span::styled(format!("{label} "), Style::default().fg(t::TEXT_DIM)),
    ]
}

/// Compute the animation zone height based on terminal size and toggle state.
pub fn anim_height(show_animation: bool, terminal_height: u16) -> u16 {
    if !show_animation || terminal_height < 20 {
        0
    } else if terminal_height < 30 {
        5
    } else if terminal_height < 40 {
        9
    } else {
        12
    }
}

pub fn render(app: &App, frame: &mut Frame) {
    let area = frame.area();

    let anim_h = anim_height(app.show_animation, area.height);

    // Layout: header (3), animation (0-7), workers (fill), graveyard (adaptive), detail (4), keys (1)
    let graveyard_count = app
        .statuses
        .iter()
        .filter(|s| {
            matches!(
                s.state,
                crate::model::task::TaskState::Completed
                    | crate::model::task::TaskState::Failed
                    | crate::model::task::TaskState::Aborted
            )
        })
        .count();

    let graveyard_height = if graveyard_count == 0 {
        3
    } else {
        (graveyard_count as u16 + 3).min(area.height / 4)
    };

    let events_height = if app.show_events { 5 } else { 0 };

    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),                // header
            Constraint::Length(anim_h),           // animation
            Constraint::Min(4),                   // workers table
            Constraint::Length(graveyard_height), // graveyard table
            Constraint::Length(events_height),    // events panel
            Constraint::Length(4),                // detail
            Constraint::Length(1),                // key hints
        ])
        .split(area);

    widgets::header::render(app, chunks[0], frame.buffer_mut());

    if anim_h > 0 {
        anim::widget::render(&app.anim, app, chunks[1], frame.buffer_mut());
    }

    widgets::table::render_workers(app, chunks[2], frame.buffer_mut());
    widgets::table::render_graveyard(app, chunks[3], frame.buffer_mut());
    if app.show_events {
        widgets::events::render(&app.recent_events, chunks[4], frame.buffer_mut());
    }
    widgets::detail::render(app, chunks[5], frame.buffer_mut());

    // Key hints
    if app.show_help {
        let keys_line = Line::from(vec![
            Span::styled(" Press ", Style::default().fg(t::TEXT_DIM)),
            Span::styled(
                "?",
                Style::default().fg(t::ACCENT).add_modifier(Modifier::BOLD),
            ),
            Span::styled(" to close help", Style::default().fg(t::TEXT_DIM)),
        ]);
        Paragraph::new(keys_line).render(chunks[6], frame.buffer_mut());
    } else {
        let mut spans: Vec<Span> = Vec::new();
        spans.push(Span::raw(" "));
        spans.extend(key_badge("↑↓", "nav"));
        spans.extend(key_badge("z", "zoom"));
        spans.extend(key_badge("t", "tear"));
        spans.extend(key_badge("r", "spawn"));
        spans.extend(key_badge("a", "amend"));
        spans.extend(key_badge("i", "integ"));
        spans.extend(key_badge("c", "ckpt"));
        spans.extend(key_badge("s", "sort"));
        spans.extend(key_badge("d", "anim"));
        spans.extend(key_badge("D", "shape"));
        spans.extend(key_badge("?", "help"));
        spans.extend(key_badge("q", "quit"));

        Paragraph::new(Line::from(spans)).render(chunks[6], frame.buffer_mut());
    }

    if app.show_help {
        widgets::help::render(area, frame.buffer_mut());
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn anim_height_hidden_when_small_terminal() {
        assert_eq!(anim_height(true, 15), 0);
        assert_eq!(anim_height(true, 19), 0);
    }

    #[test]
    fn anim_height_5_lines_for_medium_terminal() {
        assert_eq!(anim_height(true, 20), 5);
        assert_eq!(anim_height(true, 29), 5);
    }

    #[test]
    fn anim_height_9_lines_for_large_terminal() {
        assert_eq!(anim_height(true, 30), 9);
        assert_eq!(anim_height(true, 39), 9);
    }

    #[test]
    fn anim_height_12_lines_for_very_large_terminal() {
        assert_eq!(anim_height(true, 40), 12);
        assert_eq!(anim_height(true, 100), 12);
    }

    #[test]
    fn anim_height_zero_when_toggled_off() {
        assert_eq!(anim_height(false, 40), 0);
        assert_eq!(anim_height(false, 100), 0);
    }
}
