import numpy as np
import json
from .Wheel.Wheel_Model import Wheel
from .Wheel.Motor_Model import Motor
from .Wheel.Gearbox_Model import Gearbox
from .Power.MotorDriveBoard import MotorDriveBoard
from .Power.Battery import Battery
#Buggy Local Coordinate frame origin at the centre of mass
#X along Direction of travel
def rotation_matrix(angle):
    return np.array([[np.cos(angle), -np.sin(angle)],
                     [np.sin(angle),  np.cos(angle)]])

def perpendicular(vec):
    return np.array([-vec[1], vec[0]])

class Buggy:
    def __init__(self, left_wheel: Wheel, right_wheel: Wheel, track_width, mass, battery: Battery, motor_drive_board: MotorDriveBoard, friction_coefficient):
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
    
    def calculate_normal_force(self,slope_angle):
        world_normal = np.array([self.mass * 9.81 * np.cos(np.deg2rad(slope_angle)),0])
        r_inverse = rotation_matrix(-self.orientation)
        return r_inverse @ world_normal
    
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

        #Only along wheel path for now
        resitive_forces = force_gravity[0] + force_friction[0]
        normal_force_wheel = self.calculate_normal_force(slope_angle)[0] / 2

        voltage_left = self.motor_drive_board.get_voltage_left(self.battery)
        voltage_right = self.motor_drive_board.get_voltage_right(self.battery)

        #self.left_wheel.update_dynamics(voltage_left,normal_force_wheel,dt)
        #self.right_wheel.update_dynamics(voltage_right,normal_force_wheel,dt)
        force_left = self.left_wheel.get_drive_force(voltage_left,normal_force_wheel)
        force_right = self.right_wheel.get_drive_force(voltage_right,normal_force_wheel)
        # Total forward force from both wheels
        force_motor_total = (force_left + force_right)
        # Net force: motor force reduced by the gravitational force along the slope.
        force_net = np.array([force_motor_total,0])+resitive_forces
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



def load_buggys(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    buggys = []
    for buggy_id, info in data.items():
        name = info.get("name", buggy_id)
        motor = info.get("motor", {})
        gearbox_data = info.get("gearbox", {})
        wheel = info.get("wheel", {})
        buggy = info.get("buggy", {})
        battery = info.get("battery", {})

        left_motor = Motor(
            motor["armature_resistance"],
            motor["brush_voltage"],
            motor["torque_constant"],
            motor["emf_constant"],
            motor["motor_max_current"],
            motor["motor_inertia"]
        )
        right_motor = left_motor  # Share the same motor instance (or create new if needed)

        gearbox = Gearbox(
            gearbox_data["gear_ratio"],
            gearbox_data["gearbox_inertia"],
            gearbox_data["gearbox_efficiency"]
        )

        left_wheel = Wheel(left_motor, gearbox, wheel["wheel_radius"], wheel["wheel_inertia"])
        right_wheel = Wheel(right_motor, gearbox, wheel["wheel_radius"], wheel["wheel_inertia"])

        buggy_battery = Battery(battery["nominal_voltage"], battery["internal_resistance"])
        motor_drive_board = MotorDriveBoard()

        buggy_instance = Buggy(
            left_wheel,
            right_wheel,
            buggy["track_width"],
            buggy["weight"],
            buggy_battery,
            motor_drive_board,
            buggy["friction_coefficient"]
        )

        buggys.append((name, buggy_instance))

    return buggys



def select_buggy(buggys):
    print("Available Buggys:")
    for i, buggy in enumerate(buggys):
        print(f"{i + 1}. {buggy[0]}")

    while True:
        selected = input("Type the buggy name or number to select it: ").strip()

        # Try numeric selection
        if selected.isdigit():
            index = int(selected) - 1
            if 0 <= index < len(buggys):
                selected_buggy = buggys[index]
                print("Selected Buggy:", selected_buggy[0])
                return selected_buggy[1]
            else:
                print("Invalid number. Please choose a valid index.")

        # Try name-based selection (case-insensitive)
        else:
            for buggy in buggys:
                if buggy[0].lower() == selected.lower():
                    print("Selected Buggy:", buggy[0])
                    return buggy[1]

            print("Not a valid track name. Please choose from the list above.")