pub mod render;
pub mod shapes;
pub mod widget;

pub use render::{render_frame, AnimCell};

use std::f64::consts::PI;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Shape {
    Cube,
    Octahedron,
    Torus,
}

pub struct AnimState {
    pub shape: Shape,
    pub angle_y: f64,
    pub angle_x: f64,
    pub activity_level: u32,
    pub enabled: bool,
    /// Fast-ticking counter for shimmer effects, independent of rotation speed.
    pub shimmer_phase: f64,
    pub last_tick: std::time::Instant,
}

impl AnimState {
    pub fn new() -> Self {
        Self {
            shape: Shape::Torus,
            angle_y: 0.0,
            angle_x: 45.0_f64.to_radians(),
            activity_level: 0,
            enabled: true,
            shimmer_phase: 0.0,
            last_tick: std::time::Instant::now(),
        }
    }

    pub fn tick(&mut self) {
        if !self.enabled {
            return;
        }
        // Rate limit: only advance if 100ms has elapsed since last tick
        let now = std::time::Instant::now();
        if now.duration_since(self.last_tick).as_millis() < 100 {
            return;
        }
        self.last_tick = now;

        let step = rotation_step(self.activity_level);
        self.angle_y = (self.angle_y + step) % (2.0 * PI);
        self.angle_x = (self.angle_x + step * 0.4) % (2.0 * PI);
        let shimmer_speed = match self.activity_level {
            0 => 0.4,
            1..=2 => 0.8,
            3..=4 => 1.2,
            _ => 1.8,
        };
        self.shimmer_phase += shimmer_speed;
    }

    pub fn cycle_shape(&mut self) {
        self.shape = match self.shape {
            Shape::Cube => Shape::Octahedron,
            Shape::Octahedron => Shape::Torus,
            Shape::Torus => Shape::Cube,
        };
    }
}

impl Default for AnimState {
    fn default() -> Self {
        Self::new()
    }
}

pub fn rotation_step(activity: u32) -> f64 {
    match activity {
        0 => 0.5_f64.to_radians(),
        1..=2 => 2.0_f64.to_radians(),
        3..=4 => 5.0_f64.to_radians(),
        _ => 10.0_f64.to_radians(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rotation_step_maps_activity() {
        let eps = 1e-10;
        assert!((rotation_step(0) - 0.5_f64.to_radians()).abs() < eps);
        assert!((rotation_step(1) - 2.0_f64.to_radians()).abs() < eps);
        assert!((rotation_step(2) - 2.0_f64.to_radians()).abs() < eps);
        assert!((rotation_step(3) - 5.0_f64.to_radians()).abs() < eps);
        assert!((rotation_step(4) - 5.0_f64.to_radians()).abs() < eps);
        assert!((rotation_step(5) - 10.0_f64.to_radians()).abs() < eps);
        assert!((rotation_step(100) - 10.0_f64.to_radians()).abs() < eps);
    }

    #[test]
    fn cycle_shape_wraps() {
        let mut state = AnimState::new();
        assert_eq!(state.shape, Shape::Torus); // default is now Torus
        state.cycle_shape();
        assert_eq!(state.shape, Shape::Cube);
        state.cycle_shape();
        assert_eq!(state.shape, Shape::Octahedron);
        state.cycle_shape();
        assert_eq!(state.shape, Shape::Torus);
    }

    #[test]
    fn tick_advances_angle() {
        let mut state = AnimState::new();
        // Set last_tick to the past so the rate limiter allows the tick
        state.last_tick = std::time::Instant::now() - std::time::Duration::from_millis(200);
        let initial = state.angle_y;
        state.tick();
        assert!(state.angle_y > initial);
    }

    #[test]
    fn tick_disabled_does_not_advance() {
        let mut state = AnimState::new();
        state.enabled = false;
        state.tick();
        assert!((state.angle_y - 0.0).abs() < 1e-10);
    }

    #[test]
    fn default_x_tilt_is_45_degrees() {
        let state = AnimState::new();
        let eps = 1e-10;
        assert!((state.angle_x - 45.0_f64.to_radians()).abs() < eps);
    }
}
