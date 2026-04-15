use chrono::Utc;
use ratatui::prelude::*;
use ratatui::widgets::{Block, BorderType, Borders, Cell, Row, Table, TableState};

use crate::detect::DetectedState;
use crate::model::task::TaskState;
use crate::tui::app::App;
use crate::tui::theme as t;

pub fn format_tokens(tokens: u64) -> String {
    if tokens >= 1_000_000 {
        format!("{:.1}M", tokens as f64 / 1_000_000.0)
    } else if tokens >= 1_000 {
        format!("{:.1}k", tokens as f64 / 1_000.0)
    } else {
        format!("{tokens}")
    }
}

fn state_symbol(state: &TaskState) -> &'static str {
    match state {
        TaskState::Spawning => "◌",
        TaskState::Ready => "○",
        TaskState::InProgress => "●",
        TaskState::Blocked => "◼",
        TaskState::Completed => "✓",
        TaskState::Failed => "✗",
        TaskState::Aborted => "⊘",
    }
}

fn state_color(state: &TaskState) -> Color {
    match state {
        TaskState::InProgress => t::OK,
        TaskState::Completed => t::DONE,
        TaskState::Failed | TaskState::Aborted => t::ERR,
        TaskState::Blocked => t::WARN,
        TaskState::Spawning => t::TEXT_MUTED,
        TaskState::Ready => t::TEXT,
    }
}

fn activity_symbol(state: &DetectedState) -> &'static str {
    match state {
        DetectedState::Thinking => "◐",
        DetectedState::ToolUse => "⚙",
        DetectedState::Running => "▶",
        DetectedState::Idle => "◇",
        DetectedState::NeedsInput => "⚠",
        DetectedState::RateLimited => "⏳",
        DetectedState::Errored => "✗",
        DetectedState::Dead => "☠",
        DetectedState::Unknown => "·",
    }
}

fn activity_color(state: &DetectedState) -> Color {
    match state {
        DetectedState::Thinking => t::PRIMARY,
        DetectedState::ToolUse => t::DONE,
        DetectedState::Running => t::OK,
        DetectedState::Idle => t::TEXT_MUTED,
        DetectedState::NeedsInput => t::ERR,
        DetectedState::RateLimited => t::WARN,
        DetectedState::Errored => t::ERR,
        DetectedState::Dead => t::ERR,
        DetectedState::Unknown => t::TEXT_MUTED,
    }
}

fn is_graveyard(state: &TaskState) -> bool {
    matches!(
        state,
        TaskState::Completed | TaskState::Failed | TaskState::Aborted
    )
}

fn build_row(
    s: &crate::model::task::TaskStatus,
    detected: DetectedState,
    max_tokens: u64,
    now: chrono::DateTime<chrono::Utc>,
    graveyard: bool,
    stale: bool,
) -> Row<'static> {
    let dim = if graveyard {
        Modifier::DIM
    } else {
        Modifier::empty()
    };

    let id_style = if graveyard {
        Style::default().fg(t::TEXT_MUTED)
    } else {
        Style::default().fg(t::TEXT).add_modifier(Modifier::BOLD)
    };
    let id_cell = Cell::from(Span::styled(s.id.clone(), id_style));

    let sc = state_color(&s.state);
    let state_cell = Cell::from(Line::from(vec![
        Span::styled(
            format!("{} ", state_symbol(&s.state)),
            Style::default().fg(sc).add_modifier(Modifier::BOLD | dim),
        ),
        Span::styled(
            format!("{}", s.state),
            if graveyard {
                Style::default().fg(t::TEXT_MUTED).add_modifier(dim)
            } else {
                Style::default().fg(sc)
            },
        ),
    ]));

    let activity_cell = if graveyard {
        Cell::from(Span::styled(
            format!("{} {}", activity_symbol(&detected), detected),
            Style::default().fg(t::TEXT_MUTED).add_modifier(dim),
        ))
    } else {
        let ac = activity_color(&detected);
        let act_mod = if detected == DetectedState::NeedsInput {
            Modifier::BOLD
        } else {
            Modifier::empty()
        };
        Cell::from(Line::from(vec![
            Span::styled(
                format!("{} ", activity_symbol(&detected)),
                Style::default().fg(ac).add_modifier(act_mod),
            ),
            Span::styled(format!("{detected}"), Style::default().fg(ac)),
        ]))
    };

    let (token_text, token_style) = match s.token_usage {
        Some(usage) => {
            let ratio = if max_tokens > 0 {
                usage as f64 / max_tokens as f64
            } else {
                0.0
            };
            let color = if graveyard {
                t::TEXT_MUTED
            } else if ratio > 0.8 {
                t::ERR
            } else if ratio > 0.5 {
                t::WARN
            } else {
                t::ACCENT
            };
            (
                format_tokens(usage),
                Style::default().fg(color).add_modifier(dim),
            )
        }
        None => ("-".to_string(), Style::default().fg(t::TEXT_MUTED)),
    };

    let elapsed = s
        .started_at
        .map(|started| {
            let secs = (now - started).num_seconds().max(0);
            if secs < 60 {
                format!("{secs}s")
            } else if secs < 3600 {
                format!("{}m {}s", secs / 60, secs % 60)
            } else {
                format!("{}h {}m", secs / 3600, (secs % 3600) / 60)
            }
        })
        .unwrap_or_else(|| "-".into());
    let elapsed_style = Style::default().fg(t::TEXT_DIM).add_modifier(dim);

    let pane = s
        .pane_title
        .as_deref()
        .or(s.pane_id.as_deref())
        .unwrap_or("-")
        .to_string();
    let pane_style = if graveyard {
        Style::default().fg(t::TEXT_MUTED).add_modifier(dim)
    } else if stale {
        Style::default().fg(t::WARN)
    } else {
        Style::default().fg(t::PANE)
    };

    Row::new(vec![
        id_cell,
        state_cell,
        activity_cell,
        Cell::from(token_text).style(token_style),
        Cell::from(elapsed).style(elapsed_style),
        Cell::from(pane).style(pane_style),
    ])
}

