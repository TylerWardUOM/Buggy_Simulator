import numpy as np
import matplotlib.pyplot as plt

# ---------------- Simulation Parameters ----------------
max_rpm = 500                      # Maximum RPM limit
initial_rpm = 0                    # Initial RPM
Kp = 1.18                           # Proportional gain for torque generation
Ki = 1.9                           # Integral gain for slower adjustment (not used in every fast loop here)
torque_constant = 0.0082              # Base torque constant (used earlier; adjust as needed)

# PID control history buffers
compensation_history = [0] * 3      
error_history = [0] * 5
history_index = 0
error_history_index = 0
persistent_error = 0

max_angle = 18                     # Maximum slope angle in degrees
gravity_constant = -9.81            # Gravitational acceleration (m/s²)
vehicle_mass = 0.7                 # Mass of the vehicle (kg)
wheel_radius = 0.0375              # Radius of the wheel (m)
wheel_mass = 0.1                   # Estimated mass of one wheel (kg)

# Moment of Inertia for a solid disk: I = 0.5 * m * r^2
I = 0.5 * wheel_mass * (wheel_radius ** 2)  # (kg·m²)

# Damping factor for gradual convergence (units: 1/s)
damping_factor = 0.5               # Adjusted for dt integration

# Time step for integration (dt in seconds)
dt = 0.01                          

# ---------------- Slope Profile Generation ----------------
uphill_ramp = np.linspace(0, max_angle, 60)      
uptoflat_ramp = np.linspace(max_angle, 0, 60)
downhill_ramp = np.linspace(0, -max_angle, 60)   
flat = np.zeros(400)                             
slope = np.concatenate([flat, uphill_ramp, np.full(400, max_angle),
                        uptoflat_ramp, flat, downhill_ramp,
                        np.full(400, -max_angle), flat])

# ---------------- Initialize State Variables ----------------
time_steps = len(slope)
# We'll track angular velocities in rad/s (omega)
# Convert initial RPM to rad/s:
actual_omega = (2 * np.pi * initial_rpm) / 60  
actual_omega_nocontrol = actual_omega
actual_rpm=initial_rpm
actual_rpm_nocontrol=initial_rpm
set_rpm = 250                     # Control system's desired RPM (fast loop)
target_rpm = 250                  # Slower target RPM from bang-bang logic
# Convert these to angular velocities:
set_omega = (2 * np.pi * set_rpm) / 60
target_omega = (2 * np.pi * target_rpm) / 60

# For storing results
rpm_values = []                   # Actual RPM (from controlled simulation)
rpm_nocontrol_values = []         # Baseline (no control) RPM
set_rpm_values = []               # Set RPM over time
target_rpm_values = []            # Target RPM over time
adjustment_values = []            # PID adjustments
persistent_compensation_values = []  # Averaged adjustments
persistent_error_values = []
normalized_slope_values = []

# For slower bang-bang control:
stay_at_120_cycles = 0            # Counter for cycles at 120 RPM

