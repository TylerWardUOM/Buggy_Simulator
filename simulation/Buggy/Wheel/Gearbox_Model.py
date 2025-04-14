class Gearbox:
    def __init__(self, gear_ratio, inertia, efficiency=0.85):
        self.gear_ratio = gear_ratio
        self.efficiency = efficiency
        self.inertia = inertia

    def output_torque(self, input_torque):
        return input_torque * self.gear_ratio * self.efficiency

    def output_speed(self, input_speed):
        return input_speed * (1/self.gear_ratio)

    def input_speed_from_output(self, output_speed):
        return output_speed * self.gear_ratio

    def input_torque_from_output_torque(self, output_torque):
        return output_torque / (self.gear_ratio / self.efficiency)
