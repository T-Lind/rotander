import numpy as np
from typing import Tuple, List, Optional

# ...existing code...
import numpy as np
from typing import Tuple, List, Optional
from scipy.spatial import ConvexHull

class GeometryHelper4D:
    @staticmethod
    def intersect_edge_with_hyperplane_4D(
        A,
        B,
        plane_normal: np.ndarray,
        plane_offset: float
    ) -> Optional[np.ndarray]:
        A_4d = np.array(A, dtype=float)
        B_4d = np.array(B, dtype=float)
        AB = B_4d - A_4d

        denom = np.dot(plane_normal, AB)
        if abs(denom) < 1e-12:
            return None  # Parallel or no intersection

        t = (plane_offset - np.dot(plane_normal, A_4d)) / denom
        if 0.0 <= t <= 1.0:
            return A_4d + t * AB
        return None

    @staticmethod
    def project_point_onto_hyperplane_3D(
        point_4d: np.ndarray,
        plane_normal: np.ndarray
    ) -> np.ndarray:
        # Make sure plane_normal is normalized
        n_hat = plane_normal / np.linalg.norm(plane_normal)

        # We want 3 orthonormal vectors that are orthogonal to n_hat
        basis_vectors = []
        e_candidates = np.eye(4)
        for e in e_candidates:
            # Remove component in direction n_hat
            e_proj = e - np.dot(e, n_hat) * n_hat
            norm_e_proj = np.linalg.norm(e_proj)
            if norm_e_proj > 1e-12:
                e_unit = e_proj / norm_e_proj
                for b in basis_vectors:
                    e_unit -= np.dot(e_unit, b) * b
                e_unit_norm = np.linalg.norm(e_unit)
                if e_unit_norm > 1e-12:
                    e_unit /= e_unit_norm
                    basis_vectors.append(e_unit)
                if len(basis_vectors) == 3:
                    break

        if len(basis_vectors) < 3:
            # fallback:
            basis_vectors = [np.eye(4)[1], np.eye(4)[2], np.eye(4)[3]]

        basis = np.stack(basis_vectors, axis=1)  # shape (4,3)
        # Project onto the hyperplane basis
        return basis.T @ point_4d

    @staticmethod
    def compute_intersections_4D(
        shape: dict,
        plane_normal: np.ndarray,
        plane_offset: float
    ):
        """
        Return a dict with 'meshVertices' (List[List[float]]) and 'meshTriangles' (List[int]).
        'meshVertices' can be interpreted as Vector3 in Unity.
        'meshTriangles' are indices into 'meshVertices'.
        """
        # Gather intersection points
        intersection_3d = []
        for (A_idx, B_idx) in shape["edges"]:
            A_4d = shape["points"][A_idx]
            B_4d = shape["points"][B_idx]
            I_4d = GeometryHelper4D.intersect_edge_with_hyperplane_4D(
                A_4d, B_4d, plane_normal, plane_offset
            )
            if I_4d is not None:
                # project to 3D
                p3 = GeometryHelper4D.project_point_onto_hyperplane_3D(I_4d, plane_normal)
                intersection_3d.append(p3)

        # Build a numpy array
        verts_array = np.array(intersection_3d)
        if len(verts_array) < 4:
            return {
                "meshVertices": verts_array.tolist(),
                "meshTriangles": []
            }

        # Build a 3D hull out of the intersection points
        hull = ConvexHull(verts_array)
        # hull.simplices are the triangular faces
        mesh_triangles = []
        for simplex in hull.simplices:
            # each simplex is something like [i0, i1, i2]
            mesh_triangles.extend(simplex.tolist())

        # Return final data
        return {
            "meshVertices": verts_array.tolist(),
            "meshTriangles": mesh_triangles
        }


if __name__ == "__main__":
    shape_4d = {
        "points": [
            (1, 1, 1, 1),
            (2, 1, 1, 2),
            (1, 2, 2, 1),
            (2, 2, 2, 2)
        ],
        "edges": [
            (0, 1),
            (2, 3),
            
        ]
    }

    plane_normal = np.array([0.0, 1.0, 0.0, 1.0])
    plane_offset = 2.0

    intersection_points_3d, intersection_edges = GeometryHelper4D.compute_intersections_4D(
        shape_4d,
        plane_normal,
        plane_offset
    )

    print("3D intersection points:", intersection_points_3d)
    print("3D intersection edges:", intersection_edges)