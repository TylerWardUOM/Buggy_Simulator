class MotorDriveBoard:
    def __init__(self):
        self.duty_left = 0.0
        self.duty_right = 0.0

    def set_duty_left(self,duty):
        self.duty_left = duty

    def set_duty_right(self,duty):
        self.duty_right = duty

    def get_voltage_left(self,battery):
        return self.duty_left*battery.get_voltage()
    
    def get_voltage_right(self,battery):
        return self.duty_right*battery.get_voltage()