# ---------------- Main Simulation Loop ----------------
for t in range(time_steps):
    # ----- Gravity Torque Calculation -----
    # Force due to gravity: F = m * g * sin(θ)
    slope_radians = np.radians(slope[t])
    gravity_force = vehicle_mass * gravity_constant * np.sin(slope_radians)
    # Torque due to gravity: τ_g = F * r.
    gravity_torque = gravity_force * wheel_radius

    # ----- Bang-Bang Control (fast switching every 3 steps) -----
    if t % 3 == 0:
        if stay_at_120_cycles == 0:
            if np.random.rand() < 0.03:
                target_rpm = 120
                set_rpm = (120+(persistent_error*Ki))
                stay_at_120_cycles = 7  # Stay at 120 RPM for 6 cycles
            else:
                target_rpm = 250
                set_rpm = (250+(persistent_error*Ki))
        else:
            stay_at_120_cycles -= 1

    # ----- PID Control (slow adjustment every 50 steps) -----
    if t % 50 == 0:
        error = target_rpm - actual_rpm  # error in RPM
        adjustment = (error / max_rpm) * Kp
        adjustment = np.clip(adjustment, -1, 1)
        compensation_history[history_index] = adjustment
        history_index = (history_index + 1) % 3
        persistent_compensation = np.mean(compensation_history)
        error_history[error_history_index] = error
        error_history_index = (error_history_index + 1) % 5
        persistent_error = np.mean(error_history)
        set_rpm += adjustment * max_rpm
        set_rpm = np.clip(set_rpm, 0, max_rpm)

    # Update set and target angular velocities (rad/s)
    set_omega = (2 * np.pi * set_rpm) / 60
    target_omega = (2 * np.pi * target_rpm) / 60

    # ----- Motor Physics: Compute Motor Torque -----
      # Here we generate a motor torque proportional to the difference between the desired (set) angular velocity
    # and the actual angular velocity.
    angular_velocity_error = set_omega - actual_omega
    angular_velocity_error_noControl = target_omega - actual_omega_nocontrol

    motor_torque = torque_constant * angular_velocity_error  # (N·m)
    motor_torque_noControl = torque_constant * angular_velocity_error_noControl

    # Total torque applied to the wheel is the sum of motor torque and gravity torque.
    total_torque = motor_torque + gravity_torque
    total_torque_noControl = motor_torque_noControl + gravity_torque
    # ----- Compute Angular Acceleration -----
    # Newton's second law for rotation: τ = I * α  =>  α = τ / I
    angular_acceleration = total_torque / I
    angular_acceleration_noControl = total_torque_noControl / I

    # (Optional) Clamp angular acceleration to avoid runaway values:
    max_angular_acceleration = 500  # (rad/s²) - tune this as necessary
    angular_acceleration = np.clip(angular_acceleration, -max_angular_acceleration, max_angular_acceleration)
    angular_acceleration_noControl = np.clip(angular_acceleration_noControl, -max_angular_acceleration, max_angular_acceleration)
    # ----- Update Angular Velocity (Integration) -----
    # Euler integration: ω_new = ω_old + α * dt
    actual_omega += angular_acceleration * dt
    actual_omega_nocontrol +=angular_acceleration_noControl *dt
    # Apply damping (first-order response toward set_omega)
    actual_omega += damping_factor * dt * (set_omega - actual_omega)

    # For a no-control baseline, let target_omega drive the response:
    actual_omega_nocontrol += damping_factor * dt * (target_omega - actual_omega_nocontrol)

    # ----- Convert Angular Velocity Back to RPM -----
    actual_rpm = (actual_omega * 60) / (2 * np.pi)
    actual_rpm_nocontrol = (actual_omega_nocontrol * 60) / (2 * np.pi)

    # Clip RPM values to physical limits
    actual_rpm = np.clip(actual_rpm, 0, max_rpm)
    actual_rpm_nocontrol = np.clip(actual_rpm_nocontrol, 0, max_rpm)

    # ----- Normalize Slope for Plotting -----
    normalized_slope = np.clip(slope[t] * (max_rpm / max_angle), -max_rpm, max_rpm)

    # ----- Store Values for Plotting -----
    rpm_values.append(actual_rpm)
    rpm_nocontrol_values.append(actual_rpm_nocontrol)
    set_rpm_values.append(set_rpm)
    target_rpm_values.append(target_rpm)
    adjustment_values.append(adjustment * max_rpm)
    persistent_compensation_values.append(persistent_compensation * max_rpm)
    persistent_error_values.append(persistent_error)
    normalized_slope_values.append(normalized_slope)

# ---------------- Plotting ----------------
plt.figure(figsize=(10, 5))
plt.plot(rpm_values, label='Actual RPM', color='blue')
plt.plot(rpm_nocontrol_values, label='Actual RPM No Control', color='gray')
plt.plot(set_rpm_values, label='Set RPM', color='orange', linestyle='dashed')
plt.plot(target_rpm_values, label='Target RPM', color='green', linestyle='dotted')
plt.plot(adjustment_values, label='Adjustment', linestyle='dashed', color='red')
plt.plot(persistent_compensation_values, label='Persistent Compensation', linestyle='dotted', color='purple')
plt.plot(normalized_slope_values, label='Normalized Slope', linestyle='solid', color='brown', alpha=0.6)
plt.title('Simulated Buggy Speed Regulation with Hill Compensation')
plt.xlabel('Time Steps')
plt.ylabel('RPM')
plt.legend()
plt.grid(True)
plt.show()
