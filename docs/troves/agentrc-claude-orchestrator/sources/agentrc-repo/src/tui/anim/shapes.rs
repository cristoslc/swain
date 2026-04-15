use std::f64::consts::PI;

/// A point in 3D space.
#[derive(Debug, Clone, Copy)]
pub struct Vertex(pub f64, pub f64, pub f64);

/// An edge connecting two vertices by index into a vertex array.
#[derive(Debug, Clone, Copy)]
pub struct Edge(pub usize, pub usize);

/// A wireframe mesh composed of vertices and edges.
#[derive(Debug, Clone)]
pub struct Mesh {
    pub vertices: Vec<Vertex>,
    pub edges: Vec<Edge>,
}

/// Create a unit cube mesh with vertices at all (+-1, +-1, +-1) combinations.
///
/// The 8 vertices are enumerated by iterating x, y, z each over {-1, +1},
/// producing a consistent ordering. The 12 edges connect vertex pairs that
/// differ in exactly one coordinate.
pub fn cube() -> Mesh {
    let signs: [f64; 2] = [-1.0, 1.0];
    let mut vertices = Vec::with_capacity(8);

    // Enumerate vertices: index = 4*iz + 2*iy + ix
    // where ix, iy, iz in {0, 1} map to signs {-1, +1}.
    for &sz in &signs {
        for &sy in &signs {
            for &sx in &signs {
                vertices.push(Vertex(sx, sy, sz));
            }
        }
    }

    // Two vertices are adjacent (share an edge) when their indices differ
    // in exactly one bit position (Hamming distance 1), since each bit
    // corresponds to one coordinate axis.
    let mut edges = Vec::with_capacity(12);
    for i in 0..8_usize {
        for j in (i + 1)..8 {
            let xor = i ^ j;
            if xor.count_ones() == 1 {
                edges.push(Edge(i, j));
            }
        }
    }

    Mesh { vertices, edges }
}

/// Create an octahedron mesh with 6 axis-aligned vertices and 12 edges.
///
/// Vertices sit at (+-1, 0, 0), (0, +-1, 0), and (0, 0, +-1).
/// Edges connect every pair of non-opposite vertices. Two vertices are
/// opposite when one is the negation of the other.
pub fn octahedron() -> Mesh {
    let vertices = vec![
        Vertex(1.0, 0.0, 0.0),  // 0: +X
        Vertex(-1.0, 0.0, 0.0), // 1: -X
        Vertex(0.0, 1.0, 0.0),  // 2: +Y
        Vertex(0.0, -1.0, 0.0), // 3: -Y
        Vertex(0.0, 0.0, 1.0),  // 4: +Z
        Vertex(0.0, 0.0, -1.0), // 5: -Z
    ];

    // Opposite pairs by index: (0,1), (2,3), (4,5).
    let opposite_pairs: [(usize, usize); 3] = [(0, 1), (2, 3), (4, 5)];

    let mut edges = Vec::with_capacity(12);
    for i in 0..6_usize {
        for j in (i + 1)..6 {
            let is_opposite = opposite_pairs
                .iter()
                .any(|&(a, b)| (i == a && j == b) || (i == b && j == a));
            if !is_opposite {
                edges.push(Edge(i, j));
            }
        }
    }

    Mesh { vertices, edges }
}

