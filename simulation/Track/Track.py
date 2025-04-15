import numpy as np
import json

class Track:
    def __init__(self, path_points, width, line_width=0.017, name="Unnamed Track", min_distance=0.001):
        """
        :param path_points: List of (x, y, elevation) tuples defining the track center line.
        :param width: Total width of the track (meters).
        :param min_distance: The minimum distance between any two consecutive points.
        """
        self.width = width
        self.line_width = line_width
        self.name = name
        self.min_distance = min_distance  # Minimum distance between two points

        # Increase the resolution of the track based on the min_distance
        self.path_points = self.increase_resolution(np.array(path_points), self.min_distance)

    def increase_resolution(self, path_points, min_distance):
        """
        Increases the resolution of the track by interpolating points based on the distance between them.
        
        :param path_points: Original list of path points (Nx3 array).
        :param min_distance: The minimum distance between two consecutive points.
        :return: A new list of path points with increased resolution.
        """
        new_path_points = []
        
        for i in range(len(path_points) - 1):
            p1 = path_points[i]
            p2 = path_points[i + 1]
            
            # Add the start point of the segment
            new_path_points.append(p1)

            # Calculate the distance between p1 and p2
            distance = np.linalg.norm(p2[:2] - p1[:2])
            
            # Determine how many new points to insert based on min_distance
            num_new_points = int(np.floor(distance / min_distance))

            # Add the interpolated points
            for j in range(1, num_new_points):
                t = j / num_new_points
                interpolated_point = p1 + t * (p2 - p1)
                new_path_points.append(interpolated_point)

        # Add the last point of the track
        new_path_points.append(path_points[-1])
        
        return np.array(new_path_points)



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
        #print(closest)
        tangent = self.compute_tangent(idx)
        normal = np.array([-tangent[1], tangent[0]])  # Perpendicular vector

        return {
            "position": closest[:2],
            "elevation": closest[2],
            "tangent": tangent,
            "normal": normal,
            "index": idx
        }
    
    def get_slope_angle_at_position(self, position: np.ndarray) -> float:
            """
            Computes the slope angle (in degrees) at the closest segment to the given position.
            Uses get_closest_point() for consistency.
            
            :param position: np.array([x, y]) representing a world coordinate.
            :return: slope angle in degrees.
            """
            closest = self.get_closest_point(position)
            idx = closest["index"]

            # Use same logic as compute_tangent to find segment points
            if idx <= 0:
                p1, p2 = self.path_points[0], self.path_points[1]
            elif idx >= len(self.path_points) - 1:
                p1, p2 = self.path_points[-2], self.path_points[-1]
            else:
                p1, p2 = self.path_points[idx - 1], self.path_points[idx + 1]

            delta_xy = np.linalg.norm(p2[:2] - p1[:2])
            delta_z = p2[2] - p1[2]

            if delta_xy == 0:
                return 0.0

            slope_rad = np.arctan2(delta_z, delta_xy)
            return np.degrees(slope_rad)

    def get_line_intensity(self, closest, world_position, falloff_factor=0.5):
        """
        Returns a bell-curve-based intensity based on the distance from the white line center.
        Peak at the center, and smooth dropoff beyond the line width.
        
        :param world_position: np.array([x, y])
        :param falloff_factor: Controls how quickly intensity drops. 1.0 = default, >1 = steeper, <1 = softer.
        :return: intensity in [0, 1]
        """
        distance = np.abs(np.dot(world_position - closest["position"], closest["normal"]))
        
        # Gaussian: peak at center, smooth falloff with "bell curve"
        # FWHM = line_width → sigma derived to ensure curve shape matches
        base_sigma = self.line_width / (2 * np.sqrt(2 * np.log(2)))  # FWHM ≈ line_width
        sigma = base_sigma / falloff_factor  # steeper or broader based on tuning

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


def load_tracks(filename, track_width=0.3):
    with open(filename, "r") as f:
        data = json.load(f)

    tracks = []
    for track_id, info in data.items():
        name = info.get("name", track_id)
        points = info["points"]
        track = Track(path_points=points, width=track_width, name=name)
        tracks.append(track)

    return tracks


def select_track(tracks) -> Track:
    print("Available Tracks:")
    for i, track in enumerate(tracks):
        print(f"{i + 1}. {track.name}")

    while True:
        selected = input("Type the track name or number to select it: ").strip()

        # Try numeric selection
        if selected.isdigit():
            index = int(selected) - 1
            if 0 <= index < len(tracks):
                selected_track = tracks[index]
                print("Selected Track:", selected_track.name)
                return selected_track
            else:
                print("Invalid number. Please choose a valid index.")

        # Try name-based selection (case-insensitive)
        else:
            for track in tracks:
                if track.name.lower() == selected.lower():
                    print("Selected Track:", track.name)
                    return track

            print("Not a valid track name. Please choose from the list above.")