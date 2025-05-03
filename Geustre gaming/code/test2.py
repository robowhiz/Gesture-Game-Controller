from websockets.sync.client import connect
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

uri = "ws://192.168.4.1:81"

websocket = connect(uri)
print("connected")

Quaternion = np.array([0.0]*4)
gyro = np.array([0]*3)
accel = np.array([0]*3)
millis = 0
gravity = np.array([0.0]*3)
ypr = np.array([0.0]*3)
linearaccel = np.array([0.0]*3)

data_buffer = np.array([[0.0] * 6] * 200)
data_buffer_head = 0

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

def plot(length):
    df = pd.DataFrame(data_buffer)
    first = df[:length]
    second = df[length:]

    df = pd.concat([second, first]).reset_index(drop = True)[-70:]

    plt.cla()
    for i in range(3):
        plt.ylim([-20000, 20000])
        plt.plot(range(len(df[0])), df[i])
    plt.pause(0.001)

import joblib
model = joblib.load("test.joblib")

import pyautogui
import scipy.stats as stats
from scipy.signal import find_peaks

def filtered(df):
    data = []
    imaginary = []
    for i in range(3):
        fft_result = np.fft.fft(df.iloc[:, i].values)
        fft_freq = np.fft.fftfreq(len(fft_result), 0.01)

        # Identify low-frequency components
        low_freq_mask = np.abs(fft_freq) <= 4  # Change the threshold as needed
        low_freq_components = fft_result.copy()
        low_freq_components[~low_freq_mask] = 0

        # Inverse FFT to obtain the signal with only low-frequency components
        filtered_signal = np.fft.ifft(low_freq_components).real
        data.append(filtered_signal)
        imaginary.append(low_freq_components.imag[:3])
    return np.array(data), np.array(imaginary)

def slope(data):
    peaks, _ = find_peaks(data)
    # plt.plot(peaks, filtered_signal[peaks], "rx")
    valleys, _ = find_peaks(-data)
    # plt.plot(valleys, filtered_signal[valleys], "bx") 

    dx = peaks[:, np.newaxis] - valleys
    dy = data[peaks][:, np.newaxis] - data[valleys]

    return((dy/dx).flatten())

def accl_features(df):
    filtered_signal, _ = filtered(df)
    features = []

    df_dx = slope(filtered_signal[1])
    features.extend([min(df_dx) if len(df_dx) != 0 else 0])

    df_dx = slope(filtered_signal[2])
    features.extend([min(df_dx) if len(df_dx) != 0 else 0])

    features.extend([np.percentile(filtered_signal[0], 100)])
    features.extend([np.percentile(filtered_signal[1], 100)])

    features.extend([stats.iqr(filtered_signal[1])])

    features.extend([np.mean(filtered_signal[0][:25])])
    features.extend([np.mean(filtered_signal[1][:25])])

    features.extend([np.median(filtered_signal[1][:25])])

    features.extend([np.percentile(filtered_signal[1][:25], 70)])
    return features

def gyro_features(df):
    filtered_signal, imaginary = filtered(df)
    features = []

    features.extend([imaginary[0][1]])
    features.extend([imaginary[2][1]])

    features.extend([(imaginary[0]).mean()])
    features.extend([(imaginary[2]).mean()])

    features.extend([stats.iqr(filtered_signal[0])])
    features.extend([stats.iqr(filtered_signal[2])])

    features.extend([np.ptp(filtered_signal[2])])

    features.extend([np.std(filtered_signal[2])])

    features.extend([np.mean(filtered_signal[0][:25])])

    features.extend([np.median(filtered_signal[0][:25])])
    return features

counter = 0

def predict(length):
    global counter
    df = pd.DataFrame(data_buffer)
    first = df[:length]
    second = df[length:]

    df = pd.concat([second, first]).reset_index(drop = True)[-50:]
    
    feature = accl_features(df.iloc[:, 0:3])
    feature.extend(gyro_features(df.iloc[:, 3:6]))

    prediction = model.decision_function([feature])[0]
    print(prediction)
    if prediction[0] > 5:
        counter += 1
        if counter == 1:
            print("granade")
            # pyautogui.press("g")
    elif prediction[1] > 5:
        counter += 1
        if counter == 1:
            print("gun 1")
            # pyautogui.press("1")
    elif prediction[2] > 5:
        counter += 1
        if counter == 1:
            print("gun 2")
            # pyautogui.press("2")
    elif prediction[3] > 5:
        counter += 1
        if counter == 1:
            print("jump")
            # pyautogui.press("j")
    elif prediction[4] > 5:
        counter += 1
        if counter == 1:
            print("punch")
            # pyautogui.press("p")
    elif prediction[5] > 5:
        # pyautogui.press("j")
        # print("switch")
        counter = 0

try:
    while True:
        buffer = bytes.fromhex(websocket.recv(24).hex())
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
        
        for i in range(0, 3):
            data_buffer[data_buffer_head][i] = linearaccel[i]
        
        for i in range(3, 6):
            data_buffer[data_buffer_head][i] = ypr[i - 3]
        
        data_buffer_head = (data_buffer_head + 1)%200
        
        if data_buffer_head % 2 == 0:
            # plot(data_buffer_head)
            predict(data_buffer_head)

        # print(round(gravity[0], 2), round(gravity[1], 2), round(gravity[2], 2), round(linearaccel[0], 2), round(linearaccel[1], 2), round(linearaccel[2], 2), round(np.rad2deg(ypr[0]), 2), round(np.rad2deg(ypr[1]), 2), round(np.rad2deg(ypr[2]), 2), millis)

except KeyboardInterrupt:
    print("closing the web socket")
    websocket.close()
websocket.close()