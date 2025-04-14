import numpy as np

class Wheel:
    def __init__(self, motor, gearbox, radius, inertia, rolling_resistance_coeff=0.01):
        """
        Initialize the Wheel with a given motor, gearbox, wheel radius, and inertia.
        The rolling_resistance_coeff is a tunable parameter for resistive torques.
        """
        self.motor = motor
        self.gearbox = gearbox
        self.radius = radius
        self.inertia = inertia
        # Total inertia includes contributions from wheel, gearbox, and motor.
        self.total_inertia = inertia + self.gearbox.inertia + self.motor.inertia
        self.effective_inertia = self.total_inertia if self.total_inertia != 0 else 1e-4
        self.omega = 0.0  # Angular velocity (rad/s)
        self.rolling_resistance_coeff = rolling_resistance_coeff

    def reset(self):
        """Reset the wheel's angular velocity to zero."""
        self.omega = 0.0

    def compute_motor_torque(self, voltage):
        """
        Compute the output torque produced by the motor (converted through the gearbox).

        :param voltage: The applied voltage to the motor.
        :return: The output torque at the wheel.
        """
        # Convert the wheel's angular speed to the motor's side.
        motor_omega = self.gearbox.input_speed_from_output(self.omega)
        motor_torque = self.motor.get_torque(voltage, motor_omega)
        # Convert motor torque to the wheel's output torque via the gearbox.
        return self.gearbox.output_torque(motor_torque)
    
    def compute_net_torque(self, voltage, normal_force):
        """
        Calculate the net torque at the wheel taking into account:
          - The motor's output torque.
          - The rolling resistance torque which opposes the current rotation.

        :param voltage: The applied voltage to the motor.
        :param normal_force: The normal force at the wheel (used for calculating resistive effects).
        :return: The net torque available at the wheel.
        """
        # Motor torque through gearbox.
        motor_torque = self.compute_motor_torque(voltage)
        # Resistive torque: it is proportional to the normal force and opposes the current motion.
        # The np.sign(self.omega) returns +1 when omega>0 and -1 when omega<0. Flipping it applies the resistive torque in the opposite direction.
        direction = -np.sign(self.omega) if self.omega != 0 else 1
        resistive_torque = direction * self.rolling_resistance_coeff * normal_force * self.radius
        print(resistive_torque)
        net_torque = motor_torque + resistive_torque
        return net_torque
        
    def get_drive_force(self, voltage, normal_force):
        """
        Compute the linear force exerted at the wheel's contact patch.

        :param voltage: Applied voltage to the motor.
        :param normal_force: Normal load on the wheel.
        :return: Drive force (N).
        """
        torque = self.compute_net_torque(voltage, normal_force)
        return torque / self.radius

    def angular_acceleration(self, voltage, normal_force):
        """
        Compute the wheel's angular acceleration based on the net torque.

        :param voltage: The applied voltage to the motor.
        :param normal_force: The normal force on the wheel for computing resistive torque.
        :return: The angular acceleration (rad/s^2).
        """
        net_torque = self.compute_net_torque(voltage, normal_force)
        return net_torque / self.effective_inertia    

    def update_dynamics(self, voltage, normal_force, dt):
        """
        Integrate the wheel's dynamics forward in time using Euler integration.

        :param voltage: The applied voltage to the motor.
        :param normal_force: The normal force on the wheel.
        :param dt: The time step for the integration.
        """
        # Compute angular acceleration (which includes motor and resistive effects)
        alpha = self.angular_acceleration(voltage, normal_force)
        # Integrate angular acceleration to update the angular velocity
        self.omega += alpha * dt

    def update(self, linear_velocity):
        self.omega = linear_velocity/self.radius

    def get_linear_velocity(self):
        """
        Return the linear velocity at the wheel rim derived from the current angular velocity.

        :return: The linear velocity (m/s).
        """
        return self.omega * self.radius
