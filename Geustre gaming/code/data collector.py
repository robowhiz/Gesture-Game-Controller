from functions.realtime_plotter import websocketplotter
import numpy as np
import time
import pandas as pd

my_plotter = websocketplotter(3, 200, 100, 10, [-20000, 20000])

Quaternion = np.array([0.0]*4)
gyro = np.array([0]*3)
accel = np.array([0]*3)
millis = 0
gravity = np.array([0.0]*3)
ypr = np.array([0.0]*3)
linearaccel = np.array([0.0]*3)

def getGravity():
    gravity[0] = 2 * (Quaternion[1]*Quaternion[3] - Quaternion[0]*Quaternion[2])
    gravity[1] = 2 * (Quaternion[0]*Quaternion[1] + Quaternion[2]*Quaternion[3])
    gravity[2] = Quaternion[0]*Quaternion[0] - Quaternion[1]*Quaternion[1] - Quaternion[2]*Quaternion[2] + Quaternion[3]*Quaternion[3]

def getYawPitchRoll():
    # yaw: (about Z axis)
    ypr[0] = np.arctan2(2*Quaternion[1]*Quaternion[2] - 2*Quaternion[0]*Quaternion[3], 2*Quaternion[0]*Quaternion[0] + 2*Quaternion[1]*Quaternion[1] - 1)
    # pitch: (nose up/down, about Y axis)
    ypr[1] = np.arctan2(gravity[0] , (gravity[1]*gravity[1] + gravity[2]*gravity[2])**0.5)
    # roll: (tilt left/right, about X axis)
    ypr[2] = np.arctan2(gravity[1] , gravity[2])
    if gravity[2] < 0:
        if ypr[1] > 0 :
            ypr[1] = np.pi - ypr[1]
        else:
            ypr[1] = -np.pi - ypr[1]

def getLinearAccel():
    # get rid of the gravity component (+1g = +8192 in standard DMP FIFO packet, sensitivity is 2g)
    linearaccel[0] = accel[0] - gravity[0]*8192
    linearaccel[1] = accel[1] - gravity[1]*8192
    linearaccel[2] = accel[2] - gravity[2]*8192

if my_plotter.initialize_connection("192.168.4.1", 81, 24):
    try:
        start_time = time.time()
        while True:
            buffer = my_plotter.read_websocket()
            for i in range(0, 8, 2):
                Quaternion[i//2] = int.from_bytes(buffer[i:i + 2],byteorder="big",  signed=True)/16384
            for i in range(8, 14, 2):
                gyro[(i - 8)//2] = int.from_bytes(buffer[i:i + 2],byteorder="big",  signed=True)
            for i in range(14, 20, 2):
                accel[(i - 14)//2] = int.from_bytes(buffer[i:i + 2],byteorder="big",  signed=True)
            millis = (buffer[23] << 24) | (buffer[22] << 16) | (buffer[21] << 8) | buffer[20]

            getGravity()
            getLinearAccel()
            getYawPitchRoll()
            pd.DataFrame(np.concatenate([np.round(linearaccel, 3), np.round(ypr, 3), [millis, round(time.time() - start_time, 5)]])).T.to_csv("data/test.csv", mode = "a", index = False, header = None)
            my_plotter.plot(linearaccel)
    
    except KeyboardInterrupt:
        print("ending")
        my_plotter.close()

else:
    print("Connection failed. Exiting.")