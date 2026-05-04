use ratatui::prelude::*;

use super::AnimState;
use crate::tui::app::App;

fn depth_to_style(depth: f64, activity_level: u32) -> Style {
    use crate::tui::theme as t;
    let (front, back) = match activity_level {
        0 => (t::TEXT_MUTED, t::TEXT_MUTED),
        1..=2 => (t::PRIMARY_DIM, t::TEXT_MUTED),
        3..=4 => (t::PRIMARY, t::PRIMARY_DIM),
        _ => (t::TEXT, t::PRIMARY),
    };

    let interp = ((depth + 1.5) / 3.0).clamp(0.0, 1.0);
    let fg = if interp < 0.5 { front } else { back };
    Style::default().fg(fg)
}

/// Render the animation zone: info panel (left) + donut (right).
pub fn render(state: &AnimState, app: &App, area: Rect, buf: &mut Buffer) {
    if area.width < 10 || area.height < 3 {
        return;
    }

    // Split: left 40% for info, right 60% for donut
    let donut_width = (area.width as f64 * 0.55) as u16;
    let info_width = area.width.saturating_sub(donut_width);

    let info_area = Rect::new(area.x, area.y, info_width, area.height);
    let donut_area = Rect::new(area.x + info_width, area.y, donut_width, area.height);

    render_info(app, state, info_area, buf);
    render_donut(state, donut_area, buf);
}

fn render_info(app: &App, state: &AnimState, area: Rect, buf: &mut Buffer) {
    use crate::tui::theme as t;
    let dim = Style::default().fg(t::TEXT_MUTED);
    let label = Style::default().fg(t::TEXT_DIM);
    let value = Style::default().fg(t::PRIMARY);
    let bright = Style::default().fg(t::TEXT).add_modifier(Modifier::BOLD);

    let active = app.active_count();
    let done = app.completed_count();
    let total = app.statuses.len();

    let shape_name = match state.shape {
        super::Shape::Cube => "cube",
        super::Shape::Octahedron => "octahedron",
        super::Shape::Torus => "torus",
    };

    // Build info lines with dot leaders
    let lines: Vec<(String, String)> = vec![
        ("binary".into(), "agentrc v0.1.0".into()),
        ("run".into(), app.run_id.clone()),
        ("workers".into(), format!("{active} active / {total} total")),
        ("completed".into(), format!("{done}")),
        ("shape".into(), shape_name.into()),
        ("rust".into(), "edition 2021".into()),
        ("coord".into(), ".orchestrator/".into()),
    ];

    for (i, (key, val)) in lines.iter().enumerate() {
        if i as u16 >= area.height {
            break;
        }
        let y = area.y + i as u16;

        // Key
        let key_str = format!(" {key}");
        buf.set_string(area.x, y, &key_str, label);

        // Value (right-aligned before the donut)
        let val_width = val.len().min(area.width as usize / 2);
        let val_x = area.x + area.width - val_width as u16 - 1;
        buf.set_string(val_x, y, &val[..val_width], value);

        // Dot leaders between key and value
        let dots_start = area.x + key_str.len() as u16 + 1;
        let dots_end = val_x.saturating_sub(1);
        if dots_end > dots_start {
            let dots: String = std::iter::repeat('·')
                .take((dots_end - dots_start) as usize)
                .collect();
            buf.set_string(dots_start, y, &dots, dim);
        }
    }

    // Brand block: AGENT.RC, motto, author — centered in remaining space
    let banner = "░▒▓█▓▒░ AGENT.RC ░▒▓█▓▒░";
    let motto = "GOTTA GET THAT DONUT $$$";
    let author = "a tool by @ericsmithhh";

    let block_lines = 3u16; // banner + motto + author
    let info_end_y = area.y + lines.len() as u16;
    let remaining_h = area.height.saturating_sub(lines.len() as u16);

    if remaining_h >= block_lines {
        // Vertically center the 3-line block in the space below the metadata
        let block_start_y = info_end_y + (remaining_h - block_lines) / 2;
        let w = area.width as usize;

        // Horizontal center helper — use char count, not byte count
        let center_x = |text: &str| -> u16 {
            let char_len = text.chars().count();
            area.x + ((w.saturating_sub(char_len)) / 2) as u16
        };

        // Banner — pink-purple shimmer
        let bx = center_x(banner);
        render_shimmer(
            buf,
            bx,
            block_start_y,
            banner,
            state.shimmer_phase,
            0.3,
            160,
            80,
            140,
            60,
        );

        // Motto — amber shimmer
        let mx = center_x(motto);
        render_shimmer(
            buf,
            mx,
            block_start_y + 1,
            motto,
            state.shimmer_phase + 12.0,
            0.25,
            160,
            130,
            50,
            55,
        );

        // Author
        let ax = center_x(author);
        buf.set_string(ax, block_start_y + 2, "a tool by ", dim);
        buf.set_string(ax + 10, block_start_y + 2, "@ericsmithhh", bright);
    }
}

