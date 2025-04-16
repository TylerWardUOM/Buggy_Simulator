import numpy as np
import random
import matplotlib.pyplot as plt
from simulation.Track.Track import *
from simulation.Buggy.Sensors.SensorArray import SensorArray 
from simulation.Buggy.Buggy import *
from visulization.PlotTrack import *
from control.CalculateError import calculate_error
from control.BangBang import BangBang
from simulation.Simulation import simulate_motion

dev=False

buggy_path = "buggy_profiles.json"
buggys = load_buggys(buggy_path)
buggy = select_buggy(buggys)
track_path = "track.json"
tracks=load_tracks(track_path)
track = select_track(tracks)

if dev:        
    dt = 0.001
    simulation_time = 10  # s
else:
    dt=float(input("Enter Simulation Period (s): "))
    simulation_time=float(input("Enter Simulation Duration: "))
time_steps = int(simulation_time / dt)

results = simulate_motion(BangBang,0.01, buggy, track,time_steps, dt)

# def convert_to_serializable(obj):
#     if isinstance(obj, np.ndarray):
#         return obj.tolist()
#     if isinstance(obj, (np.float32, np.float64, np.int32, np.int64)):
#         return obj.item()
#     if isinstance(obj, dict):
#         return {k: convert_to_serializable(v) for k, v in obj.items()}
#     if isinstance(obj, list):
#         return [convert_to_serializable(i) for i in obj]
#     return obj
# serializable_results = convert_to_serializable(results)

# with open("PrevResults.json", "w") as last_results_file:
#     json.dump(serializable_results, last_results_file, indent=2)


# Unpack from dictionary
orientation_log = results["orientation_log"]
left_omega = results["left_omega"]
right_omega = results["right_omega"]
duty_lefts = results["left_duty"]
duty_rights = results["right_duty"]
slope_angles = results["slope_angles"]
position_log = results["position_log"]
sensor_values = results["sensor_values"]
sensor_positions = results["sensor_positions"]
time_steps = results["time_steps"]
error_values = results["error_values"]

average_wheel_speed = []
for i in range(len(left_omega)):
    average_wheel_speed.append((left_omega[i]+right_omega[i])/2)
# Initialize empty lists for each sensor dynamically
num_sensors = len(sensor_values[0])  # assume at least one reading exists
sensor_series = [[] for _ in range(num_sensors)]
sensor_position_series = [[] for _ in range(num_sensors)]

# Fill each sensor's time series
for values in sensor_values:
    for i in range(num_sensors):
        sensor_series[i].append(values[i])

buggy_x,buggy_y =[],[]
for cords in position_log:
    buggy_x.append(cords[0])
    buggy_y.append(cords[1])

# Fill each sensor's positional time series
for values in sensor_positions:
    for i in range(num_sensors):
        sensor_position_series[i].append((values[i][0], values[i][1]))

    
time = np.linspace(0, time_steps * dt, time_steps)
# Plotting the results
fig, axs = plt.subplots(5, 1, figsize=(10, 8))
for i, series in enumerate(sensor_position_series):
    x_vals = [pos[0] for pos in series]
    y_vals = [pos[1] for pos in series]
    color = (random.random(), random.random(), random.random())
    axs[0].plot(x_vals, y_vals, label=f"Sensor {i+1}", color=color)
marker_interval = int(0.5 / dt)  # every 1 second
for i in range(0, len(buggy_x), marker_interval):
    axs[0].annotate(f"{i*dt:.1f}s", (buggy_x[i], buggy_y[i]),
                    textcoords="offset points", xytext=(5,5), ha='left', fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.5))
axs[0].set_title("Differential Drive Vehicle Motion")
axs[0].set_xlabel("X Position (meters)")
axs[0].set_ylabel("Y Position (meters)")
axs[0].grid(True)
axs[0].legend()

# Subplot 2: Wheel angular velocities
axs[1].plot(time, left_omega, label="Left Wheel ω", color='b')
axs[1].plot(time, right_omega, label="Right Wheel ω", color='r')
axs[1].plot(time, average_wheel_speed, label="Average Wheel ω", color='g')
axs[1].set_title("Wheel Angular Velocities Over Time")
axs[1].set_xlabel("Time (seconds)")
axs[1].set_ylabel("Angular Velocity (RPM)")
axs[1].grid(True)
axs[1].legend()

# Subplot 3: Terrain slope angle over time based on the position
axs[2].plot(time, slope_angles, label="Slope Angle", color='g')
axs[2].set_title("Slope Angle Over Time (Based on Position)")
axs[2].set_xlabel("Time (seconds)")
axs[2].set_ylabel("Slope Angle (degrees)")
axs[2].grid(True)
axs[2].legend()

# Subplot 4: Buggy orientation over time
axs[3].plot(time, duty_lefts, label="Left", color='b')
axs[3].plot(time, duty_rights, label="RIght", color='r')
axs[3].set_title("Orientation Over Time")
axs[3].set_xlabel("Time (seconds)")
axs[3].set_ylabel("Orientation (rad)")
axs[3].grid(True)
axs[3].legend()

for i, series in enumerate(sensor_series):
    color = (random.random(), random.random(), random.random())
    axs[4].plot(time, series, label=f"Sensor {i+1}", color=color)
axs[4].plot(time, error_values, label="error", color='g')
axs[4].set_title("Sensor Over Time")
axs[4].set_xlabel("Time (seconds)")
axs[4].set_ylabel("Sensor (intentisty)")
axs[4].grid(True)
axs[4].legend()

plt.tight_layout()
plt.show()
#plot_track(track,True)
plot_track_with_buggy(track,position_log,True)
#plot_track_with_buggy_animated(track,position_log,interval=5,show_elevation=True)