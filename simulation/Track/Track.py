import numpy as np

class Track:
    def __init__(self, path_points, width, line_width=0.017):
        """
        :param path_points: List of (x, y, elevation) tuples defining the track center line.
        :param width: Total width of the track (meters).
        """
        self.path_points = np.array(path_points)  # Nx3: [x, y, z]
        self.width = width
        self.line_width = line_width

    def get_closest_point(self, buggy_position):
        """
        Given the buggy's current (x, y) position, return the closest point on the track centerline.
        :param buggy_position: np.array([x, y])
        :return: dict with keys: 'position', 'tangent', 'normal', 'elevation', 'index'
        """
        positions = self.path_points[:, :2]  # Ignore elevation for projection
        diffs = positions - buggy_position
        distances = np.linalg.norm(diffs, axis=1)
        idx = np.argmin(distances)

        closest = self.path_points[idx]
        tangent = self.compute_tangent(idx)
        normal = np.array([-tangent[1], tangent[0]])  # Perpendicular vector

        return {
            "position": closest[:2],
            "elevation": closest[2],
            "tangent": tangent,
            "normal": normal,
            "index": idx
        }


    def get_line_intensity(self, world_position):
        """
        Simulate white line visibility based on distance to centerline.
        :param world_position: np.array([x, y])
        :return: intensity in [0,1], 1 = perfectly centered, 0 = too far
        """
        closest = self.get_closest_point(world_position)
        distance = np.abs(np.dot(world_position - closest["position"], closest["normal"]))
        
        # Gaussian-like falloff (adjust sensitivity if needed)
        sigma = self.line_width / 2
        intensity = np.exp(- (distance ** 2) / (2 * sigma ** 2))
        return intensity
    
    def compute_tangent(self, idx):
        if idx <= 0:
            p1, p2 = self.path_points[0], self.path_points[1]
        elif idx >= len(self.path_points) - 1:
            p1, p2 = self.path_points[-2], self.path_points[-1]
        else:
            p1, p2 = self.path_points[idx - 1], self.path_points[idx + 1]
        delta = p2[:2] - p1[:2]
        return delta / np.linalg.norm(delta)
