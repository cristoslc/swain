use super::shapes::Vertex;

/// A single cell in the rendered animation grid.
///
/// Contains the character to draw and the Z-depth of the geometry at that
/// position. The depth value is preserved so that the widget layer can map
/// it to a color gradient (e.g. brighter for closer geometry).
#[derive(Debug, Clone)]
pub struct AnimCell {
    pub ch: char,
    pub depth: f64,
}

/// Render a frame of the animation to a 2D grid.
///
/// Returns `Vec<Vec<Option<AnimCell>>>` where the outer vector is rows (height)
/// and the inner vector is columns (width). `None` means empty space;
/// `Some(AnimCell)` means a character to draw at that position.
pub fn render_frame(
    state: &super::AnimState,
    width: u16,
    height: u16,
) -> Vec<Vec<Option<AnimCell>>> {
    let w = width as usize;
    let h = height as usize;
    let mut grid = vec![vec![None; w]; h];

    match state.shape {
        super::Shape::Cube | super::Shape::Octahedron => {
            let mesh = match state.shape {
                super::Shape::Cube => super::shapes::cube(),
                _ => super::shapes::octahedron(),
            };

            // Rotate all vertices according to the current animation angles.
            let rotated: Vec<Vertex> = mesh
                .vertices
                .iter()
                .map(|v| rotate_vertex(v, state.angle_y, state.angle_x))
                .collect();

            // Project from 3D to 2D screen coordinates.
            let projected: Vec<(f64, f64, f64)> =
                rotated.iter().map(|v| project(v, width, height)).collect();

            // Draw edges first so that vertex markers can overwrite them.
            // Skip very back-facing edges (both endpoints behind center) to
            // reduce visual clutter and improve the wireframe illusion.
            for edge in &mesh.edges {
                let (x0, y0, d0) = projected[edge.0];
                let (x1, y1, d1) = projected[edge.1];
                let avg_depth = (d0 + d1) / 2.0;
                if avg_depth > 0.8 {
                    // Very far back — draw with dots for depth cue
                    draw_line_dotted(&mut grid, x0, y0, x1, y1, avg_depth);
                } else {
                    draw_line(&mut grid, x0, y0, x1, y1, avg_depth);
                }
            }

            // Draw vertices on top of edge lines.
            for &(sx, sy, depth) in &projected {
                let x = sx.round() as isize;
                let y = sy.round() as isize;
                if x >= 0 && y >= 0 && (x as usize) < w && (y as usize) < h {
                    grid[y as usize][x as usize] = Some(AnimCell {
                        ch: vertex_char(depth),
                        depth,
                    });
                }
            }
        }
        super::Shape::Torus => {
            // Higher resolution for denser point coverage
            let resolution = ((width as usize) + (height as usize) * 2).max(40);
            let points = super::shapes::torus_points(resolution);

            // Light from above-left, towards viewer (classic donut.c: 0, 1, -1)
            let light = (0.0_f64, 1.0, -1.0);
            let light_len = (light.0 * light.0 + light.1 * light.1 + light.2 * light.2).sqrt();
            let light = (
                light.0 / light_len,
                light.1 / light_len,
                light.2 / light_len,
            );

            for (v, normal) in &points {
                let rotated = rotate_vertex(v, state.angle_y, state.angle_x);
                let rotated_normal = rotate_vertex(normal, state.angle_y, state.angle_x);
                let (sx, sy, depth) = project(&rotated, width, height);
                let x = sx.round() as isize;
                let y = sy.round() as isize;
                if x >= 0 && y >= 0 && (x as usize) < w && (y as usize) < h {
                    // Dot product with light direction for shading
                    let brightness = (rotated_normal.0 * light.0
                        + rotated_normal.1 * light.1
                        + rotated_normal.2 * light.2)
                        .clamp(0.0, 1.0);
                    let ch = torus_brightness_char(brightness);
                    let cell = AnimCell { ch, depth };
                    let slot = &mut grid[y as usize][x as usize];
                    if slot.as_ref().is_none_or(|existing| depth < existing.depth) {
                        *slot = Some(cell);
                    }
                }
            }
        }
    }

    grid
}

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------

