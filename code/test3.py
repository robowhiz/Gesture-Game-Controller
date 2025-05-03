import numpy as np
import matplotlib.pyplot as plt

# Generate a sample signal
fs = 1000  # Sampling frequency
t = np.arange(0, 1, 1/fs)  # Time vector
frequency = 5  # Frequency of the signal
signal = np.sin(2 * np.pi * frequency * t)

# Perform FFT
fft_result = np.fft.fft(signal)
fft_freq = np.fft.fftfreq(len(fft_result), 1/fs)

# Identify low-frequency components
low_freq_mask = np.abs(fft_freq) < 10  # Change the threshold as needed
low_freq_components = fft_result.copy()
low_freq_components[~low_freq_mask] = 0

# Inverse FFT to obtain the signal with only low-frequency components
filtered_signal = np.fft.ifft(low_freq_components)

# Plot original and filtered signals
plt.figure(figsize=(12, 8))
plt.subplot(3, 1, 1)
plt.plot(t, signal)
plt.title('Original Signal')

plt.subplot(3, 1, 2)
plt.plot(t, filtered_signal.real)
plt.title('Filtered Signal (Low-Frequency Components)')

# Plot FFT of the original signal
plt.subplot(3, 1, 3)
plt.plot(fft_freq, np.abs(fft_result))
plt.title('FFT of Original Signal')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.grid(True)

plt.tight_layout()
plt.show()