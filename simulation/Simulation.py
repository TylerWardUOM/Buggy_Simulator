import numpy as np
import matplotlib.pyplot as plt
from Gearbox_Model import Gearbox
from Motor_Model import Motor
from Wheel_Model import Wheel
from Buggy_Model import Buggy

#Motor Constants
armature_resistance = 1.8375 #Ohms
brush_voltage = 0.2315 #V
torque_constant = 0.0082 #NmA^-1
emf_constant = 0.0081 #NmA^-1
motor_max_current=1.4 #A
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

#Initital State
voltage_left=10.0
voltage_right=10.0
slope_angle = 0.0
buggy.left_wheel.omega=150.0
buggy.right_wheel.omega=150.0
# Simulate for 100 time steps
def simulate_motion(voltage_left, voltage_right,slope_angle, buggy, time_steps=10000, dt=0.001):
    # Simulate the motion over time
    x_traj, y_traj, theta_traj = [], [], []
    left_omega, right_omega = [], []
    for t in range(time_steps):
        buggy.update(voltage_left, voltage_right,slope_angle, dt)
        x_traj.append(buggy.x)
        y_traj.append(buggy.y)
        theta_traj.append(buggy.theta)
        left_omega.append(buggy.left_wheel.omega)
        right_omega.append(buggy.right_wheel.omega)
    
    return x_traj, y_traj, theta_traj, left_omega, right_omega


dt = 0.001
simulation_time = 20 #s
time_steps = int(simulation_time/dt)
x_traj, y_traj, theta_traj, left_omega, right_omega = simulate_motion(voltage_left, voltage_right,slope_angle,buggy, time_steps,dt)

print(left_omega[-1])
time = np.linspace(0, time_steps * dt, time_steps)

fig, axs = plt.subplots(2, 1, figsize=(10, 8))

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
axs[1].set_ylabel("Angular Velocity (rad/s)")
axs[1].grid(True)
axs[1].legend()

plt.tight_layout()
plt.show()