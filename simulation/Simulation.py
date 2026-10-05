from dataclasses import dataclass
from typing import Callable, List, Sequence, Tuple, TypedDict
from tqdm import trange
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
    dt: float


ErrorFunction = Callable[[Sequence[float]], float]
@dataclass(frozen=True)
class ControllerState:
    """Measurements and state available to a controller at one control step."""

    sensor_values: Sequence[float]
    sensor_positions_local: Sequence[Tuple[float, float]]
    previous_left_duty: float
    previous_right_duty: float
    previous_error: float
    left_wheel_speed: float
    right_wheel_speed: float
    battery_voltage: float
    slope_angle: float
    dt: float
    current_time: float


ControlFunction = Callable[[ControllerState], Tuple[float, float]]


def simulate_motion(
    control_func: ControlFunction,
    control_period: float,
    buggy: Buggy,
    track: Track,
    time_steps: int = 10000,
    dt: float = 0.001,
    error_function: ErrorFunction = calculate_error,
) -> SimulationResult:
    if dt <= 0:
        raise ValueError("Simulation timestep must be positive.")
    if control_period <= 0:
        raise ValueError("Control period must be positive.")
    if time_steps <= 0:
        raise ValueError("Simulation must contain at least one timestep.")

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
        "dt": dt,
    }
    lost_count = 0
    duty_left = buggy.motor_drive_board.duty_left
    duty_right = buggy.motor_drive_board.duty_right
    previous_error = 0.0
    time_since_control = control_period
    
    for t in trange(time_steps, desc="Simulating"):
        sensor_value = buggy.sensor_array.get_readings(buggy.position, buggy.orientation, track)
        slope_angle = track.get_slope_angle_at_position(buggy.position.copy())
        cur_sensor_positions = buggy.sensor_array.get_positions(buggy.position, buggy.orientation)
        sensor_positions_local = buggy.sensor_array.sensor_positions_local
        current_error = error_function(sensor_value)

        if time_since_control >= control_period:
            left_rpm = (buggy.left_wheel.omega / (2 * np.pi)) * 60
            right_rpm = (buggy.right_wheel.omega / (2 * np.pi)) * 60
            state = ControllerState(
                sensor_values=sensor_value,
                sensor_positions_local=sensor_positions_local,
                previous_left_duty=buggy.motor_drive_board.duty_left,
                previous_right_duty=buggy.motor_drive_board.duty_right,
                previous_error=previous_error,
                left_wheel_speed=left_rpm,
                right_wheel_speed=right_rpm,
                battery_voltage=buggy.battery.get_voltage(),
                # This is available from the simulated track, but may not be
                # directly measurable by a real buggy without extra sensors.
                slope_angle=slope_angle,
                dt=dt,
                current_time=t * dt,
            )
            duty_left, duty_right = control_func(state)
            buggy.set_duty(duty_left, duty_right)
            previous_error = current_error
            time_since_control = 0.0

        # Store values in the result dict
        result["left_duty"].append(duty_left)
        result["right_duty"].append(duty_right)
        result["slope_angles"].append(slope_angle)
        result["sensor_values"].append(sensor_value)
        result["error_values"].append(current_error)
        result["sensor_positions"].append(cur_sensor_positions)
        result["position_log"].append(buggy.position.copy())
        result["orientation_log"].append(np.rad2deg(buggy.orientation))

        buggy.set_duty(duty_left, duty_right)
        buggy.update(slope_angle, dt)
        time_since_control += dt

        left_rpm = max((buggy.left_wheel.omega / (2 * np.pi)) * 60, 0)
        right_rpm = max((buggy.right_wheel.omega / (2 * np.pi)) * 60, 0)
        result["left_omega"].append(left_rpm)
        result["right_omega"].append(right_rpm)
        result["time_steps"] = t+1

        if sum(sensor_value) < 0.0001:
            lost_count += 1
            if lost_count >= time_steps * 0.1:
                sim_time = (t + 1) * dt
                sim_percent = 100 * (t + 1) / time_steps
                print(f"\n⚠️ Simulation ended early at {sim_percent:.1f}% ({sim_time:.2f} seconds simulated) due to line loss.")
                break

    return result
