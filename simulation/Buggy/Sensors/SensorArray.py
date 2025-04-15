import numpy as np
from Track.Track import Track

class SensorArray:
    def __init__(self, sensor_positions_local, track: Track):
        """
        :param sensor_positions_local: List of np.array([x, y]) positions in buggy's local frame
        :param track: Instance of Track
        """
        self.sensor_positions_local = sensor_positions_local
        self.track = track

    def get_readings(self, buggy_position, buggy_orientation):
        """
        :param buggy_position: np.array([x, y]) in world frame
        :param buggy_orientation: float (radians)
        :return: List of intensities [0..1] for each sensor
        """
        readings = []
        rotation = np.array([[np.cos(buggy_orientation), -np.sin(buggy_orientation)],
                             [np.sin(buggy_orientation),  np.cos(buggy_orientation)]])

        for local_pos in self.sensor_positions_local:
            world_pos = buggy_position + rotation @ local_pos
            intensity = self.track.get_line_intensity(world_pos)
            readings.append(intensity)

        return readings
