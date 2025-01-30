import numpy as np

def make_4d_hypercube_shape() -> dict:
    """
    Return a dictionary describing a 4D hypercube (tesseract),
    with keys "name", "points", and "edges".
    - "points" is a list of all 16 vertices in 4D space.
    - "edges" is a list of [i, j] pairs, with i < j, for edges
      that differ in exactly one coordinate.
    """
    import itertools

    shape_name = "Hypercube"

    # Generate all 16 vertices with coordinates in {-1, +1}^4
    coords = [-1.0, 1.0]
    points = []
    for x in coords:
        for y in coords:
            for z in coords:
                for w in coords:
                    points.append([x, y, z, w])

    # Build the edge list: two vertices form an edge if they
    # differ in exactly one of the four coordinates.
    edges = []
    n = len(points)  # should be 16
    for i in range(n):
        for j in range(i + 1, n):
            diff_count = sum(
                1 for a, b in zip(points[i], points[j]) if a != b
            )
            if diff_count == 1:
                edges.append([i, j])

    return {
        "name": shape_name,
        "points": points,
        "edges": edges
    }

def intersect_segment_with_hyperplane_4d(
    A_4d, B_4d, hyperplane_pos_4d, hyperplane_angle
):
    """
    Intersect the line segment from A_4d to B_4d with
    the 3D hyperplane defined by hyperplane_pos_4d and a normal
    that depends on hyperplane_angle (rotated about W-axis).
    Return the 4D intersection point or None.
    """
    A = np.array(A_4d, dtype=float)
    B = np.array(B_4d, dtype=float)
    U = np.array(hyperplane_pos_4d, dtype=float)

    # Normal in 4D, rotating in XY-plane
    # about W-axis:
    n = np.array([
        np.cos(hyperplane_angle),
        np.sin(hyperplane_angle),
        0.0,
        0.0
    ], dtype=float)

    AB = B - A
    AU = A - U

    denom = np.dot(n, AB)
    nom = -np.dot(n, AU)

    if abs(denom) < 1e-12:
        # Parallel or no intersection
        return None

    t = nom / denom
    if 0.0 <= t <= 1.0:
        I = A + t * AB
        return tuple(I)
    return None


def project_point_onto_hyperplane_3d(point_4d, hyperplane_pos_4d, hyperplane_angle):
    """
    Project a 4D point 'point_4d' lying on the hyperplane into
    a local 3D coordinate system of that hyperplane.
    """
    P = np.array(point_4d, dtype=float)
    U = np.array(hyperplane_pos_4d, dtype=float)
    relative = P - U

    # Normal = (cos(angle), sin(angle), 0, 0)
    # An orthonormal basis that spans the hyperplane can be:
    #   u1 = (-sin(angle), cos(angle), 0, 0)
    #   u2 = (0, 0, 1, 0)
    #   u3 = (0, 0, 0, 1)
    u1 = np.array([-np.sin(hyperplane_angle),
                    np.cos(hyperplane_angle),
                    0.0, 0.0])
    u2 = np.array([0.0, 0.0, 1.0, 0.0])
    u3 = np.array([0.0, 0.0, 0.0, 1.0])

    X = np.dot(relative, u1)
    Y = np.dot(relative, u2)
    Z = np.dot(relative, u3)
    return (X, Y, Z)


def compute_intersections_4d(shape, hyperplane_pos_4d, hyperplane_angle):
    """
    Similar to the 3D version, but in 4D. Takes a shape
    with 'points' in 4D and 'edges' connecting those points.
    Returns the list of 3D intersection points in the
    hyperplane's local coordinate system.
    """
    pts_4d = shape['points']
    edges = shape['edges']

    intersection_points_4d = []
    for edge in edges:
        A_idx, B_idx = edge
        A_4d = pts_4d[A_idx]
        B_4d = pts_4d[B_idx]
        I_4d = intersect_segment_with_hyperplane_4d(
            A_4d, B_4d, hyperplane_pos_4d, hyperplane_angle
        )
        if I_4d is not None:
            intersection_points_4d.append(I_4d)

    # Convert to 3D "hyperplane" coords
    intersection_points_3d = [
        project_point_onto_hyperplane_3d(
            pt, hyperplane_pos_4d, hyperplane_angle
        )
        for pt in intersection_points_4d
    ]

    return intersection_points_3d


def main():
    hypercube_shape = make_4d_hypercube_shape()
    shapes_4d = [hypercube_shape]

    hyperplane_pos_4d = np.array([0.5, 0.0, 0.0, 0.0], dtype=float)
    hyperplane_angle = 0.7  # controlling normal in the x-y subspace

    for shape in shapes_4d:
        intersections_3d = compute_intersections_4d(
            shape, hyperplane_pos_4d, hyperplane_angle
        )
        print(f"Shape {shape.get('name', 'Unnamed')} intersections in 3D hyperplane coords:")
        for p in intersections_3d:
            print("  ", p)


if __name__ == "__main__":
    main()
