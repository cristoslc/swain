use ratatui::prelude::*;
use ratatui::widgets::{Block, BorderType, Borders, Paragraph};

use crate::tui::app::App;
use crate::tui::theme as t;
use crate::tui::widgets::table::format_tokens;

pub fn render(app: &App, area: Rect, buf: &mut Buffer) {
    let active = app.active_count();
    let done = app.completed_count();
    let failed = app.failed_count();
    let total = app.statuses.len();
    let healthy = total.saturating_sub(app.stale_heartbeats.len());

    let worker_tokens = app.total_tokens();
    let orc_tokens = app.orchestrator_tokens.unwrap_or(0);
    let session_total = worker_tokens + orc_tokens;

    let mut spans1 = vec![
        Span::styled(
            " agentrc ",
            Style::default().fg(t::PRIMARY).add_modifier(Modifier::BOLD),
        ),
        Span::styled("│ ", Style::default().fg(t::BORDER)),
    ];

    if active > 0 {
        spans1.push(Span::styled(
            format!("● {active} active"),
            Style::default().fg(t::OK).add_modifier(Modifier::BOLD),
        ));
    } else {
        spans1.push(Span::styled("○ 0 active", Style::default().fg(t::TEXT_DIM)));
    }
    spans1.push(Span::raw("  "));

    if done > 0 {
        spans1.push(Span::styled(
            format!("✓ {done} done"),
            Style::default().fg(t::DONE),
        ));
    } else {
        spans1.push(Span::styled("✓ 0 done", Style::default().fg(t::TEXT_DIM)));
    }
    spans1.push(Span::raw("  "));

    if failed > 0 {
        spans1.push(Span::styled(
            format!("✗ {failed} fail"),
            Style::default().fg(t::ERR).add_modifier(Modifier::BOLD),
        ));
    } else {
        spans1.push(Span::styled("✗ 0 fail", Style::default().fg(t::TEXT_DIM)));
    }
    spans1.push(Span::styled("  │ ", Style::default().fg(t::BORDER)));

    let hb_style = if healthy < total {
        Style::default().fg(t::WARN)
    } else {
        Style::default().fg(t::OK)
    };
    spans1.push(Span::styled(format!("♥ {healthy}/{total}"), hb_style));

    let mut spans2: Vec<Span> = vec![Span::raw(" ")];
    if session_total > 0 {
        spans2.push(Span::styled("◆ ", Style::default().fg(t::ACCENT)));
        spans2.push(Span::styled(
            format_tokens(session_total),
            Style::default().fg(t::TEXT).add_modifier(Modifier::BOLD),
        ));
        spans2.push(Span::styled(" total", Style::default().fg(t::TEXT_DIM)));
        if orc_tokens > 0 {
            spans2.push(Span::styled("  orc:", Style::default().fg(t::TEXT_DIM)));
            spans2.push(Span::styled(
                format_tokens(orc_tokens),
                Style::default().fg(t::BRANCH),
            ));
        }
        if worker_tokens > 0 {
            spans2.push(Span::styled("  wkr:", Style::default().fg(t::TEXT_DIM)));
            spans2.push(Span::styled(
                format_tokens(worker_tokens),
                Style::default().fg(t::PRIMARY),
            ));
        }
    }

    let text = Text::from(vec![Line::from(spans1), Line::from(spans2)]);

    let block = Block::default()
        .borders(Borders::BOTTOM)
        .border_type(BorderType::Rounded)
        .border_style(Style::default().fg(t::BORDER));

    Paragraph::new(text).block(block).render(area, buf);
}