/// Apply Y-axis rotation followed by X-axis rotation to a vertex.
///
/// The rotation order is: first rotate around Y (horizontal spin), then
/// rotate around X (vertical tilt). This matches the convention where
/// `angle_y` controls the horizontal rotation visible to the user and
/// `angle_x` controls the tilt.
fn rotate_vertex(v: &Vertex, angle_y: f64, angle_x: f64) -> Vertex {
    let cos_y = angle_y.cos();
    let sin_y = angle_y.sin();

    // Y-axis rotation (x-z plane).
    let x1 = v.0 * cos_y - v.2 * sin_y;
    let z1 = v.0 * sin_y + v.2 * cos_y;
    let y1 = v.1;

    let cos_x = angle_x.cos();
    let sin_x = angle_x.sin();

    // X-axis rotation (y-z plane).
    let y2 = y1 * cos_x - z1 * sin_x;
    let z2 = y1 * sin_x + z1 * cos_x;

    Vertex(x1, y2, z2)
}

/// Perspective-project a 3D vertex onto 2D screen coordinates.
///
/// Returns `(screen_x, screen_y, depth)`. The depth is the rotated Z value
/// and is passed through unchanged for downstream color mapping.
///
/// The Y projection is halved (`* 0.5`) because terminal characters are
/// roughly twice as tall as they are wide, so this keeps the aspect ratio
/// visually correct.
fn project(v: &Vertex, width: u16, height: u16) -> (f64, f64, f64) {
    // Scale to fill the available space. Terminal chars are ~2x taller than wide.
    // Use height as the limiting dimension since animation zones are wide but short.
    let scale = (height as f64) * 2.5;
    let camera_dist = 3.5;
    let factor = scale / (v.2 + camera_dist).max(0.1);
    let sx = v.0 * factor + (width as f64) / 2.0;
    let sy = v.1 * factor * 0.5 + (height as f64) / 2.0;
    (sx, sy, v.2)
}

/// Map Z-depth to a vertex marker character.
///
/// More negative depth means closer to the viewer and gets a bolder glyph.
/// The expected depth range for unit shapes after rotation is roughly
/// `[-1.5, 1.5]`.
fn vertex_char(depth: f64) -> char {
    if depth < -0.6 {
        '\u{25C6}' // ◆  front / closest
    } else if depth < -0.2 {
        '\u{25C8}' // ◈
    } else if depth < 0.2 {
        '\u{25C7}' // ◇
    } else if depth < 0.6 {
        '\u{25E6}' // ◦
    } else {
        '\u{00B7}' // ·  back / farthest
    }
}

/// Choose a line-drawing character based on the direction of a segment.
///
/// The angle is measured from the positive X axis. Near-horizontal segments
/// get `'─'`, near-vertical get `'│'`, and diagonals get `'╲'` or `'╱'`
/// depending on slope direction.
fn edge_char(dx: f64, dy: f64) -> char {
    let angle = dy.atan2(dx).abs().to_degrees();
    if !(22.5..=157.5).contains(&angle) {
        '\u{2500}' // ─
    } else if angle < 67.5 {
        // Diagonal: pick backslash vs forward-slash based on slope sign.
        if dx * dy > 0.0 {
            '\u{2572}' // ╲
        } else {
            '\u{2571}' // ╱
        }
    } else if angle < 112.5 {
        '\u{2502}' // │
    } else {
        // Mirror diagonal region (112.5 .. 157.5).
        if dx * dy > 0.0 {
            '\u{2572}' // ╲
        } else {
            '\u{2571}' // ╱
        }
    }
}

/// Rasterise a line segment onto the character grid using linear stepping.
///
/// Each cell along the line receives the same edge character determined by
/// the overall direction `(dx, dy)`. The provided `depth` (typically the
/// average of the two endpoint depths) is stored in every cell for color
/// mapping.
fn draw_line(grid: &mut [Vec<Option<AnimCell>>], x0: f64, y0: f64, x1: f64, y1: f64, depth: f64) {
    let total_dx = x1 - x0;
    let total_dy = y1 - y0;
    let steps = (total_dx.abs().max(total_dy.abs())).ceil() as usize;
    if steps == 0 {
        return;
    }

    let dx = total_dx / steps as f64;
    let dy = total_dy / steps as f64;
    let ch = edge_char(total_dx, total_dy);

    let h = grid.len();
    let w = if h > 0 { grid[0].len() } else { 0 };

    for i in 0..=steps {
        let x = (x0 + dx * i as f64).round() as isize;
        let y = (y0 + dy * i as f64).round() as isize;
        if x >= 0 && y >= 0 && (x as usize) < w && (y as usize) < h {
            let slot = &mut grid[y as usize][x as usize];
            if slot.as_ref().is_none_or(|existing| depth < existing.depth) {
                *slot = Some(AnimCell { ch, depth });
            }
        }
    }
}

