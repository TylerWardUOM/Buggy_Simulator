import math

class Wheel:
    def __init__(self, wheel_radius, gearbox_ratio, motor_resistance, brush_voltage, torque_constant, max_motor_voltage=10, 
                 max_current=1.35, motor_inertia=0.01, wheel_inertia=0.01):
        self.wheel_radius = wheel_radius
        self.gearbox_ratio = gearbox_ratio
        self.motor_resistance = motor_resistance
        self.brush_voltage = brush_voltage
        self.torque_constant = torque_constant
        self.max_motor_voltage = max_motor_voltage
        self.max_current = max_current
        self.motor_inertia = motor_inertia  
        self.wheel_inertia = wheel_inertia
        self.wheel_torque = 0
        
        self.motor_angular_velocity = 0  
        self.wheel_angular_velocity = 0  

    def motor_torque(self, pwm_value):
        """Calculates the torque produced by the motor, considering back EMF."""
        motor_voltage = (pwm_value / 255.0) * self.max_motor_voltage  

        # Motor current considering back EMF
        current = (motor_voltage - (self.torque_constant * self.motor_angular_velocity)) / self.motor_resistance
        current = min(current, self.max_current)  # Limit current

        # Motor torque: T = k_T * I
        motor_torque = self.torque_constant * current  
        return motor_torque

    def update_wheel_velocity(self, pwm_value, time_step, gravity_torque):
        """Updates the wheel's angular velocity based on motor torque, gearbox, and gravity effects."""
        motor_torque = self.motor_torque(pwm_value)  # Torque at motor
        self.wheel_torque = (motor_torque * self.gearbox_ratio) - gravity_torque  # Apply opposing gravity torque

        # Calculate wheel angular acceleration using **wheel inertia**
        wheel_angular_acceleration = self.wheel_torque / self.wheel_inertia  
        self.wheel_angular_velocity += wheel_angular_acceleration * time_step

        # Convert back to motor angular velocity
        self.motor_angular_velocity = self.wheel_angular_velocity * self.gearbox_ratio  

        return self.wheel_angular_velocity


    def force_at_wheel(self):
        """Calculates the force at the wheel using torque and radius."""
        return self.wheel_torque / self.wheel_radius  


class LineFollowingBuggy:
    def __init__(self, mass, wheel_radius, gearbox_ratio, friction_coefficient, track_width, gravity=9.81):
        self.mass = mass  
        self.gravity = gravity  
        self.friction_coefficient = friction_coefficient  
        self.track_width = track_width  

        # Create two wheels
        self.left_wheel = Wheel(wheel_radius, gearbox_ratio, motor_resistance=1.8375, brush_voltage=0.2315, torque_constant=0.0082)
        self.right_wheel = Wheel(wheel_radius, gearbox_ratio, motor_resistance=1.8375, brush_voltage=0.2315, torque_constant=0.0082)

        self.velocity = 0  
        self.angular_velocity = 0  

    def compute_gravity_torque(self, slope_angle_deg):
        """Calculates the torque due to gravity that opposes motion."""
        slope_angle_rad = math.radians(slope_angle_deg)  
        gravity_force = self.mass * self.gravity * math.sin(slope_angle_rad)  

        # Gravity torque on each wheel
        gravity_torque = (gravity_force * (self.track_width / 2)) / 2  
        return gravity_torque

    def update_motion(self, left_pwm, right_pwm, slope_angle_deg, time_step):
        """Updates the buggy’s velocity and yaw rate based on wheel inputs and gravity effects."""
        
        gravity_torque = self.compute_gravity_torque(slope_angle_deg)

        # Update each wheel's angular velocity considering gravity torque
        left_wheel_velocity = self.left_wheel.update_wheel_velocity(left_pwm, time_step, gravity_torque)
        right_wheel_velocity = self.right_wheel.update_wheel_velocity(right_pwm, time_step, gravity_torque)

        # Convert to linear velocities
        v_left = left_wheel_velocity * self.left_wheel.wheel_radius
        v_right = right_wheel_velocity * self.right_wheel.wheel_radius

        # Compute forward velocity (center of the buggy)
        self.velocity = (v_left + v_right) / 2

        # Compute yaw rate (turning speed)
        self.angular_velocity = (v_right - v_left) / self.track_width  

        return self.velocity, self.angular_velocity

# Example usage
buggy = LineFollowingBuggy(mass=1.3, wheel_radius=0.0375,
                           gearbox_ratio=13.5, friction_coefficient=0.2, track_width=0.2)

left_pwm = 255  
right_pwm = 255  
slope_angle = 0  
time_step = 0.1  

for _ in range(200):  # Simulate for 10 seconds
    if _ > 50:
        slope_angle = 18  

    velocity, angular_velocity = buggy.update_motion(left_pwm, right_pwm, slope_angle, time_step)
    print(f"Time: {_ * time_step:.2f}s, Velocity: {velocity:.2f} m/s, Yaw Rate: {angular_velocity:.2f} rad/s")
