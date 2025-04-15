from typing import TypedDict, List, Tuple
import numpy as np
from .Buggy.Buggy import Buggy
from .Track.Track import Track
from control.CalculateError import calculate_error

class SimulationResult(TypedDict):
    orientation_log: List[float]
    left_omega: List[float]
    right_omega: List[float]
    left_duty: List[float]
    right_duty: List[float]
    slope_angles: List[float]
    position_log: List[List[float]]  # assuming each position is a [x, y]
    sensor_values: List[List[float]]
    sensor_positions: List[List[Tuple[float, float]]]
    time_steps: int
    error_values: List[float]


def simulate_motion(control_func, buggy: Buggy, track: Track, time_steps=10000, dt=0.001) -> SimulationResult:

    result = {
        "orientation_log": [],
        "left_omega": [],
        "right_omega": [],
        "left_duty": [],
        "right_duty": [],
        "slope_angles": [],
        "position_log": [],
        "sensor_values": [],
        "sensor_positions": [],
        "time_steps": time_steps,
        "error_values": [],
    }
    
    lost_count = 0
    
    for t in range(time_steps):
        sensor_value = buggy.sensor_array.get_readings(buggy.position, buggy.orientation, track)

        if t % 10 == 0:
            duty_left, duty_right = control_func(sensor_value, buggy.motor_drive_board.duty_left, buggy.motor_drive_board.duty_right)
            buggy.set_duty(duty_left, duty_right)

        slope_angle = track.get_slope_angle_at_position(buggy.position.copy())
        cur_sensor_positions = buggy.sensor_array.get_positions(buggy.position, buggy.orientation)

        # Store values in the result dict
        result["left_duty"].append(duty_left)
        result["right_duty"].append(duty_right)
        result["slope_angles"].append(slope_angle)
        result["sensor_values"].append(sensor_value)
        result["error_values"].append(calculate_error(sensor_value))
        result["sensor_positions"].append(cur_sensor_positions)
        result["position_log"].append(buggy.position.copy())
        result["orientation_log"].append(np.rad2deg(buggy.orientation))

        buggy.set_duty(duty_left, duty_right)
        buggy.update(slope_angle, dt)

        left_rpm = max((buggy.left_wheel.omega / (2 * np.pi)) * 60, 0)
        right_rpm = max((buggy.right_wheel.omega / (2 * np.pi)) * 60, 0)
        result["left_omega"].append(left_rpm)
        result["right_omega"].append(right_rpm)
        result["time_steps"] = t+1

        if sum(sensor_value) < 0.0001:
            lost_count += 1
            if lost_count >= time_steps * 0.1:
                break

    return result

