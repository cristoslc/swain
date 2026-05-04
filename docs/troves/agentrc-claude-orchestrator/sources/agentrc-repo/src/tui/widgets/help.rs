use ratatui::prelude::*;
use ratatui::widgets::{Block, BorderType, Borders, Clear, Paragraph};

use crate::tui::theme as t;

fn help_line(key: &str, desc: &str) -> Line<'static> {
    Line::from(vec![
        Span::styled(
            format!("  {key:>6}"),
            Style::default().fg(t::ACCENT).add_modifier(Modifier::BOLD),
        ),
        Span::styled(format!("  {desc}"), Style::default().fg(t::TEXT)),
    ])
}

pub fn render(area: Rect, buf: &mut Buffer) {
    let lines = vec![
        Line::from(Span::styled(
            "  Keyboard Shortcuts",
            Style::default().fg(t::PRIMARY).add_modifier(Modifier::BOLD),
        )),
        Line::from(""),
        help_line("↑/k", "Previous worker"),
        help_line("↓/j", "Next worker"),
        help_line("z", "Zoom into worker pane"),
        help_line("t", "Teardown selected worker"),
        help_line("r", "Respawn selected worker"),
        help_line("a", "Amend task brief"),
        help_line("i", "Integrate completed branches"),
        help_line("c", "Save checkpoint"),
        help_line("s", "Cycle sort order"),
        help_line("d", "Toggle animation"),
        help_line("D", "Cycle animation shape"),
        help_line("?", "Toggle this help"),
        help_line("q", "Quit dashboard"),
    ];

    let width = 42;
    let height = lines.len() as u16 + 2;
    let x = area.x + (area.width.saturating_sub(width)) / 2;
    let y = area.y + (area.height.saturating_sub(height)) / 2;
    let overlay = Rect::new(x, y, width.min(area.width), height.min(area.height));

    Clear.render(overlay, buf);

    let block = Block::default()
        .title(Span::styled(
            " Help ",
            Style::default().fg(t::PRIMARY).add_modifier(Modifier::BOLD),
        ))
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .border_style(Style::default().fg(t::PRIMARY_DIM));

    Paragraph::new(lines).block(block).render(overlay, buf);
}
