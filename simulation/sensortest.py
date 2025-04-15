import numpy as np 
from Track.Track import Track
from Buggy.Sensors.SensorArray import SensorArray 
# Define a flat straight track
track = Track([(0, 0, 0), (10, 0, 0)], width=0.3)

# Define sensors: front-left, center, front-right
sensor_positions = [
    np.array([0.1, -0.05]),
    np.array([0.1,  0.0]),
    np.array([0.1,  0.05])
]

sensors = SensorArray(sensor_positions, track)

# Get readings for buggy at (1.0, 0.0), facing forward
position = np.array([1.0, 0.0])
orientation = 0.0  # radians

readings = sensors.get_readings(position, orientation)
print(readings)  # Example output: [0.3, 0.95, 0.3]
