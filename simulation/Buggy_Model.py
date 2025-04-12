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

        # Initial state: position (x, y), orientation (theta), and velocities
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.velocity = 0.0         # Linear velocity (m/s)
        self.angular_velocity = 0.0 # Angular velocity (rad/s)

    def calculate_gravity_force(self, slope_angle):
        """
        Calculate the component of gravitational force along the slope.
        For a given slope angle (in degrees), the force acting downhill is:
            F_gravity = mass * g * sin(slope_angle)
        """
        return self.mass * 9.81 * np.sin(np.deg2rad(slope_angle))

    def update(self, voltage_left, voltage_right, slope_angle, dt):
        """
        Update the buggy state for the time increment dt.
        This includes:
          - Updating wheel dynamics taking into account both motor torque and resistive torques.
          - Computing net forces on the buggy (subtracting gravity along the slope).
          - Updating the buggy's translational and rotational state.
        """
        # ----- Step 1. Compute gravitational force along the slope -----
        F_gravity = self.calculate_gravity_force(slope_angle)
        
        # ----- Step 2. Compute the normal force per wheel (assuming two wheels) -----
        # Normal force is the force perpendicular to the slope (mass*g*cos(slope))
        normal_force = F_gravity


        force_left = self.left_wheel.calculate_net_force(voltage_left,normal_force/2)
        force_right = self.right_wheel.calculate_net_force(voltage_right,normal_force/2)


        # Total forward force from both wheels
        F_x_total = force_left + force_right
        # Yaw torque: difference in forces multiplied by track width (lever arm)
        torque_yaw = (force_right - force_left) * self.track_width

        # Net forward force: motor force reduced by the gravitational force along the slope.
        F_net = F_x_total - F_gravity

        # ----- Step 5. Update buggy linear and angular acceleration/velocity -----
        a_x = F_net / self.mass  # Linear acceleration (m/s^2)
        # Approximate moment of inertia for yaw (using a point mass model) 
        I_yaw = self.mass * (self.track_width / 2)**2
        alpha_yaw = torque_yaw / I_yaw  # Angular acceleration (rad/s^2)

        # Update velocities
        self.velocity += a_x * dt
        self.angular_velocity += alpha_yaw * dt

        # ----- Step 6. Update position and orientation -----
        self.x += self.velocity * np.cos(self.theta) * dt
        self.y += self.velocity * np.sin(self.theta) * dt
        self.theta += self.angular_velocity * dt

        left_wheel_acceleration = force_left/self.mass
        right_wheel_acceleration = force_right/self.mass

        # ----- Step 3. Update wheel dynamics -----
        # Update each wheel by providing both the voltage and the normal force (for resistive effects)
        self.left_wheel.update(left_wheel_acceleration, dt)
        self.right_wheel.update(right_wheel_acceleration, dt)
