import numpy as np
import matplotlib.pyplot as plt
from simulation.Track.Track import *
from simulation.Buggy.Sensors.SensorArray import SensorArray 
from simulation.Buggy.Buggy import *
from visulization.PlotTrack import *
from control.CalculateError import calculate_error
from control.BangBang import BangBang
buggy_path = "buggy_profiles.json"
buggys = load_buggys(buggy_path)
buggy = select_buggy(buggys)
track_path = "track.json"
tracks=load_tracks(track_path)
track = select_track(tracks)


def simulate_motion(control_func, buggy: Buggy, track: Track, time_steps=10000, dt=0.001):
    # Simulate the motion over time
    x_traj, y_traj, theta_traj = [], [], []
    left_omega, right_omega = [], []
    left_duty, right_duty = [], []
    slope_angles = []
    sensor_values = []
    error_values=[]
    sensor_positions=[]
    position_log = []  # Log of the vehicle's x and y positions
    lost_count = 0
    
    for t in range(time_steps):
        # Get the updated duty cycle for the left and right wheels
        sensor_value = buggy.sensor_array.get_readings(buggy.position,buggy.orientation,track)
        if t%10 == 0:
            duty_left,duty_right = control_func(sensor_value,buggy.motor_drive_board.duty_left,buggy.motor_drive_board.duty_right)
            buggy.set_duty(duty_left,duty_right)
        slope_angle = track.get_slope_angle_at_position(buggy.position.copy())
        cur_sensor_positions = buggy.sensor_array.get_positions(buggy.position,buggy.orientation)
        left_duty.append(duty_left)
        right_duty.append(duty_right)
        slope_angles.append(slope_angle)
        sensor_values.append(sensor_value)
        error_values.append(calculate_error(sensor_value))
        sensor_positions.append(cur_sensor_positions)
        
        # Update the buggy state
        buggy.set_duty(duty_left,duty_right)
        #print(slope_angle)
        buggy.update(slope_angle, dt)
        
        # Collect data
        position_log.append(buggy.position.copy())
        x_traj.append(buggy.position[0])
        y_traj.append(buggy.position[1])
        theta_traj.append(np.rad2deg(buggy.orientation))
        
        if buggy.left_wheel.omega < 0:
            left_omega.append(0)
        else:
            left_omega.append((buggy.left_wheel.omega / (2 * np.pi)) * 60)

        if buggy.right_wheel.omega < 0:
            right_omega.append(0)
        else:
            right_omega.append((buggy.right_wheel.omega / (2 * np.pi)) * 60)

        if sum(sensor_value)<0.0001:
            lost_count+=1
            if lost_count>=time_steps*0.1:
                return x_traj, y_traj, theta_traj, left_omega, right_omega, left_duty, right_duty, slope_angles, position_log,sensor_values,t+1, error_values,sensor_positions
        else:
            count=0
    return x_traj, y_traj, theta_traj, left_omega, right_omega, left_duty, right_duty, slope_angles, position_log,sensor_values,t+1,error_values,sensor_positions



dt = 0.0005
simulation_time = 10  # s
time_steps = int(simulation_time / dt)

results = simulate_motion(BangBang, buggy, track,time_steps, dt)

x_traj, y_traj = results[0], results[1]
theta_traj = results[2]
left_omega, right_omega = results[3], results[4]
duty_lefts, duty_rights = results[5], results[6]
slope_angles = results[7]
position_log = results[8]
sensor_values = results[9]
time_steps = results[10]
error_values = results[11]
sensor_positions = results[12]

sensor1,sensor2,sensor3 = [],[],[]
for values in sensor_values:
    sensor1.append(values[0])
    sensor2.append(values[1])
    sensor3.append(values[2])

buggy_x,buggy_y =[],[]
for cords in position_log:
    buggy_x.append(cords[0])
    buggy_y.append(cords[1])

sensor2_x,sensor2_y = [], []
for sensor in sensor_positions:
    sensor2_x.append(sensor[1][0])
    sensor2_y.append(sensor[1][1])
    
print(time_steps)
time = np.linspace(0, time_steps * dt, time_steps)
# Plotting the results
fig, axs = plt.subplots(5, 1, figsize=(10, 8))

# Subplot 1: Vehicle trajectory
axs[0].plot(buggy_x, buggy_y, label="Vehicle Trajectory")
axs[0].plot(sensor2_x, sensor2_y, label="sensor Trajectory")
# Mark time every N seconds
marker_interval = int(1 / dt)  # every 1 second
for i in range(0, len(buggy_x), marker_interval):
    axs[0].annotate(f"{i*dt:.0f}s", (buggy_x[i], buggy_y[i]),
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

axs[4].plot(time, sensor1, label="right", color='b')
axs[4].plot(time, sensor2, label="middle", color='r')
axs[4].plot(time, sensor3, label="left", color='g')
axs[4].plot(time, error_values, label="error", color='y')
axs[4].set_title("Sensor Over Time")
axs[4].set_xlabel("Time (seconds)")
axs[4].set_ylabel("Sensor (intentisty)")
axs[4].grid(True)
axs[4].legend()

plt.tight_layout()
plt.show()
#plot_track(track,True)
plot_track_with_buggy(track,position_log,True)
#plot_track_with_buggy_animated(track,position_log,interval=50,show_elevation=True)