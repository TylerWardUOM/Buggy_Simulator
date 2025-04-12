#Torque=Kt*I=torque_constant*I
#Back emf = Ke*Omega = emf_constant * omega
#Voltage = Back_emf + I * armature_resistance + brush_voltage
#Torque = (torque_constant/armature_resistance)*((Voltage-brush_voltage)-emf_constant*Omega)

class Motor:
    def __init__(self,armature_resistance,brush_voltage,torque_constant,emf_constant, max_current, inertia):
        self.armature_resistance = armature_resistance
        self.brush_voltage = brush_voltage
        self.torque_constant = torque_constant
        self.emf_constant = emf_constant
        self.max_current = max_current
        self.inertia = inertia

    def calculate_back_emf(self,omega):
        return self.emf_constant*omega
    
    def calculate_current(self, voltage, omega):
        effective_voltage = (voltage - self.brush_voltage) - self.emf_constant * omega
        current = effective_voltage / self.armature_resistance
        #print(effective_voltage,omega,current)
        current = max(min(current, self.max_current), -self.max_current)
        return current

    def get_torque(self, voltage, omega):
        current = self.calculate_current(voltage, omega)
        return self.torque_constant * current