class Wheel:
    def __init__(self, motor, gearbox, radius, inertia):
        self.motor = motor
        self.gearbox = gearbox
        self.radius = radius
        self.inertia = inertia
        # Total inertia includes contributions from wheel, gearbox, and motor
        self.total_inertia = inertia + self.gearbox.inertia + self.motor.inertia
        self.effective_inertia = self.total_inertia if self.total_inertia != 0 else 1e-4
        self.omega = 0.0  # Angular velocity (rad/s)
        # Rolling resistance coefficient (tunable parameter)


    def reset(self):
        self.omega=0.0
    def get_torque(self, voltage):
        """
        Calculate the output torque at the wheel.
        The motor's torque is adjusted by the gearbox.
        """
        # Convert the wheel's angular speed to the motor side input
        motor_omega = self.gearbox.input_speed_from_output(self.omega)
        motor_torque = self.motor.get_torque(voltage, motor_omega)
        # Convert motor torque to output torque using the gearbox's ratio/effects
        return self.gearbox.output_torque(motor_torque)
    
    def get_force(self, voltage):
        """
        Compute the linear force at the wheel's circumference.
        """
        torque = self.get_torque(voltage)
        return torque / self.radius
    
    def angular_acceleration(self, voltage):
        """
        Compute the angular acceleration from the motor's torque.
        Uses a small epsilon to avoid division by zero in case total_inertia is zero.
        """
        torque = self.get_torque(voltage)
        return torque / self.effective_inertia    
    
    def calculate_net_angular_acceleration(self,voltage,normal_force):
        # Motor-induced angular acceleration:
        motor_alpha = self.angular_acceleration(voltage)
        
        # Rolling resistance torque (acts opposite to the direction of rotation)
        T_resistive = -normal_force * self.radius
        resistive_alpha = T_resistive / self.effective_inertia

        # Net angular acceleration (motor + resistive)
        net_alpha = motor_alpha + resistive_alpha
        return net_alpha
    
    def calculate_net_force(self,voltage,normal_force):
        T_motor = self.get_torque(voltage)
        T_resistive = -normal_force * self.radius
        T_net = T_motor+T_resistive
        return T_net/self.radius

    
    def update(self, linear_velocity):
        # Update the angular velocity:
        self.omega = (linear_velocity/self.radius)
        

    def get_velocity(self):
        """
        Return the linear velocity at the wheel rim based on its angular velocity.
        """
        return self.omega * self.radius