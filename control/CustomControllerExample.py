"""Example extension points for custom sensor errors and controllers."""

from typing import Sequence

from simulation.Simulation import ControllerState


def custom_error(sensor_values: Sequence[float]) -> float:
    """Return a signed line-position error for a left-to-right sensor array."""
    midpoint = (len(sensor_values) - 1) / 2
    weights = [index - midpoint for index in range(len(sensor_values))]
    total = sum(sensor_values)
    if total == 0:
        return 0.0
    return sum(value * weight for value, weight in zip(sensor_values, weights)) / total


def custom_controller(
    state: ControllerState,
) -> tuple[float, float]:
    """Return left and right motor duty cycles from sensor readings."""
    error = custom_error(state.sensor_values)
    base_duty = 0.6
    correction = 0.2 * error
    return base_duty - correction, base_duty + correction
