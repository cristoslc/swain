use ratatui::prelude::*;
use ratatui::widgets::{Block, BorderType, Borders, Paragraph};

use crate::tui::app::App;
use crate::tui::theme as t;

pub fn render(app: &App, area: Rect, buf: &mut Buffer) {
    let (line1, line2) = if let Some(s) = app.selected_status() {
        let pane = s
            .pane_title
            .as_deref()
            .or(s.pane_id.as_deref())
            .unwrap_or("-");
        let branch = s.branch.as_deref().unwrap_or("-");
        let phase = s.phase.as_deref().unwrap_or("-");

        let hb_span = if app.stale_heartbeats.contains(&s.id) {
            Span::styled(
                "STALE",
                Style::default().fg(t::ERR).add_modifier(Modifier::BOLD),
            )
        } else {
            Span::styled("ok", Style::default().fg(t::OK))
        };

        let l1 = Line::from(vec![
            Span::styled(" ", Style::default()),
            Span::styled(
                &s.id,
                Style::default().fg(t::TEXT).add_modifier(Modifier::BOLD),
            ),
            Span::styled(" ", Style::default()),
            Span::styled(pane, Style::default().fg(t::PANE)),
            Span::styled("  branch:", Style::default().fg(t::TEXT_DIM)),
            Span::styled(branch, Style::default().fg(t::BRANCH)),
        ]);

        let msg = s.last_message.as_deref().unwrap_or("");
        let l2 = Line::from(vec![
            Span::styled(" phase:", Style::default().fg(t::TEXT_DIM)),
            Span::styled(phase, Style::default().fg(t::ACCENT)),
            Span::styled("  hb:", Style::default().fg(t::TEXT_DIM)),
            hb_span,
            Span::styled("  ", Style::default()),
            Span::styled(
                msg,
                Style::default()
                    .fg(t::TEXT_DIM)
                    .add_modifier(Modifier::ITALIC),
            ),
        ]);

        (l1, l2)
    } else {
        (
            Line::from(Span::styled(
                " No tasks",
                Style::default().fg(t::TEXT_MUTED),
            )),
            Line::from(""),
        )
    };

    let block = Block::default()
        .title(Span::styled(
            " Detail ",
            Style::default().fg(t::PRIMARY).add_modifier(Modifier::BOLD),
        ))
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .border_style(Style::default().fg(t::BORDER));

    Paragraph::new(Text::from(vec![line1, line2]))
        .block(block)
        .render(area, buf);
}