fn make_header() -> Row<'static> {
    let cells = ["ID", "STATE", "ACTIVITY", "TOKENS", "ELAPSED", "PANE"]
        .iter()
        .map(|h| {
            Cell::from(*h).style(
                Style::default()
                    .fg(t::TEXT_DIM)
                    .add_modifier(Modifier::BOLD),
            )
        });
    Row::new(cells).bottom_margin(0)
}

const WIDTHS: [Constraint; 6] = [
    Constraint::Length(5),
    Constraint::Length(14),
    Constraint::Length(14),
    Constraint::Length(8),
    Constraint::Length(9),
    Constraint::Min(15),
];

pub fn render_workers(app: &App, area: Rect, buf: &mut Buffer) {
    let now = Utc::now();
    let max_tokens = app
        .statuses
        .iter()
        .filter_map(|s| s.token_usage)
        .max()
        .unwrap_or(0);

    let rows: Vec<Row> = app
        .statuses
        .iter()
        .filter(|s| !is_graveyard(&s.state))
        .map(|s| {
            let detected = app
                .detected
                .get(&s.id)
                .copied()
                .unwrap_or(DetectedState::Unknown);
            let stale = app.stale_heartbeats.contains(&s.id);
            build_row(s, detected, max_tokens, now, false, stale)
        })
        .collect();

    let block = Block::default()
        .title(Span::styled(
            " Workers ",
            Style::default().fg(t::PRIMARY).add_modifier(Modifier::BOLD),
        ))
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .border_style(Style::default().fg(t::BORDER));

    let table = Table::new(rows, WIDTHS)
        .header(make_header())
        .block(block)
        .row_highlight_style(
            Style::default()
                .bg(t::HIGHLIGHT_BG)
                .add_modifier(Modifier::BOLD),
        );

    let active_count = app
        .statuses
        .iter()
        .filter(|s| !is_graveyard(&s.state))
        .count();
    let mut state = TableState::default();
    if app.selected < active_count {
        state.select(Some(app.selected));
    }

    StatefulWidget::render(table, area, buf, &mut state);
}

pub fn render_graveyard(app: &App, area: Rect, buf: &mut Buffer) {
    let now = Utc::now();
    let max_tokens = app
        .statuses
        .iter()
        .filter_map(|s| s.token_usage)
        .max()
        .unwrap_or(0);

    let rows: Vec<Row> = app
        .statuses
        .iter()
        .filter(|s| is_graveyard(&s.state))
        .map(|s| {
            let detected = app
                .detected
                .get(&s.id)
                .copied()
                .unwrap_or(DetectedState::Unknown);
            let stale = app.stale_heartbeats.contains(&s.id);
            build_row(s, detected, max_tokens, now, true, stale)
        })
        .collect();

    let block = Block::default()
        .title(Span::styled(
            " Graveyard 👻 ",
            Style::default().fg(t::TEXT_MUTED),
        ))
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .border_style(Style::default().fg(t::TEXT_MUTED));

    let table = Table::new(rows, WIDTHS)
        .header(make_header())
        .block(block)
        .row_highlight_style(
            Style::default()
                .bg(t::GRAVEYARD_BG)
                .add_modifier(Modifier::DIM),
        );

    let active_count = app
        .statuses
        .iter()
        .filter(|s| !is_graveyard(&s.state))
        .count();
    let mut state = TableState::default();
    if app.selected >= active_count {
        let graveyard_index = app.selected - active_count;
        state.select(Some(graveyard_index));
    }
    StatefulWidget::render(table, area, buf, &mut state);
}