/// Render text with a traveling shimmer effect.
///
/// Each character cycles through brightness based on a sine wave:
/// `brightness = sin(phase + char_index * spread)`. The wave travels
/// as `phase` (driven by angle_y) advances each tick.
/// Render text with a subtle iridescent shimmer.
///
/// The whole text is always readable. A gentle sine-based brightness
/// wave passes through — each character's RGB values shift by a small
/// amount based on its position in the wave. Like Claude Code's shimmer.
fn render_shimmer(
    buf: &mut Buffer,
    x: u16,
    y: u16,
    text: &str,
    phase: f64,
    _spread: f64,
    base_r: u8,
    base_g: u8,
    base_b: u8,
    boost: u8,
) {
    let len = text.chars().count() as f64;
    // Shimmer position sweeps across text. Wider than a single char.
    let pos = (phase * 0.8) % (len + 8.0) - 4.0;

    for (i, ch) in text.chars().enumerate() {
        let dist = (i as f64 - pos).abs();
        // Gaussian-ish falloff: sharp peak, smooth tails
        let intensity = (-dist * dist / 8.0).exp(); // width ~4 chars
        let lift = (intensity * boost as f64) as u8;
        // At peak, push towards white (boost all channels towards 255)
        let white_mix = (intensity * 0.4).min(1.0);
        let r = lerp_u8(base_r.saturating_add(lift), 240, white_mix);
        let g = lerp_u8(base_g.saturating_add(lift), 240, white_mix);
        let b = lerp_u8(base_b.saturating_add(lift), 240, white_mix);
        buf.set_string(
            x + i as u16,
            y,
            ch.to_string(),
            Style::default().fg(Color::Rgb(r, g, b)),
        );
    }
}

fn lerp_u8(a: u8, b: u8, t: f64) -> u8 {
    (a as f64 + (b as f64 - a as f64) * t) as u8
}

fn render_donut(state: &AnimState, area: Rect, buf: &mut Buffer) {
    if area.width == 0 || area.height == 0 {
        return;
    }

    let grid = super::render::render_frame(state, area.width, area.height);
    for (y, row) in grid.iter().enumerate() {
        for (x, cell) in row.iter().enumerate() {
            if let Some(c) = cell {
                let style = depth_to_style(c.depth, state.activity_level);
                buf.set_string(
                    area.x + x as u16,
                    area.y + y as u16,
                    c.ch.to_string(),
                    style,
                );
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn depth_to_style_idle() {
        use crate::tui::theme as t;
        let style = depth_to_style(0.0, 0);
        assert_eq!(style.fg, Some(t::TEXT_MUTED));
    }

    #[test]
    fn depth_to_style_low_front() {
        use crate::tui::theme as t;
        let style = depth_to_style(-1.5, 1);
        assert_eq!(style.fg, Some(t::PRIMARY_DIM));
    }

    #[test]
    fn depth_to_style_high_front() {
        use crate::tui::theme as t;
        let style = depth_to_style(-1.5, 5);
        assert_eq!(style.fg, Some(t::TEXT));
    }

    #[test]
    fn render_zero_area_no_panic() {
        let state = AnimState::new();
        let app_area = Rect::new(0, 0, 0, 0);
        let mut buf = Buffer::empty(app_area);
        render_donut(&state, app_area, &mut buf);
    }
}
