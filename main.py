from simulation.Track.Track import *
from simulation.Buggy.Sensors.SensorArray import SensorArray 
from simulation.Buggy.Buggy import *

buggy_path = "buggy_profiles.json"
buggys = load_buggys(buggy_path)
buggy = select_buggy(buggys)
track_path = "track.json"
tracks=load_tracks(track_path)
track = select_track(tracks)
print(buggy.sensor_array.get_readings(buggy.position,buggy.orientation,track))