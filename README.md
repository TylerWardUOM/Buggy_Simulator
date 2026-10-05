# Line-Following Buggy Simulator

This project is a Python simulator for testing line-following buggy designs.
It models a differential-drive buggy, motors, gearboxes, wheels, battery,
track elevation, line sensors, and a controller.

## Installation

Install the Python dependencies:

```bash
python3 -m pip install numpy matplotlib tqdm
```

## Running a simulation

From the repository root:

```bash
python3 main.py
```

The program asks you to select a buggy profile and track, then asks for the
simulation timestep and duration. It runs the simulation and displays
diagnostic plots followed by the buggy trajectory over the track.

Buggy profiles are stored in [`buggy_profiles.json`](./buggy_profiles.json)
and tracks are stored in [`track.json`](./track.json). The profile editor can
be started with:

```bash
python3 visulization/buggy_gui.py
```

## Project structure

```text
simulation/       Physics, buggy, wheel, power, sensor, and track models
control/          Line-following controllers
visulization/     Simulation and track plots plus the profile editor
tests/            Characterization and simulator verification tests
main.py           Interactive entry point
buggy_profiles.json
track.json
```

The simulation engine is callable without the interactive interface through
`simulation.Simulation.simulate_motion`. This allows controllers and tests to
run repeatable simulations directly from Python.

## Two types of tests

**Buggy characterization tests** measure a real buggy's behaviour, such as
motor speed, acceleration, battery voltage, and turning response. Their
results are used to tune a profile in `buggy_profiles.json`.

**Simulator verification tests** check that the Python implementation behaves
correctly. These cover the motor, wheel, battery, track, sensors, controllers,
and short end-to-end simulations. They do not classify a real buggy.
