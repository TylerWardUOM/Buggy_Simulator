class Battery:
    def __init__(self,V_nominal,R_internal):
        if V_nominal <= 0:
            raise ValueError("Nominal battery voltage must be positive.")
        if R_internal < 0:
            raise ValueError("Battery internal resistance cannot be negative.")
        self.V_nominal = V_nominal
        self.R_internal = R_internal
        self.voltage = V_nominal

    def update(self,currentDraw):
        self.voltage = self.V_nominal-(currentDraw*self.R_internal)

    def get_voltage(self):
        return self.voltage

    def reset(self):
        self.voltage = self.V_nominal
    
    #Add Battery Capcity in Future