/// Draw a dotted line for back-facing edges.
fn draw_line_dotted(
    grid: &mut [Vec<Option<AnimCell>>],
    x0: f64,
    y0: f64,
    x1: f64,
    y1: f64,
    depth: f64,
) {
    let total_dx = x1 - x0;
    let total_dy = y1 - y0;
    let steps = (total_dx.abs().max(total_dy.abs())).ceil() as usize;
    if steps == 0 {
        return;
    }
    let dx = total_dx / steps as f64;
    let dy = total_dy / steps as f64;
    let h = grid.len();
    let w = if h > 0 { grid[0].len() } else { 0 };

    for i in (0..=steps).step_by(2) {
        // Every other pixel for dotted effect
        let x = (x0 + dx * i as f64).round() as isize;
        let y = (y0 + dy * i as f64).round() as isize;
        if x >= 0 && y >= 0 && (x as usize) < w && (y as usize) < h {
            let slot = &mut grid[y as usize][x as usize];
            if slot.is_none() {
                *slot = Some(AnimCell {
                    ch: '\u{00B7}', // ·
                    depth,
                });
            }
        }
    }
}

/// Map a brightness value in `[0.0, 1.0]` to a torus surface character.
///
/// Brighter areas (facing the light) get denser block characters.
fn torus_brightness_char(brightness: f64) -> char {
    if brightness < 0.2 {
        '\u{00B7}' // ·
    } else if brightness < 0.4 {
        '\u{2591}' // ░
    } else if brightness < 0.6 {
        '\u{2592}' // ▒
    } else if brightness < 0.8 {
        '\u{2593}' // ▓
    } else {
        '\u{2588}' // █
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tui::anim::shapes::Vertex;

    #[test]
    fn rotation_identity() {
        // Zero rotation must return the same coordinates.
        let v = Vertex(1.0, 2.0, 3.0);
        let r = rotate_vertex(&v, 0.0, 0.0);
        assert!((r.0 - 1.0).abs() < 1e-10);
        assert!((r.1 - 2.0).abs() < 1e-10);
        assert!((r.2 - 3.0).abs() < 1e-10);
    }

    #[test]
    fn rotation_360_roundtrip() {
        use std::f64::consts::PI;
        let v = Vertex(1.0, 0.5, -0.3);
        let r = rotate_vertex(&v, 2.0 * PI, 2.0 * PI);
        assert!((r.0 - v.0).abs() < 1e-9);
        assert!((r.1 - v.1).abs() < 1e-9);
        assert!((r.2 - v.2).abs() < 1e-9);
    }

    #[test]
    fn rotation_y_90_swaps_x_z() {
        use std::f64::consts::FRAC_PI_2;
        // Rotating (1, 0, 0) by 90 degrees around Y should give (0, 0, 1).
        let v = Vertex(1.0, 0.0, 0.0);
        let r = rotate_vertex(&v, FRAC_PI_2, 0.0);
        assert!((r.0).abs() < 1e-10);
        assert!((r.1).abs() < 1e-10);
        assert!((r.2 - 1.0).abs() < 1e-10);
    }

    #[test]
    fn project_origin_to_center() {
        let v = Vertex(0.0, 0.0, 0.0);
        let (sx, sy, _) = project(&v, 40, 20);
        assert!((sx - 20.0).abs() < 1.0, "sx = {sx}, expected near 20");
        assert!((sy - 10.0).abs() < 1.0, "sy = {sy}, expected near 10");
    }

    #[test]
    fn project_depth_affects_scale() {
        // A point at z=-1 should project larger (farther from center)
        // than the same point at z=1, because it is closer to the camera.
        let near = Vertex(1.0, 0.0, -1.0);
        let far = Vertex(1.0, 0.0, 1.0);
        let (sx_near, _, _) = project(&near, 40, 20);
        let (sx_far, _, _) = project(&far, 40, 20);
        assert!(
            (sx_near - 20.0).abs() > (sx_far - 20.0).abs(),
            "Near point offset {:.2} should exceed far point offset {:.2}",
            (sx_near - 20.0).abs(),
            (sx_far - 20.0).abs(),
        );
    }

    #[test]
    fn project_preserves_depth() {
        let v = Vertex(0.5, 0.5, 0.42);
        let (_, _, depth) = project(&v, 40, 20);
        assert!((depth - 0.42).abs() < 1e-10);
    }

    #[test]
    fn vertex_char_by_depth() {
        assert_eq!(vertex_char(-1.0), '\u{25C6}'); // ◆
        assert_eq!(vertex_char(-0.4), '\u{25C8}'); // ◈
        assert_eq!(vertex_char(0.0), '\u{25C7}'); // ◇
        assert_eq!(vertex_char(0.4), '\u{25E6}'); // ◦
        assert_eq!(vertex_char(1.0), '\u{00B7}'); // ·
    }

    #[test]
    fn vertex_char_boundary_values() {
        // Exactly on threshold values: -0.6 belongs to the next bracket.
        assert_eq!(vertex_char(-0.6), '\u{25C8}'); // ◈  (not ◆)
        assert_eq!(vertex_char(-0.2), '\u{25C7}'); // ◇  (not ◈)
        assert_eq!(vertex_char(0.2), '\u{25E6}'); // ◦  (not ◇)
        assert_eq!(vertex_char(0.6), '\u{00B7}'); // ·  (not ◦)
    }

    #[test]
    fn edge_char_horizontal() {
        assert_eq!(edge_char(5.0, 0.0), '\u{2500}'); // ─
    }

    #[test]
    fn edge_char_vertical() {
        assert_eq!(edge_char(0.0, 5.0), '\u{2502}'); // │
    }

    #[test]
    fn edge_char_diagonal_backslash() {
        // Positive dx and positive dy (going down-right in screen coords).
        assert_eq!(edge_char(1.0, 1.0), '\u{2572}'); // ╲
    }

    #[test]
    fn edge_char_diagonal_forward_slash() {
        // Positive dx and negative dy (going up-right in screen coords).
        assert_eq!(edge_char(1.0, -1.0), '\u{2571}'); // ╱
    }

    #[test]
    fn torus_brightness_chars() {
        assert_eq!(torus_brightness_char(0.0), '\u{00B7}'); // ·
        assert_eq!(torus_brightness_char(0.1), '\u{00B7}'); // ·
        assert_eq!(torus_brightness_char(0.3), '\u{2591}'); // ░
        assert_eq!(torus_brightness_char(0.5), '\u{2592}'); // ▒
        assert_eq!(torus_brightness_char(0.7), '\u{2593}'); // ▓
        assert_eq!(torus_brightness_char(0.9), '\u{2588}'); // █
    }

    #[test]
    fn render_frame_dimensions() {
        let state = crate::tui::anim::AnimState::new();
        let grid = render_frame(&state, 30, 10);
        assert_eq!(grid.len(), 10);
        for row in &grid {
            assert_eq!(row.len(), 30);
        }
    }

    #[test]
    fn render_frame_has_content() {
        // A default cube at angle_y=0 should produce some non-None cells.
        let state = crate::tui::anim::AnimState::new();
        let grid = render_frame(&state, 40, 20);
        let filled = grid
            .iter()
            .flat_map(|row| row.iter())
            .filter(|c| c.is_some())
            .count();
        assert!(
            filled > 0,
            "Expected some rendered cells but got an empty grid",
        );
    }

    #[test]
    fn render_frame_torus() {
        let mut state = crate::tui::anim::AnimState::new();
        state.shape = crate::tui::anim::Shape::Torus;
        let grid = render_frame(&state, 40, 20);
        assert_eq!(grid.len(), 20);
        assert_eq!(grid[0].len(), 40);
        let filled = grid
            .iter()
            .flat_map(|row| row.iter())
            .filter(|c| c.is_some())
            .count();
        assert!(filled > 0, "Torus should produce some rendered cells");
    }

    #[test]
    fn render_frame_octahedron() {
        let mut state = crate::tui::anim::AnimState::new();
        state.shape = crate::tui::anim::Shape::Octahedron;
        let grid = render_frame(&state, 40, 20);
        let filled = grid
            .iter()
            .flat_map(|row| row.iter())
            .filter(|c| c.is_some())
            .count();
        assert!(filled > 0, "Octahedron should produce some rendered cells");
    }

    #[test]
    fn render_frame_zero_size() {
        // Edge case: zero dimensions should produce an empty grid without panicking.
        let state = crate::tui::anim::AnimState::new();
        let grid = render_frame(&state, 0, 0);
        assert!(grid.is_empty());
    }

    #[test]
    fn draw_line_stays_in_bounds() {
        // Drawing a line that extends beyond the grid should not panic.
        let mut grid = vec![vec![None; 10]; 5];
        draw_line(&mut grid, -5.0, -3.0, 15.0, 8.0, 0.0);
        // Just verify no panic occurred. Check that at least some cells were set.
        let filled = grid
            .iter()
            .flat_map(|row| row.iter())
            .filter(|c| c.is_some())
            .count();
        assert!(filled > 0);
    }

    #[test]
    fn draw_line_zero_length() {
        // A zero-length line should not panic.
        let mut grid = vec![vec![None; 10]; 5];
        draw_line(&mut grid, 5.0, 2.0, 5.0, 2.0, 0.0);
        // Zero-length => steps == 0 => no cells drawn (early return).
    }
}
