import numpy as np

class Enemy:
    def __init__(self, position: np.ndarray):
        self.position = np.array(position, dtype=float)
        self.velocity = np.zeros(3, dtype=float)
        self.speed = 0.02  # Adjust as needed

        # Define enemy shape (e.g., cube)
        self.points = [
            [-0.5, -0.5, -0.5],
            [0.5, -0.5, -0.5],
            [0.5, 0.5, -0.5],
            [-0.5, 0.5, -0.5],
            [-0.5, -0.5, 0.5],
            [0.5, -0.5, 0.5],
            [0.5, 0.5, 0.5],
            [-0.5, 0.5, 0.5]
        ]
        self.edges = [
            [0,1], [1,2], [2,3], [3,0],  # Bottom face
            [4,5], [5,6], [6,7], [7,4],  # Top face
            [0,4], [1,5], [2,6], [3,7]   # Side edges
        ]

    def update(self, player_position: np.ndarray):
        direction = player_position - self.position
        distance = np.linalg.norm(direction)
        if distance > 0:
            direction /= distance
            self.velocity = direction * self.speed
            self.position += self.velocity

    def get_transformed_points(self):
        # Translate enemy shape points to current position
        return [np.array(point) + self.position for point in self.points]