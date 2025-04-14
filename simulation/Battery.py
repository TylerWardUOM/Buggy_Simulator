class Battery:
    def __init__(self,V_nominal,R_internal):
        self.V_nominal = V_nominal
        self.R_internal = R_internal
        self.voltage = V_nominal

    def update(self,currentDraw):
        self.voltage = self.V_nominal-(currentDraw*self.R_internal)

    def get_voltage(self):
        return self.voltage
    
    #Add Battery Capcity in Future