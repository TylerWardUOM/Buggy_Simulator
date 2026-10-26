import argparse
from typing import Callable

from simulation.Buggy.Buggy import load_buggys, select_buggy
from simulation.Simulation import ControlFunction, ErrorFunction, simulate_motion
from simulation.Track.Track import load_tracks, select_track
from control.BangBang import BangBang
from control.CalculateError import calculate_error
from control.CustomControllerExample import custom_controller, custom_error
from visulization.SimulationPlots import plot_simulation_results


CONTROLLERS: dict[str, tuple[str, ControlFunction, str]] = {
    "bang-bang": ("Bang-bang", BangBang, "default"),
    "custom-example": ("Custom example", custom_controller, "custom-example"),
}

ERROR_FUNCTIONS: dict[str, tuple[str, ErrorFunction]] = {
    "default": ("Default sensor error", calculate_error),
    "custom-example": ("Custom example error", custom_error),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run a buggy line-following simulation.")
    parser.add_argument("--buggy", help="Buggy number or name.")
    parser.add_argument("--track", help="Track number or name.")
    parser.add_argument(
        "--controller",
        help=f"Controller name ({', '.join(CONTROLLERS)}).",
    )
    parser.add_argument(
        "--error-function",
        help=f"Error function name ({', '.join(ERROR_FUNCTIONS)}).",
    )
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


def select_named_option(
    options: dict[str, tuple[str, Callable]],
    selection: str | None,
    prompt: str,
) -> str:
    if selection is not None:
        if selection in options:
            return selection
        available = ", ".join(options)
        raise ValueError(f"Unknown {prompt.lower()} '{selection}'. Choose from: {available}.")

    print(f"\nAvailable {prompt.lower()}s:")
    option_names = list(options)
    for index, option_name in enumerate(option_names, start=1):
        print(f"{index}. {options[option_name][0]} ({option_name})")

    while True:
        choice = input(f"Choose a {prompt.lower()} [1-{len(option_names)}]: ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(option_names):
                return option_names[index]
        print("Invalid selection. Please choose one of the listed numbers.")


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
    controller_name = select_named_option(CONTROLLERS, args.controller, "controller")
    default_error_name = CONTROLLERS[controller_name][2]
    error_name = (
        args.error_function
        if args.error_function is not None
        else default_error_name
    )
    error_name = select_named_option(ERROR_FUNCTIONS, error_name, "error function")
    _, controller, _ = CONTROLLERS[controller_name]
    _, error_function = ERROR_FUNCTIONS[error_name]

    if dt <= 0:
        raise ValueError("Simulation timestep must be positive.")
    if simulation_time <= 0:
        raise ValueError("Simulation duration must be positive.")
    if args.control_period <= 0:
        raise ValueError("Control period must be positive.")
    time_steps = int(simulation_time / dt)

    results = simulate_motion(
        controller,
        control_period=args.control_period,
        buggy=buggy,
        track=track,
        time_steps=time_steps,
        dt=dt,
        error_function=error_function,
    )
    plot_simulation_results(results, track)


if __name__ == "__main__":
    run_simulation(parse_args())
