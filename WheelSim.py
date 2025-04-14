import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
max_rpm = 500
initial_rpm = 0
Kp = 0.50  # Proportional constant for the PID controller
Ki = 0.75
compensation_history = [0] * 3  # Buffer for persistent compensation
error_history = [0] * 3
history_index = 0
error_history_index=0
compensation_decay = 0.9  # Decay factor for hill compensation
compensation_weight = 0.5  # Factor for weighting recent adjustments
max_angle = 18  # Maximum slope angle in degrees (for uphill and downhill)

# Generate slope profile
uphill_ramp = np.linspace(0, max_angle, 60)    # Ramp up to 18° (Uphill)
uptoflat_ramp = np.linspace(max_angle, 0, 60)
downhill_ramp = np.linspace(0, -max_angle, 60)  # Ramp down to -18° (Downhill)
flat = np.zeros(400)  # Flat section (0°)

# Full slope profile: ramp up, stay at 18°, flat, ramp down, stay at -18°, flat, repeat
slope = np.concatenate([
    flat,
    uphill_ramp,                # Uphill ramp
    np.full(400, max_angle),     # Uphill flat at 18°
    uptoflat_ramp,
    flat,                       # Flat section (0°)
    downhill_ramp,              # Downhill ramp to -18°
    np.full(400, -max_angle),    # Downhill flat at -18°
    flat                        # Flat section (0°)
])

# Store results
time_steps = len(slope)
rpm_values = []
rpm_nocontrol_values = []
set_rpm_values = []
target_rpm_values = []
adjustment_values = []
persistent_compensation_values = []
persistent_compensation=0
persistent_error_values=[]
persistent_error=0
normalized_slope_values = []  
actual_rpm = initial_rpm
actual_rpm_nocontrol=initial_rpm
set_rpm = 250  # The control system's output RPM
target_rpm = 250  # Target RPM (the system aims for this RPM)
adjustment = 0
c = 0
stay_at_120_cycles = 0  # Counter to track the cycles at 120 RPM
inertia_factor = 0.5  # Damping factor to simulate inertia
torque_constant = 0.1  # This determines how much torque influences RPM change

# Main simulation loop
for t in range(time_steps):
 # Simulate the effect of the hill (slope) on the actual RPM with a scaling factor
    if slope[t] > 0:  # Uphill (positive slope)
        gravity_factor = -6 * slope[t]  # Decelerate uphill
    else:  # Downhill (negative slope)
        gravity_factor = 6 * abs(slope[t])  # Accelerate downhill

    # Apply gravity effect to simulate a change in the RPM due to the hill
    actual_rpm += gravity_factor  # Gravity influences the actual RPM
    actual_rpm_nocontrol += gravity_factor  # Apply gravity effect for no-control RPM


    # Bang-bang control logic (every 10 loops)
    if t % 3 == 0:  # Every 10 time steps
        if stay_at_120_cycles == 0:
            # Randomly decide to go to 120 RPM
            if np.random.rand() < 0.05:  # 50% chance to switch to 120 RPM
                target_rpm = 120
                set_rpm = 120 + (persistent_error*Ki)
                stay_at_120_cycles = 6  # Stay at 120 RPM for 3 cycles
            else:
                target_rpm = 250
                set_rpm = 250 + (persistent_error*Ki)
        else:
            stay_at_120_cycles -= 1  # Decrement cycle counter when at 120 RPM

    # Every 100 loops, update the speed adjustment logic (PID)
    if t % 50 == 0:
        # Reset adjustment logic for long-term control (e.g., reduce oscillations)
        error = target_rpm - actual_rpm
        adjustment = (error / max_rpm) * Kp
        adjustment = np.clip(adjustment, -1, 1)
        # Store the adjustment in the history buffer (circular buffer style)
        compensation_history[history_index] = adjustment
        history_index = (history_index + 1) % 3
        persistent_compensation = np.mean(compensation_history)
        error_history[error_history_index] = error
        error_history_index=(error_history_index+1)%3
        persistent_error = np.mean(error_history)
        set_rpm += adjustment * max_rpm
        set_rpm = np.clip(set_rpm, 0, max_rpm)

# Calculate the torque based on the error between the set RPM and actual RPM
    error = target_rpm - actual_rpm  # The difference between target and actual RPM
    
    # Calculate torque: Torque is proportional to the error
    torque = torque_constant * error  # Apply the torque constant to the error
    

    # Apply the inertia effect to the change in RPM
    angular_acceleration = torque / inertia_factor  # Newton's second law: torque = inertia * acceleration

    # Update the RPM using the calculated angular acceleration
    actual_rpm += angular_acceleration  # Simulate the effect of the torque on the motor's RPM
    
    # Simulate the gradual response to set RPM
    actual_rpm += inertia_factor * (set_rpm - actual_rpm)  # Simulate gradual response to set RPM
    actual_rpm_nocontrol += inertia_factor * (target_rpm - actual_rpm_nocontrol)  # Simulate gradual response to set RPM
    

    normalized_slope = np.clip(slope[t] * (max_rpm / max_angle), -max_rpm, max_rpm)

    # Store values for plotting
    rpm_values.append(actual_rpm)  # Simulated actual RPM
    rpm_nocontrol_values.append(actual_rpm_nocontrol)  # Simulated actual RPM
    set_rpm_values.append(set_rpm)  # Control system's set RPM
    target_rpm_values.append(target_rpm)  # Target RPM (desired RPM)
    adjustment_values.append(adjustment * max_rpm)
    persistent_compensation_values.append(persistent_compensation * max_rpm)
    persistent_error_values.append(persistent_error)
    normalized_slope_values.append(normalized_slope)

# Plot the results
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
