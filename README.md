# 🚀 Line-Following Buggy Simulator

## 📌 Project Overview
This project is a **realistic simulator** for testing line-following buggies using **real-world physics** and **sensor models**. Teams can use this simulator to develop and test their **C++ control algorithms** before running them on actual hardware.

### 🔥 **Key Features**
✅ **Accurate Buggy Motion Simulation** – Models acceleration, braking, drift, and ground friction.  
✅ **Realistic IR Sensor Simulation** – Detects track lines with sensor delay & noise.  
✅ **C++ Control Algorithm Compatibility** – Run real buggy code inside the simulator.  
✅ **Buggy Profile Loader** – Use real-world test data to match actual buggy performance.  
✅ **2D Visualization & Track Editor** – Watch the buggy follow a track in real-time.  

---

## 📦 **Installation**
### **1️⃣ Install Dependencies**
Ensure you have Python & necessary libraries:
```bash
pip install numpy matplotlib pybind11
```
If using C++ control integration:
```bash
sudo apt install g++   # (Linux)
```
``` bash
brew install gcc       # (Mac)
```
2️⃣ Clone the Repository
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/buggy-simulator.git
cd buggy-simulator
```
🚀 Getting Started
Running the Simulation
To test a basic buggy motion simulation, run:
``` bash
python simulator.py --track sample_track.json
```
To run a C++ control algorithm inside the simulator, use:
``` bash
python simulator.py --control team_algorithm.so
```
🔧 Project Structure
``` bash
/buggy-simulator
├── /simulation        # Physics engine & sensors
├── /control           # C++ integration & control interface
├── /tests             # Characterization test scripts
├── /visualization     # 2D UI & track editor
├── simulator.py       # Main simulation entry point
├── buggy_profiles.json # Test results for different buggies
├── README.md          # Project documentation
```
📜 How It Works
1️⃣ Define Your Buggy Profile
Before running the simulator, teams should run characterization tests on their real buggy and save the results in buggy_profiles.json.
Example:
```json
{
    "Left_Motor_Constant": 0.8,
    "Right_Motor_Constant": 0.82,
    "Drift_Correction_Factor": 0.03,
    "Battery_Voltage": 12.0,
    "Ground_Friction_Coefficient": 0.05
}
```
2️⃣ Implement a Control Algorithm
Teams write a control.cpp file that processes sensor readings and outputs motor commands:
```cpp
float left_motor_power, right_motor_power;
void update(float error, float sensor_values[]) {
    left_motor_power = 0.5 - error * 0.1;
    right_motor_power = 0.5 + error * 0.1;
}
```
Compile it to a shared library (team_algorithm.so) and load it into the simulator.

🛠 Contributing
👩‍💻 Want to help? Check out our GitHub issues and open a pull request!