/// Generate points on a torus surface with per-point surface normals.
///
/// The torus has major radius R = 1.0 and minor radius r = 0.4. Points are
/// sampled parametrically over angles theta and phi, each taking `resolution`
/// evenly-spaced steps across [0, 2pi).
///
/// Returns a `Vec` of `(Vertex, Vertex)` pairs (position, surface normal)
/// with `resolution * resolution` entries. The normal is unit-length and
/// points outward from the torus surface. The caller should rotate the
/// normal along with the position and then compute brightness from the
/// rotated normal's dot product with the light direction.
pub fn torus_points(resolution: usize) -> Vec<(Vertex, Vertex)> {
    const R: f64 = 1.0; // major radius
    const MINOR_R: f64 = 0.5; // minor radius (chunkier donut)

    let mut points = Vec::with_capacity(resolution * resolution);

    for i in 0..resolution {
        let theta = 2.0 * PI * (i as f64) / (resolution as f64);
        let cos_theta = theta.cos();
        let sin_theta = theta.sin();

        for j in 0..resolution {
            let phi = 2.0 * PI * (j as f64) / (resolution as f64);
            let cos_phi = phi.cos();
            let sin_phi = phi.sin();

            let x = (R + MINOR_R * cos_phi) * cos_theta;
            let y = (R + MINOR_R * cos_phi) * sin_theta;
            let z = MINOR_R * sin_phi;

            // Outward surface normal (unit vector):
            // n = (cos_phi * cos_theta, cos_phi * sin_theta, sin_phi)
            let normal = Vertex(cos_phi * cos_theta, cos_phi * sin_theta, sin_phi);

            points.push((Vertex(x, y, z), normal));
        }
    }

    points
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cube_has_8_vertices_12_edges() {
        let mesh = cube();
        assert_eq!(mesh.vertices.len(), 8);
        assert_eq!(mesh.edges.len(), 12);
    }

    #[test]
    fn octahedron_has_6_vertices_12_edges() {
        let mesh = octahedron();
        assert_eq!(mesh.vertices.len(), 6);
        assert_eq!(mesh.edges.len(), 12);
    }

    #[test]
    fn cube_vertices_are_unit() {
        let mesh = cube();
        for v in &mesh.vertices {
            assert!(
                v.0.abs() == 1.0 && v.1.abs() == 1.0 && v.2.abs() == 1.0,
                "Vertex ({}, {}, {}) does not have all coordinates at +/-1",
                v.0,
                v.1,
                v.2,
            );
        }
    }

    #[test]
    fn octahedron_vertices_on_axes() {
        let mesh = octahedron();
        for v in &mesh.vertices {
            let nonzero_count = [v.0, v.1, v.2].iter().filter(|c| c.abs() > 1e-10).count();
            assert_eq!(
                nonzero_count, 1,
                "Vertex ({}, {}, {}) should have exactly one non-zero coordinate",
                v.0, v.1, v.2,
            );
        }
    }

    #[test]
    fn cube_edges_connect_adjacent() {
        let mesh = cube();
        for edge in &mesh.edges {
            let a = &mesh.vertices[edge.0];
            let b = &mesh.vertices[edge.1];
            let diffs = [
                (a.0 - b.0).abs() > 1e-10,
                (a.1 - b.1).abs() > 1e-10,
                (a.2 - b.2).abs() > 1e-10,
            ];
            let diff_count = diffs.iter().filter(|&&d| d).count();
            assert_eq!(
                diff_count, 1,
                "Edge ({}, {}) connects vertices that differ in {} coordinates, expected 1",
                edge.0, edge.1, diff_count,
            );
        }
    }

    #[test]
    fn octahedron_no_opposite_edges() {
        let mesh = octahedron();
        for edge in &mesh.edges {
            let a = &mesh.vertices[edge.0];
            let b = &mesh.vertices[edge.1];
            let is_opposite =
                (a.0 + b.0).abs() < 1e-10 && (a.1 + b.1).abs() < 1e-10 && (a.2 + b.2).abs() < 1e-10;
            assert!(
                !is_opposite,
                "Edge ({}, {}) connects opposite vertices ({},{},{}) and ({},{},{})",
                edge.0, edge.1, a.0, a.1, a.2, b.0, b.1, b.2,
            );
        }
    }

    #[test]
    fn torus_point_count() {
        let points = torus_points(10);
        assert_eq!(points.len(), 100);
    }

    #[test]
    fn torus_normals_are_unit_length() {
        let points = torus_points(20);
        for (_, normal) in &points {
            let len = (normal.0 * normal.0 + normal.1 * normal.1 + normal.2 * normal.2).sqrt();
            assert!(
                (len - 1.0).abs() < 1e-10,
                "Normal ({}, {}, {}) has length {}, expected 1.0",
                normal.0,
                normal.1,
                normal.2,
                len,
            );
        }
    }
}
