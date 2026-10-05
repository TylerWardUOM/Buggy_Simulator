from simulation.Buggy.Buggy import load_buggys, select_buggy
from simulation.Simulation import simulate_motion
from simulation.Track.Track import load_tracks, select_track
from control.BangBang import BangBang
from visulization.SimulationPlots import plot_simulation_results


def run_interactive():
    buggys = load_buggys("buggy_profiles.json")
    buggy = select_buggy(buggys)
    tracks = load_tracks("track.json")
    track = select_track(tracks)

    dt = float(input("Enter Simulation Timestep (s): "))
    simulation_time = float(input("Enter Simulation Duration: "))
    if dt <= 0:
        raise ValueError("Simulation timestep must be positive.")
    if simulation_time <= 0:
        raise ValueError("Simulation duration must be positive.")
    time_steps = int(simulation_time / dt)

    results = simulate_motion(
        BangBang,
        control_period=0.01,
        buggy=buggy,
        track=track,
        time_steps=time_steps,
        dt=dt,
    )
    plot_simulation_results(results, track)


if __name__ == "__main__":
    run_interactive()
