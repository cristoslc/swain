# ASCII Animations for Dashboard

## Overview

Add a rotating 3D wireframe animation zone to the ratatui dashboard, positioned between the header and the worker table. The animation reacts to aggregate worker activity level (rotation speed) and provides visual personality to the dashboard.

## Shapes

Three shapes, cycleable with `D` (shift-d):

1. **Cube** (default) — 8 vertices, 12 edges. Classic wireframe.
2. **Octahedron** — 6 vertices, 12 edges. Diamond/gem silhouette.
3. **Torus** — point cloud rendered with brightness characters. Dense, demoscene.

## 3D Rendering

### Coordinate System

Vertices defined in 3D space as `(f64, f64, f64)`. Unit shapes centered at origin.

### Rotation

Continuous Y-axis rotation with ~15° X-axis tilt. Rotation angle increments on each tick based on worker activity:

| Workers Active | Rotation per tick |
|---|---|
| 0 | 0.5° |
| 1-2 | 2° |
| 3-4 | 5° |
| 5+ | 10° |

### Projection

Simple perspective projection from 3D to 2D terminal grid:

```
screen_x = (x / (z + camera_distance)) * scale + offset_x
screen_y = (y / (z + camera_distance)) * scale * 0.5 + offset_y
```

The `* 0.5` on Y compensates for terminal characters being ~2x taller than wide.

### Character Selection

**Vertices** — mapped by Z-depth (closer = brighter):

| Depth | Char |
|---|---|
| Front | `◆` |
| Mid-front | `◈` |
| Middle | `◇` |
| Mid-back | `◦` |
| Back | `·` |

**Edges (wireframe shapes)** — line-drawing characters chosen by angle and Z-depth:

| Angle Range | Char |
|---|---|
| 0°-22° | `─` |
| 23°-67° | `╲` or `╱` |
| 68°-90° | `│` |

Back edges drawn dimmer: `·` dotted or space for very back edges.

**Torus (point cloud)** — surface normals mapped to brightness:

| Brightness | Char |
|---|---|
| Darkest | `·` |
| Dark | `░` |
| Medium | `▒` |
| Bright | `▓` |
| Brightest | `█` |

### Color

- Front geometry: `Color::Cyan`
- Mid geometry: `Color::Blue`
- Back geometry: `Color::DarkGray`
- Activity level shifts front color: idle = `DarkGray`, active = `Cyan`, busy = `White`

## Layout Integration

### Adaptive Height

| Terminal Height | Animation Zone |
|---|---|
| < 20 rows | Hidden |
| 20-30 rows | 3 lines |
| 30-40 rows | 5 lines |
| 40+ rows | 7 lines |

### Dashboard Layout Change

In `src/tui/ui.rs`, the layout becomes:

```
header (3 lines — 2 content + border)
animation (0-7 lines — adaptive)
table (fill)
detail (4 lines — 2 content + border)
keys (1 line)
```

### Toggle

`d` toggles the animation zone on/off. State stored in `App.show_animation: bool` (default `true`). When off, the animation zone gets `Constraint::Length(0)` and the table gets more space.

`D` (shift-d) cycles through shapes: cube → octahedron → torus → cube.

## Module Structure

```
src/tui/
  anim/
    mod.rs        — pub exports, AnimState struct, shape enum
    shapes.rs     — vertex/edge definitions for cube, octahedron, torus
    render.rs     — 3D rotation, projection, character mapping
    widget.rs     — ratatui Widget impl that renders the animation
```

### AnimState

```rust
pub enum Shape {
    Cube,
    Octahedron,
    Torus,
}

pub struct AnimState {
    pub shape: Shape,
    pub angle_y: f64,        // current Y rotation in radians
    pub angle_x: f64,        // fixed X tilt (~0.26 rad / 15°)
    pub activity_level: u32, // 0 = idle, 1-2 = slow, 3-4 = medium, 5+ = fast
}
```

Updated on each tick in the event loop (not on the 3-second refresh cycle — animation needs smooth updates).

### Integration with App

Add to `App`:

```rust
pub anim: AnimState,
pub show_animation: bool,
```

In the event loop's `Tick` handler, update `anim.angle_y` based on activity. In `refresh()`, update `anim.activity_level` from the active worker count.

## Tick Rate Change

The event loop tick rate in `src/tui/event.rs` changes from 250ms to 100ms to support smooth animation. The 3-second data refresh cycle is unchanged — only the render/input polling gets faster.

## Performance

The animation renders on every tick (100-150ms). The render is pure math — rotate 8-12 vertices, project to 2D, draw ~12 edges. No I/O, no allocations in the hot path. This is negligible compared to the tmux pane captures happening on the 3-second refresh cycle.

## Testing

Unit tests for the math:

1. `cube_has_8_vertices_12_edges` — shape definition
2. `octahedron_has_6_vertices_12_edges` — shape definition
3. `project_point_center` — origin projects to center of screen
4. `project_point_depth` — farther Z = smaller screen coords
5. `rotation_360_returns_to_start` — full rotation cycle
6. `character_selection_by_depth` — correct brightness mapping
7. `activity_to_rotation_speed` — speed mapping table
