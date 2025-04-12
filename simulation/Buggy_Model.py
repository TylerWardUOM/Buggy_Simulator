import numpy as np
#left and right motor constans used to calculate wheel output speed based on input
#Motor_bias power bias between motors

#buggy model stores parameters from tests that relate to buggy characteristics
#calls functions to simulate effects or physics uses this undecided
class Buggy:
    def __init__(self, left_wheel, right_wheel, track_width, mass):
        self.left_wheel = left_wheel
        self.right_wheel = right_wheel
        self.track_width = track_width
        self.mass = mass

        # Initial state (position, orientation)
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.velocity = 0.0  # Linear velocity of the buggy
        self.angular_velocity = 0.0  # Angular velocity (yaw rate)

    def calculate_forces(self, voltage_left, voltage_right, F_gravity):
        force_left = self.left_wheel.get_force(voltage_left, F_gravity / 2)
        force_right = self.right_wheel.get_force(voltage_right, F_gravity / 2)

        F_x = force_left + force_right  # Forward force along the x-axis
        torque_yaw = (force_right - force_left) * self.track_width  # Yaw torque

        return F_x, torque_yaw
    
    def calculate_acceleration(self, F_x_total, torque_yaw):
        a_x = F_x_total / self.mass  # Translational acceleration

        I_yaw = self.mass * (self.track_width / 2)**2  # Approximate inertia for yaw
        alpha_yaw = torque_yaw / I_yaw  # Rotational acceleration

        return a_x, alpha_yaw

    def calculate_gravity_force(self, slope_angle):
        return self.mass * 9.81 * np.sin(np.deg2rad(slope_angle))  # Force due to gravity along the slope

    def update(self, voltage_left, voltage_right, slope_angle, dt):
        F_gravity = self.calculate_gravity_force(slope_angle)

        # Update wheel dynamics
        self.left_wheel.update(voltage_left, F_gravity / 2, dt)
        self.right_wheel.update(voltage_right, F_gravity / 2, dt)

        # Calculate forces and accelerations
        F_x_total, torque_yaw = self.calculate_forces(voltage_left, voltage_right, F_gravity)
        a_x, alpha_yaw = self.calculate_acceleration(F_x_total, torque_yaw)

        # Update velocities based on accelerations
        self.velocity += a_x * dt
        self.angular_velocity += alpha_yaw * dt

        # Update position and orientation based on current velocities
        self.x += self.velocity * np.cos(self.theta) * dt
        self.y += self.velocity * np.sin(self.theta) * dt
        self.theta += self.angular_velocity * dt
