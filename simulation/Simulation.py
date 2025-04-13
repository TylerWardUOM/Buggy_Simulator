import numpy as np
import matplotlib.pyplot as plt
from Gearbox_Model import Gearbox
from Motor_Model import Motor
from Wheel_Model import Wheel
from Buggy import Buggy

def rotation_matrix(angle):
    return np.array([[np.cos(angle), -np.sin(angle)],
                     [np.sin(angle),  np.cos(angle)]])

#Motor Constants
armature_resistance = 1.8375 #Ohms
brush_voltage = 0.2315 #V
torque_constant = 0.0082 #NmA^-1
emf_constant = 0.0081 #NmA^-1
motor_max_current=1.35 #A
motor_inertia = 0.0

#Gearbox Constants
gear_ratio = 18.75 #Ideal from DR1
gearbox_efficency = 0.7224   #0.85*0.85
gearbox_inertia = 0.0

#Wheel Constants
wheel_radius = 0.075 #m
wheel_inertia = 0.0
#Buggy Constants
buggy_weight = 1.472 #Kg
buggy_track_width = 0.22 #m

left_motor = Motor(armature_resistance,brush_voltage,torque_constant,emf_constant,motor_max_current,motor_inertia)
right_motor = Motor(armature_resistance,brush_voltage,torque_constant,emf_constant,motor_max_current,motor_inertia)
gearbox = Gearbox(gear_ratio,gearbox_inertia,gearbox_efficency)
left_wheel = Wheel(left_motor,gearbox,wheel_radius,wheel_inertia)
right_wheel = Wheel(left_motor,gearbox,wheel_radius,wheel_inertia)
buggy = Buggy(left_wheel,right_wheel,buggy_track_width,buggy_weight)

#Initital Stat
#buggy.left_wheel.omega=150.0
#buggy.right_wheel.omega=150.0
buggy.orientation = np.deg2rad(00)
# Function to generate updated voltages and slope angle as the simulation progresses
def simulate_motion(voltage_left_func, voltage_right_func, slope_angle_func, buggy, time_steps=10000, dt=0.001):
    # Simulate the motion over time
    x_traj, y_traj, theta_traj = [], [], []
    left_omega, right_omega = [], []
    left_voltage,right_voltage,slope_angle_log = [], [], []
    
    for t in range(time_steps):
        # Get the updated voltage and slope for the current time step
        voltage_left = voltage_left_func(t, dt)
        voltage_right = voltage_right_func(t, dt)
        slope_angle = slope_angle_func(time_steps,t, dt)
        left_voltage.append(voltage_left)
        right_voltage.append(voltage_right)
        slope_angle_log.append(slope_angle)
        # Update the buggy state
        buggy.update(voltage_left, voltage_right, slope_angle, dt)
        
        # Convert to world frame and collect data
        r = rotation_matrix(buggy.orientation)
        world_position = r @ buggy.position
        
        x_traj.append(world_position[0])
        y_traj.append(world_position[1])
        theta_traj.append(buggy.orientation)
        
        if buggy.left_wheel.omega < 0:
            left_omega.append(0)
        else:
            left_omega.append((buggy.left_wheel.omega / (2 * np.pi)) * 60)

        if buggy.right_wheel.omega < 0:
            right_omega.append(0)
        else:
            right_omega.append((buggy.right_wheel.omega / (2 * np.pi)) * 60)

    
    return x_traj, y_traj, theta_traj, left_omega, right_omega, left_voltage, right_voltage, slope_angle_log

def voltage_left_func(t, dt):
    voltage = 10.0 + 0 * t  # Increase voltage for the left wheel over time
    if voltage>=7:
        voltage=7
    return voltage

def voltage_right_func(t, dt):
    voltage = 6 + 0.5 * t* dt   # Increase voltage for the right wheel over time
    if voltage>=6:
        voltage=6
    return voltage

def slope_angle_func(time_steps, t, dt):
    # Cycle duration (time for a full up-down cycle)
    cycle_duration = time_steps  # Choose a suitable cycle length
    cycle_position = t % cycle_duration  # Get position in the cycle
    
    # Define the phases of the cycle:
    # 0 -> Ramp up from 0 to 18 degrees,
    # 1 -> Hold at 18 degrees,
    # 2 -> Ramp down from 18 to 0 degrees,
    # 3 -> Hold at 0 degrees,
    # 4 -> Ramp down from 0 to -18 degrees,
    # 5 -> Hold at -18 degrees.
    
    if cycle_position < 0.1 * cycle_duration:  # First phase: Ramp from 0 to 18 degrees
        return 18 * np.sin(np.pi * cycle_position / (0.2 * cycle_duration))
    
    elif cycle_position < 0.3 * cycle_duration:  # Second phase: Hold at 18 degrees
        return 18
    
    elif cycle_position < 0.4 * cycle_duration:  # Third phase: Ramp down from 18 to 0 degrees
        return 18 * np.cos(np.pi * (cycle_position - 0.3 * cycle_duration) / (0.2 * cycle_duration))
    
    elif cycle_position < 0.79 * cycle_duration:  # Fourth phase: Hold at 0 degrees
        return 0
    
    elif cycle_position < 0.80 * cycle_duration:  # Fifth phase: Ramp down from 0 to -18 degrees
        return -18 * np.sin(np.pi * (cycle_position - 0.8 * cycle_duration) / (0.2 * cycle_duration))
    
    elif cycle_position < 0.9 * cycle_duration:  # Sixth phase: Hold at -18 degrees
        return -18
    
    # Last phase: Return to 0 degrees
    return 0



dt = 0.01
simulation_time = 100 #s
time_steps = int(simulation_time/dt)
x_traj, y_traj, theta_traj, left_omega, right_omega, left_voltage, right_voltage, slope_angle_log = simulate_motion(voltage_left_func, voltage_right_func,slope_angle_func,buggy, time_steps,dt)

print(left_omega[-1])
time = np.linspace(0, time_steps * dt, time_steps)

fig, axs = plt.subplots(4, 1, figsize=(10, 8))

# Subplot 1: Vehicle trajectory
axs[0].plot(x_traj, y_traj, label="Vehicle Trajectory")
axs[0].set_title("Differential Drive Vehicle Motion")
axs[0].set_xlabel("X Position (meters)")
axs[0].set_ylabel("Y Position (meters)")
axs[0].grid(True)
axs[0].legend()

# Subplot 2: Wheel angular velocities
axs[1].plot(time, left_omega, label="Left Wheel ω", color='r')
axs[1].plot(time, right_omega, label="Right Wheel ω", color='b')
axs[1].set_title("Wheel Angular Velocities Over Time")
axs[1].set_xlabel("Time (seconds)")
axs[1].set_ylabel("Angular Velocity (RPM)")
axs[1].grid(True)
axs[1].legend()

axs[2].plot(time, slope_angle_log, label="Y Position", color='r')
axs[2].set_title("Y Position Over Time")
axs[2].set_xlabel("Time (seconds)")
axs[2].set_ylabel("Y Position m")
axs[2].grid(True)
axs[2].legend()

axs[3].plot(time, theta_traj, label="Orientation", color='r')
axs[3].set_title("Orientation Over Time")
axs[3].set_xlabel("Time (seconds)")
axs[3].set_ylabel("Orientation (rad)")
axs[3].grid(True)
axs[3].legend()

plt.tight_layout()
plt.show()