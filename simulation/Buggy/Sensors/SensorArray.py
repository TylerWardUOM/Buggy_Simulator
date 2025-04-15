import numpy as np
from ...Track.Track import Track

class SensorArray:
    def __init__(self, sensor_positions_local):
        """
        :param sensor_positions_local: List of np.array([x, y]) positions in buggy's local frame
        :param track: Instance of Track
        """
        self.sensor_positions_local = sensor_positions_local

    def get_positions(self, buggy_position, buggy_orientation):
        world_poss = []
        #print(buggy_position)
        rotation = np.array([[np.cos(buggy_orientation), -np.sin(buggy_orientation)],
                            [np.sin(buggy_orientation),  np.cos(buggy_orientation)]])

        for local_pos in self.sensor_positions_local:
            world_pos = buggy_position + rotation @ local_pos
            world_poss.append(world_pos)
        return world_poss
    
    def get_readings(self, buggy_position, buggy_orientation, track: Track):
        """
        :param buggy_position: np.array([x, y]) in world frame
        :param buggy_orientation: float (radians)
        :return: List of intensities [0..1] for each sensor
        """
        closest = track.get_closest_point(buggy_position)
        readings = []
        world_poss = []
        rotation = np.array([[np.cos(buggy_orientation), -np.sin(buggy_orientation)],
                             [np.sin(buggy_orientation),  np.cos(buggy_orientation)]])

        for local_pos in self.sensor_positions_local:
            world_pos = buggy_position + rotation @ local_pos
            world_poss.append(world_pos)
            intensity = track.get_line_intensity(closest,world_pos)
            readings.append(intensity)

        return readings
