import numpy as np
import matplotlib.pyplot as plt
from Gearbox_Model import Gearbox
from Motor_Model import Motor
from Wheel_Model import Wheel
from Buggy import Buggy
from Battery import Battery
from MotorDriveBoard import MotorDriveBoard

def rotation_matrix(angle):
    return np.array([[np.cos(angle), -np.sin(angle)],
                     [np.sin(angle),  np.cos(angle)]])

#Motor Constants
armature_resistance = 1.8375 #Ohms
brush_voltage = 0.2315 #V
torque_constant = 0.0082 #NmA^-1
emf_constant = 0.0081 #NmA^-1
motor_max_current = 1.35 #A
motor_inertia = 0.0

#Gearbox Constants
gear_ratio = 18.75 #Ideal from DR1
gearbox_efficiency = 0.7224   #0.85*0.85
gearbox_inertia = 0.0

#Wheel Constants
wheel_radius = 0.075 #m
wheel_inertia = 0

#Buggy Constants
buggy_weight = 1.472 #Kg
buggy_track_width = 0.22 #m
friction_coefficent = 0.088

left_motor = Motor(armature_resistance, brush_voltage, torque_constant, emf_constant, motor_max_current, motor_inertia)
right_motor = Motor(armature_resistance, brush_voltage, torque_constant, emf_constant, motor_max_current, motor_inertia)
gearbox = Gearbox(gear_ratio, gearbox_inertia, gearbox_efficiency)
left_wheel = Wheel(left_motor, gearbox, wheel_radius, wheel_inertia)
right_wheel = Wheel(left_motor, gearbox, wheel_radius, wheel_inertia)
battery = Battery(10, 0.8)
motor_drive_board = MotorDriveBoard()
buggy = Buggy(left_wheel, right_wheel, buggy_track_width, buggy_weight, battery, motor_drive_board, friction_coefficent)

# Initial Stat
buggy.orientation = np.deg2rad(0)

# Function to generate updated voltages and slope angle as the simulation progresses
def simulate_motion(duty_left_func, duty_right_func,slope_angle_func, buggy, time_steps=10000, dt=0.001):
    # Simulate the motion over time
    x_traj, y_traj, theta_traj = [], [], []
    left_omega, right_omega = [], []
    left_duty, right_duty = [], []
    position_log = []  # Log of the vehicle's x and y positions
    
    for t in range(time_steps):
        # Get the updated duty cycle for the left and right wheels
        duty_left = duty_left_func(t, dt)
        duty_right = duty_right_func(t, time_steps)
        slope_angle = slope_angle_func(buggy.position)
        left_duty.append(duty_left)
        right_duty.append(duty_right)
        
        # Update the buggy state
        buggy.set_duty(duty_left,duty_right)
        #print(slope_angle)
        buggy.update(slope_angle, dt)
        
        # Collect data
        position_log.append(buggy.position[0])  # Log x position of the buggy
        
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
    
    return x_traj, y_traj, theta_traj, left_omega, right_omega, left_duty, right_duty, position_log

def duty_left_func(t, dt):
    duty = 1.0 + 0 * t  # Keep duty for the left wheel constant over time
    if duty >= 0.8:
        duty = 0.8
    return duty

def duty_right_func(t, time_steps):
    duty = 1+0.5*(t/time_steps)  # Increase duty for the right wheel over time
    if duty >= 0.8:
        duty = 0.8
    return duty

def slope_angle_func(position):
    """
    This function defines the slope of the terrain based on the buggy's x position.
    We will simulate a simple sinusoidal terrain for testing purposes.
    """
    # Example slope based on the buggy's x position
    # The terrain could be a sine wave or any other function
    amplitude = 14  # maximum slope in degrees
    wavelength = 10  # length of one cycle (the distance between peaks)
    return amplitude * np.sin(2 * np.pi * position[0] / wavelength)

dt = 0.0001
simulation_time = 5  # s
time_steps = int(simulation_time / dt)
x_traj, y_traj, theta_traj, left_omega, right_omega, left_voltage, right_voltage, position_log = simulate_motion(duty_left_func, duty_right_func,slope_angle_func, buggy, time_steps, dt)

print(left_omega[-1])

time = np.linspace(0, time_steps * dt, time_steps)

# Plotting the results
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

# Subplot 3: Terrain slope angle over time based on the position
slope_angles = [slope_angle_func((pos,0)) for pos in position_log]
axs[2].plot(time, slope_angles, label="Slope Angle", color='g')
axs[2].set_title("Slope Angle Over Time (Based on Position)")
axs[2].set_xlabel("Time (seconds)")
axs[2].set_ylabel("Slope Angle (degrees)")
axs[2].grid(True)
axs[2].legend()

# Subplot 4: Buggy orientation over time
axs[3].plot(time, theta_traj, label="Orientation", color='r')
axs[3].set_title("Orientation Over Time")
axs[3].set_xlabel("Time (seconds)")
axs[3].set_ylabel("Orientation (rad)")
axs[3].grid(True)
axs[3].legend()

plt.tight_layout()
plt.show()
