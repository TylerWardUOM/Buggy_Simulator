import random

import matplotlib.pyplot as plt
import numpy as np

from .PlotTrack import plot_track_with_buggy


def plot_simulation_results(results, track):
    """Display the diagnostic plots produced by a simulation run."""
    left_omega = results["left_omega"]
    right_omega = results["right_omega"]
    position_log = results["position_log"]
    sensor_values = results["sensor_values"]
    sensor_positions = results["sensor_positions"]
    dt = results["dt"]

    if not sensor_values:
        raise ValueError("Cannot plot a simulation with no sensor readings.")

    time = np.arange(len(left_omega)) * dt
    average_wheel_speed = [
        (left + right) / 2 for left, right in zip(left_omega, right_omega)
    ]
    sensor_series = list(zip(*sensor_values))
    sensor_position_series = list(zip(*sensor_positions))
    buggy_positions = np.asarray(position_log)

    fig, axs = plt.subplots(5, 1, figsize=(10, 8))
    for i, series in enumerate(sensor_position_series):
        positions = np.asarray(series)
        color = (random.random(), random.random(), random.random())
        axs[0].plot(positions[:, 0], positions[:, 1], label=f"Sensor {i + 1}", color=color)

    marker_interval = max(1, int(0.5 / dt))
    for i in range(0, len(buggy_positions), marker_interval):
        axs[0].annotate(
            f"{i * dt:.1f}s",
            buggy_positions[i],
            textcoords="offset points",
            xytext=(5, 5),
            ha="left",
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.5),
        )
    axs[0].set_title("Differential Drive Vehicle Motion")
    axs[0].set_xlabel("X Position (meters)")
    axs[0].set_ylabel("Y Position (meters)")
    axs[0].grid(True)
    axs[0].legend()

    axs[1].plot(time, left_omega, label="Left Wheel ω", color="b")
    axs[1].plot(time, right_omega, label="Right Wheel ω", color="r")
    axs[1].plot(time, average_wheel_speed, label="Average Wheel ω", color="g")
    axs[1].set_title("Wheel Angular Velocities Over Time")
    axs[1].set_xlabel("Time (seconds)")
    axs[1].set_ylabel("Angular Velocity (RPM)")
    axs[1].grid(True)
    axs[1].legend()

    axs[2].plot(time, results["slope_angles"], label="Slope Angle", color="g")
    axs[2].set_title("Slope Angle Over Time")
    axs[2].set_xlabel("Time (seconds)")
    axs[2].set_ylabel("Slope Angle (degrees)")
    axs[2].grid(True)
    axs[2].legend()

    axs[3].plot(time, results["left_duty"], label="Left", color="b")
    axs[3].plot(time, results["right_duty"], label="Right", color="r")
    axs[3].set_title("Motor Duty Cycles Over Time")
    axs[3].set_xlabel("Time (seconds)")
    axs[3].set_ylabel("Duty cycle")
    axs[3].grid(True)
    axs[3].legend()

    for i, series in enumerate(sensor_series):
        color = (random.random(), random.random(), random.random())
        axs[4].plot(time, series, label=f"Sensor {i + 1}", color=color)
    axs[4].plot(time, results["error_values"], label="Error", color="g")
    axs[4].set_title("Sensor Readings Over Time")
    axs[4].set_xlabel("Time (seconds)")
    axs[4].set_ylabel("Sensor intensity")
    axs[4].grid(True)
    axs[4].legend()

    fig.tight_layout()
    plot_track_with_buggy(track, position_log, True)
    return fig
