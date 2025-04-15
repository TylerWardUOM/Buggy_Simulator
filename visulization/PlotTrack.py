import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider
import numpy as np
from simulation.Track.Track import Track

def plot_track(track: Track, show_elevation: bool = False):
    """
    Plots the track using matplotlib.

    :param track: A Track object.
    :param show_elevation: If True, color the line by elevation.
    """
    points = track.path_points
    x, y = points[:, 0], points[:, 1]

    plt.figure(figsize=(8, 6))

    if show_elevation and points.shape[1] >= 3:
        # Build segments from consecutive points
        segments = np.array([[[x[i], y[i]], [x[i + 1], y[i + 1]]] for i in range(len(x) - 1)])
        z = points[:, 2]
        z_avg = (z[:-1] + z[1:]) / 2  # average elevation per segment

        lc = LineCollection(segments, cmap='viridis', array=z_avg, linewidths=2)
        plt.gca().add_collection(lc)
        plt.colorbar(lc, label='Elevation (m)')
    else:
        plt.plot(x, y, 'b-', linewidth=2, label='Track Path')
        plt.scatter(x, y, color='red', s=10)

    plt.title(f"Track: {track.name}")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_track_with_buggy(track: Track, buggy_positions, show_elevation: bool = False):
    """
    Plots the track and overlays the buggy's position over time.

    :param track: A Track object.
    :param buggy_positions: List or np.ndarray of buggy positions over time, shape (N, 2) or (N, 3).
    :param show_elevation: If True, color the track by elevation.
    """
    track_points = track.path_points
    x, y = track_points[:, 0], track_points[:, 1]

    plt.figure(figsize=(10, 8))

    # Plot the track
    if show_elevation and track_points.shape[1] >= 3:
        segments = np.array([[[x[i], y[i]], [x[i + 1], y[i + 1]]] for i in range(len(x) - 1)])
        z = track_points[:, 2]
        z_avg = (z[:-1] + z[1:]) / 2
        lc = LineCollection(segments, cmap='viridis', array=z_avg, linewidths=2)
        plt.gca().add_collection(lc)
        plt.colorbar(lc, label='Elevation (m)')
    else:
        plt.plot(x, y, 'b-', linewidth=2, label='Track Path')

    # Plot buggy positions
    buggy_positions = np.array(buggy_positions)
    plt.plot(buggy_positions[:, 0], buggy_positions[:, 1], 'r.-', label='Buggy Path')
    plt.scatter(buggy_positions[0, 0], buggy_positions[0, 1], color='green', s=50, label='Start')
    plt.scatter(buggy_positions[-1, 0], buggy_positions[-1, 1], color='black', s=50, label='End')

    plt.title(f"Track with Buggy Trajectory: {track.name}")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_track_with_buggy_animated(track: Track, buggy_positions, show_elevation: bool = False, interval: int = 100):
    buggy_positions = np.array(buggy_positions)
    track_points = track.path_points
    x, y = track_points[:, 0], track_points[:, 1]

    fig, ax = plt.subplots(figsize=(10, 8))
    plt.subplots_adjust(bottom=0.25)  # leave space for controls

    # Plot track
    if show_elevation and track_points.shape[1] >= 3:
        segments = np.array([[[x[i], y[i]], [x[i + 1], y[i + 1]]] for i in range(len(x) - 1)])
        z = track_points[:, 2]
        z_avg = (z[:-1] + z[1:]) / 2
        lc = LineCollection(segments, cmap='viridis', array=z_avg, linewidths=2)
        ax.add_collection(lc)
        plt.colorbar(lc, ax=ax, label='Elevation (m)')
    else:
        ax.plot(x, y, 'b-', linewidth=2, label='Track Path')

    # Setup elements
    path_line, = ax.plot([], [], 'r.-', label='Buggy Path')
    buggy_dot, = ax.plot([], [], 'ko', markersize=8, label='Buggy')

    # Start/End points
    ax.scatter(buggy_positions[0, 0], buggy_positions[0, 1], color='green', s=50, label='Start')
    ax.scatter(buggy_positions[-1, 0], buggy_positions[-1, 1], color='black', s=50, label='End')

    ax.set_title(f"Track with Buggy Animation: {track.name}")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.axis('equal')
    ax.grid(True)
    ax.legend()

    # Animation logic
    frame = [0]
    playing = [False]

    def init():
        path_line.set_data([], [])
        buggy_dot.set_data([], [])
        return path_line, buggy_dot


    # --- Controls (buttons/sliders) ---
    ax_play = plt.axes([0.1, 0.1, 0.1, 0.075])
    ax_reset = plt.axes([0.22, 0.1, 0.1, 0.075])
    ax_speed = plt.axes([0.5, 0.1, 0.4, 0.03])

    btn_play = Button(ax_play, 'Play')
    btn_reset = Button(ax_reset, 'Reset')
    slider_speed = Slider(ax_speed, 'Speed', 0.5, 20.0, valinit=1.0)
    
    def update(_):
        if playing[0]:
            current_speed = slider_speed.val  # Always pull from the slider directly
            frame[0] = (frame[0] + int(current_speed)) % len(buggy_positions)
            path_line.set_data(buggy_positions[:frame[0]+1, 0], buggy_positions[:frame[0]+1, 1])
            buggy_dot.set_data(buggy_positions[frame[0], 0], buggy_positions[frame[0], 1])
        return path_line, buggy_dot
    
    ani = FuncAnimation(fig, update, init_func=init, interval=interval, blit=False)

    def toggle_play(event):
        playing[0] = not playing[0]
        btn_play.label.set_text("Pause" if playing[0] else "Play")
            

    def reset_animation(event):
        frame[0] = 0
        path_line.set_data([], [])
        buggy_dot.set_data([], [])

    def update_speed(val):
        pass

    btn_play.on_clicked(toggle_play)
    btn_reset.on_clicked(reset_animation)
    slider_speed.on_changed(update_speed)

    plt.tight_layout()
    plt.show()