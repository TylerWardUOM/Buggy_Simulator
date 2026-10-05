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

Without options, the program asks you to select a buggy profile and track,
then asks for the simulation timestep and duration. You can also provide
these values on startup:

```bash
python3 main.py --buggy 1 --track 3 --dt 0.001 --duration 10
```

The available options are:

```text
--buggy           Buggy number or name
--track           Track number or name
--dt              Simulation timestep in seconds
--duration        Simulation duration in seconds
--control-period  Controller update period in seconds (default: 0.01)
```

The program runs the simulation and displays diagnostic plots followed by the
buggy trajectory over the track.

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

## Custom controllers and sensor errors

`simulate_motion` accepts a controller function with this interface:

```python
def controller(state):
    return left_duty, right_duty
```

The controller receives a `state` object. These are the available fields:

```python
state.sensor_values          # Line-sensor readings
state.sensor_positions_local # Sensor positions relative to the buggy
state.previous_left_duty     # Previous left motor duty cycle
state.previous_right_duty    # Previous right motor duty cycle
state.previous_error         # Error from the previous controller update
state.left_wheel_speed       # Left wheel speed in RPM
state.right_wheel_speed      # Right wheel speed in RPM
state.battery_voltage        # Current simulated battery voltage
state.slope_angle            # Track slope angle in degrees
state.dt                     # Simulation timestep in seconds
state.current_time           # Current simulation time in seconds
```

`slope_angle` is available from the simulator's track model, but a real buggy
may not be able to measure it directly. Use it in a controller only if the
real buggy has a suitable inclinometer/IMU or another way to estimate slope.

The simulator also accepts an `error_function` for calculating the error shown
in the results:

```python
def error_function(sensor_values):
    return signed_error
```

For example:

```python
from control.CustomControllerExample import custom_controller, custom_error

results = simulate_motion(
    control_func=custom_controller,
    control_period=0.01,
    buggy=buggy,
    track=track,
    time_steps=10000,
    dt=0.001,
    error_function=custom_error,
)
```

The existing `BangBang` controller and `calculate_error` function remain the
defaults. A custom controller may calculate its own error internally; pass
the same error function to `simulate_motion` if you also want that error
recorded in the plots and results.

## Two types of tests

**Buggy characterization tests** measure a real buggy's behaviour, such as
motor speed, acceleration, battery voltage, and turning response. Their
results are used to tune a profile in `buggy_profiles.json`.

**Simulator verification tests** check that the Python implementation behaves
correctly. These cover the motor, wheel, battery, track, sensors, controllers,
and short end-to-end simulations. They do not classify a real buggy.

## Pending hardware clarification

The motor-drive model currently assumes forward, average-voltage control. After
confirming how the real buggies' H-bridges operate, add explicit unipolar or
bipolar drive modes, command-range validation, and the correct coast/brake
behaviour to the motor-drive model.

The battery model currently includes only nominal voltage and short-term
voltage sag from internal resistance. Add battery capacity, state-of-charge
tracking, current limits, and any required low-voltage cutoff behaviour later,
once battery measurements are available. And any other key battery simulations.

## Future hardware-realism additions

The following features should be added after characterization tests provide
real buggy parameters and failure rates:

1. **Unequal left/right wheel and motor performance**
   Model differences in motor constants, gearbox efficiency, friction,
   current limits, and wheel radius.
2. **Sensor noise and dropout**
   Add per-sensor noise, bias, gain differences, saturation, response delay,
   and temporary loss of readings.
3. **Motor-command variation**
   Model duty-cycle deadband, command delay, PWM variation, and differences
   between requested and delivered motor power.
4. **Wheel slip**
   Limit drive force using available grip so that wheels can spin faster than
   the buggy moves during acceleration, braking, turning, or low-grip
   conditions.
5. **Encoder model and errors**
   Implement encoder quantisation, missed pulses, timing jitter, delayed
   readings, and intermittent failure.
6. **Random disturbances and hardware faults**
   Support reproducible random disturbances such as changing friction,
   temporary motor power reduction, sensor failure, encoder dropout, and
   mechanical drag changes.

These behaviours should be configurable and use an optional random seed so
that realistic variable runs can be reproduced during testing. And any other key battery simulations.

## Future track representations

The current tracks are represented as measured points joined by straight
segments. This should remain available for reproducing tape-based tracks,
including sharp or uneven corners.

Add an optional smoothed-track mode in the future, using a spline or Bézier
representation for comparison with the measured polyline. Smoothing must be
configurable and should not replace the measured track by default, because it
can change corner geometry, track length, and slope behaviour. And any other key battery simulations.
