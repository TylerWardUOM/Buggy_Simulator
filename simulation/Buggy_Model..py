
#left and right motor constans used to calculate wheel output speed based on input
#Motor_bias power bias between motors

#buggy model stores parameters from tests that relate to buggy characteristics
#calls functions to simulate effects or physics uses this undecided
class Buggy_Model:
    def __init__(self, left_motor_constant, right_motor_constant):
        self.left_motor_constant = left_motor_constant
        self.rigt