import numpy as np
from typing import Tuple, List, Optional


shapes = [
    {
      "name": "1",
      "points": [
        [1, 1, 1],
        [3, 1, 1],
        [3, 3, 1],
        [1, 3, 1],
        [1, 1, 3],
        [3, 1, 3],
        [3, 3, 3],
        [1, 3, 3]
      ],
      "edges": [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [4, 5],
        [5, 6],
        [6, 7],
        [7, 4],
        [0, 4],
        [1, 5],
        [2, 6],
        [3, 7]
      ]
    },
    {
      "name": "2",
      "points": [
        [-2, -1, 0],
        [-1, -1, 0],
        [-1, 1, 0],
        [-2, 1, 0],
        [-1.5, 0, 2]
      ],
      "edges": [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [0, 4],
        [1, 4],
        [2, 4],
        [3, 4]
      ]
    },
    {
      "points": [
          [-5.0, -5.0, -2.0],
          [5.0, -5.0, -2.0],
          [5.0, 5.0, -2.0],
          [-5.0, 5.0, -2.0]
      ],
      "edges": [
          [0, 1],
          [1, 2],
          [2, 3],
          [3, 0]
      ]
  }
]

def intersect_edge_with_plane(A: Tuple[float, float, float], 
                            B: Tuple[float, float, float],
                            plane_pos: Tuple[float, float, float], 
                            plane_angle: float) -> Optional[Tuple[float, float, float]]:
    """
    Intersect line segment AB with the vertical plane that passes through plane_pos
    and has normal n(theta) = (cos(theta), sin(theta), 0).
    """
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)
    U = np.array(plane_pos, dtype=float)

    # Plane normal
    n = np.array([np.cos(plane_angle), np.sin(plane_angle), 0.0], dtype=float)

    AB = B - A
    AU = A - U

    denom = np.dot(n, AB)
    nom = -np.dot(n, AU)

    # If denom is 0, line is parallel to plane
    if abs(denom) < 1e-12:
        return None

    t = nom / denom
    if 0.0 <= t <= 1.0:
        I = A + t * AB
        return tuple(I)
    return None

def project_point_onto_plane_2D(point_3d: Tuple[float, float, float],
                               plane_pos: Tuple[float, float, float],
                               plane_angle: float) -> Tuple[float, float]:
    """Convert a 3D intersection point to 2D plane coordinates (X,Z)."""
    P = np.array(point_3d, dtype=float)
    U = np.array(plane_pos, dtype=float)
    relative = P - U

    p_x = np.array([-np.sin(plane_angle), np.cos(plane_angle), 0.0], dtype=float)
    p_z = np.array([0.0, 0.0, 1.0], dtype=float)

    X = np.dot(relative, p_x)
    Z = np.dot(relative, p_z)
    return (X, Z)

def compute_intersections(shape: dict, 
                        plane_pos: np.ndarray, 
                        plane_angle: float) -> List[Tuple[float, float]]:
    """Compute intersection points for a single shape."""
    pts_3d = shape['points']
    edges = shape['edges']
    
    # Gather intersection points
    intersection_points_3d = []
    for edge in edges:
        A_idx, B_idx = edge
        A_3d = pts_3d[A_idx]
        B_3d = pts_3d[B_idx]
        I_3d = intersect_edge_with_plane(A_3d, B_3d, plane_pos, plane_angle)
        if I_3d is not None:
            intersection_points_3d.append(I_3d)

    # Convert to 2D plane coords
    intersection_points_2d = [project_point_onto_plane_2D(pt, plane_pos, plane_angle)
                            for pt in intersection_points_3d]
    return intersection_points_2d

def main():
    global shapes
    # Load shapes
    plane_pos = np.array([0.0, 0.0, 0.0], dtype=float)
    plane_angle = 1.963
    
    print(f"Computing intersections for plane at position {plane_pos} with angle {plane_angle}")
    print("-" * 50)
    
    # Process each shape
    for i, shape in enumerate(shapes):
        intersections_2d = compute_intersections(shape, plane_pos, plane_angle)
        print(f"\nShape {i}: {shape.get('name', 'Unnamed')}")
        print("Intersection points (X, Z):")
        for point in intersections_2d:
            print(f"  {point}")

if __name__ == "__main__":
    main()