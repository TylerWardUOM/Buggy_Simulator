import argparse

from simulation.Buggy.Buggy import load_buggys, select_buggy
from simulation.Simulation import simulate_motion
from simulation.Track.Track import load_tracks, select_track
from control.BangBang import BangBang
from control.CalculateError import calculate_error
from visulization.SimulationPlots import plot_simulation_results


def parse_args():
    parser = argparse.ArgumentParser(description="Run a buggy line-following simulation.")
    parser.add_argument("--buggy", help="Buggy number or name.")
    parser.add_argument("--track", help="Track number or name.")
    parser.add_argument("--dt", type=float, help="Simulation timestep in seconds.")
    parser.add_argument("--duration", type=float, help="Simulation duration in seconds.")
    parser.add_argument("--control-period", type=float, default=0.01)
    return parser.parse_args()


def select_by_value(items, selection, selector):
    if selection is None:
        return selector(items)
    if selection.isdigit():
        index = int(selection) - 1
        if 0 <= index < len(items):
            return items[index][1] if isinstance(items[index], tuple) else items[index]
    for item in items:
        value = item[0] if isinstance(item, tuple) else item.name
        if value.lower() == selection.lower():
            return item[1] if isinstance(item, tuple) else item
    raise ValueError(f"Unknown selection: {selection}")


def run_simulation(args):
    buggys = load_buggys("buggy_profiles.json")
    buggy = select_by_value(buggys, args.buggy, select_buggy)
    tracks = load_tracks("track.json")
    track = select_by_value(tracks, args.track, select_track)

    dt = args.dt if args.dt is not None else float(input("Enter Simulation Timestep (s): "))
    simulation_time = (
        args.duration
        if args.duration is not None
        else float(input("Enter Simulation Duration: "))
    )
    if dt <= 0:
        raise ValueError("Simulation timestep must be positive.")
    if simulation_time <= 0:
        raise ValueError("Simulation duration must be positive.")
    if args.control_period <= 0:
        raise ValueError("Control period must be positive.")
    time_steps = int(simulation_time / dt)

    results = simulate_motion(
        BangBang,
        control_period=args.control_period,
        buggy=buggy,
        track=track,
        time_steps=time_steps,
        dt=dt,
        error_function=calculate_error,
    )
    plot_simulation_results(results, track)


if __name__ == "__main__":
    run_simulation(parse_args())
