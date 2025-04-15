import numpy as np

def calculate_error(sensor_values):
    error = 0.0
    count = len(sensor_values)

    if count % 2 == 1:  # odd number of sensors
        mid = count // 2
        weights = np.arange(-mid, mid + 1)
    else:  # even number of sensors
        half = count // 2
        weights = np.concatenate((np.arange(-half, 0), np.arange(1, half + 1)))

    lostcount=0
    for i in range(count):
        if not (sensor_values[i]<0.0001):
            error += sensor_values[i] * weights[i]
        else:
            lostcount+=1
            pass
    
    if lostcount>=count:
        return 9
    return error
