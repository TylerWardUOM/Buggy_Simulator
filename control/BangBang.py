from simulation.Simulation import ControllerState
from .CalculateError import calculate_error


def BangBang(state: ControllerState) -> tuple[float, float]:
    """Run bang-bang control using the default sensor error calculation."""
    error = calculate_error(state.sensor_values)
    if error == 9:
        duty_left = state.previous_left_duty
        duty_right = state.previous_right_duty
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