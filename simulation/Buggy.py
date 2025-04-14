import numpy as np
#Buggy Local Coordinate frame origin at the centre of mass
#X along Direction of travel
def rotation_matrix(angle):
    return np.array([[np.cos(angle), -np.sin(angle)],
                     [np.sin(angle),  np.cos(angle)]])

def perpendicular(vec):
    return np.array([-vec[1], vec[0]])

class Buggy:
    def __init__(self, left_wheel, right_wheel, track_width, mass, battery, motor_drive_board, friction_coefficient):
        self.left_wheel = left_wheel
        self.left_wheel_position = np.array([0.0,-10]) #x,y coords
        self.right_wheel = right_wheel
        self.right_wheel_position = np.array([0.0,10]) #x,y coords
        self.track_width = abs(np.linalg.norm(self.left_wheel_position - self.right_wheel_position))
        self.mass = mass
        self.battery = battery
        self.motor_drive_board = motor_drive_board
        self.friction_coefficient = friction_coefficient
        
        self.orientation = 0.0 #Angle (rad) relative to world frame 
        self.position = np.array([0.0,0.0])
        self.velocity = np.array([0.0,0.0])         # Linear velocity (m/s)
        self.angular_velocity = 0.0 # Angular velocity (rad/s)

    def reset(self):
        self.velocity = np.array([0.0,0.0])         # Linear velocity (m/s)
        self.angular_velocity = 0.0 # Angular velocity (rad/s)
        self.orientation = 0.0 #Angle (rad) relative to world frame 
        self.left_wheel.reset()
        self.right_wheel.reset()

    def calculate_gravity_force(self, slope_angle):
        world_gravity = np.array([self.mass * 9.81 * np.sin(np.deg2rad(slope_angle)),0])
        r_inverse = rotation_matrix(-self.orientation)
        return r_inverse @ world_gravity
    
    def calculate_friction_force(self, slope_angle):
        world_friction = np.array([self.mass * 9.81 * np.cos(np.deg2rad(slope_angle))*self.friction_coefficient,0])
        r_inverse = rotation_matrix(-self.orientation)
        return r_inverse @ world_friction
    
    def set_duty(self,duty_left,duty_right):
        if duty_left!=None:
            self.motor_drive_board.set_duty_left(duty_left)
        if duty_right!=None:
            self.motor_drive_board.set_duty_right(duty_right)

    def update(self, slope_angle, dt):
        """
        Update the buggy state for the time increment dt.
        This includes:
          - Updating wheel dynamics taking into account both motor torque and resistive torques.
          - Computing net forces on the buggy (subtracting gravity along the slope).
          - Updating the buggy's translational and rotational state.
        """
        # ----- Step 1. Compute gravitational force along the slope -----
        force_gravity = -self.calculate_gravity_force(slope_angle)
        force_friction = -self.calculate_friction_force(slope_angle)
        force_left = self.left_wheel.get_force(self.motor_drive_board.get_voltage_left(self.battery))
        force_right = self.right_wheel.get_force(self.motor_drive_board.get_voltage_right(self.battery))


        # Total forward force from both wheels
        force_motor_total = (force_left + force_right)

        # Net force: motor force reduced by the gravitational force along the slope.
        force_net = np.array([force_motor_total,0]) + force_gravity + force_friction

        acceleration_net = force_net / self.mass  # Linear acceleration (m/s^2)
        acceleration_net[1] = 0
        #Torque
        # Approximate moment of inertia for yaw (using a point mass model) 
        intertia_buggy = self.mass * (self.track_width / 2)**2
                # Yaw torque: difference in forces multiplied by track width (lever arm)
        torque_buggy = (force_right - force_left) * self.track_width
        angular_acceleration_buggy = torque_buggy / intertia_buggy  # Angular acceleration (rad/s^2)
        # Update velocities
        self.velocity += acceleration_net * dt
        self.angular_velocity += angular_acceleration_buggy * dt
        #Update Local Frame Position
        self.position += self.velocity * dt
        self.orientation += self.angular_velocity * dt

        left_wheel_velocity = self.velocity[0] + self.angular_velocity * self.left_wheel_position[1]
        right_wheel_velocity = self.velocity[0] + self.angular_velocity * self.right_wheel_position[1]

        #print(f"Torque: {torque_buggy}, Left Force: {force_left}, Right Force: {force_right}")
        #print(f"Left Wheel Velocity: {left_wheel_velocity}, Right Wheel Velocity: {right_wheel_velocity}")

        left_wheel_acceleration = force_left/self.mass
        right_wheel_acceleration = force_right/self.mass

        # ----- Step 3. Update wheel dynamics -----
        # Update each wheel by providing both the voltage and the normal force (for resistive effects)
        self.left_wheel.update(left_wheel_velocity)
        self.right_wheel.update(right_wheel_velocity)
        currentDraw = self.left_wheel.motor.current + self.right_wheel.motor.current
        self.battery.update(currentDraw)