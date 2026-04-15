use ratatui::prelude::Color;

// ── agentrc brand palette ────────────────────────────────────────────────
// Warm amber + cool teal, with supporting grays that have color temperature.

/// Primary brand — pink/purple family
pub const PRIMARY: Color = Color::Rgb(210, 120, 190); // bright pink-purple
pub const PRIMARY_DIM: Color = Color::Rgb(130, 70, 120); // muted purple

/// Accent — warm amber/gold
pub const ACCENT: Color = Color::Rgb(230, 180, 80); // warm gold
pub const ACCENT_DIM: Color = Color::Rgb(140, 110, 50); // muted gold

/// Status colors
pub const OK: Color = Color::Rgb(120, 210, 120); // soft green
pub const WARN: Color = Color::Rgb(230, 180, 80); // same as accent (amber)
pub const ERR: Color = Color::Rgb(220, 100, 100); // soft red
pub const DONE: Color = Color::Rgb(120, 150, 220); // soft blue

/// Text hierarchy
pub const TEXT: Color = Color::Rgb(200, 200, 210); // near-white with cool cast
pub const TEXT_DIM: Color = Color::Rgb(120, 120, 135); // medium gray, cool
pub const TEXT_MUTED: Color = Color::Rgb(70, 70, 85); // dark gray, cool

/// Surfaces
pub const BORDER: Color = Color::Rgb(60, 65, 80); // subtle blue-gray border
pub const HIGHLIGHT_BG: Color = Color::Rgb(35, 40, 55); // selection highlight
pub const GRAVEYARD_BG: Color = Color::Rgb(25, 25, 35); // dimmer than default

/// Special
pub const BRANCH: Color = Color::Rgb(180, 140, 220); // lavender for git branches
pub const PANE: Color = Color::Rgb(180, 140, 220); // lavender, matches branch
