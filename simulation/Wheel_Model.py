class Wheel:
    def __init__(self, motor, gearbox, radius, inertia):
        self.motor = motor
        self.gearbox = gearbox
        self.radius = radius
        self.inertia = inertia
        self.total_inertia = inertia + self.gearbox.inertia + self.motor.inertia
        self.omega = 0.0

    def get_torque(self, voltage):
        motor_omega = self.gearbox.input_speed_from_output(self.omega)
        motor_torque = self.motor.get_torque(voltage, motor_omega)
        return self.gearbox.output_torque(motor_torque)
    
    def get_force(self, voltage, F_gravity):
        torque = self.get_torque(voltage, F_gravity)
        return torque / self.radius
    
    def angular_acceleration(self, voltage, F_gravity):
        torque = self.get_torque(voltage, F_gravity)
        if self.total_inertia == 0: 
            return torque / 0.0001
        return torque / self.total_inertia    
    
    def update(self, voltage, F_gravity, dt):
        delta_omega = self.angular_acceleration(voltage, F_gravity) * dt
        self.omega += delta_omega

    def get_velocity(self):
        # Returns the linear velocity at the wheel's radius
        return self.omega * self.radius
