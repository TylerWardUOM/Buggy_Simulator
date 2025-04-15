from simulation.Buggy.Buggy import Buggy
from .CalculateError import calculate_error
def BangBang(sensor_values,prev_left,prev_right):
    error=calculate_error(sensor_values)
    if error == 9:
        duty_left=prev_left
        duty_right=prev_right
    elif error>0:
        duty_left = 0.5
        duty_right = 0.7
        #print(sensor_values,"fast R")
    elif error<0:
        duty_left = 0.7
        duty_right = 0.5
        #print(sensor_values, "fast L")
    else:
        duty_left = 0.7
        duty_right = 0.7
    return (duty_left,duty_right)