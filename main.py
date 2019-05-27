import time

import pyaudio

import numpy as np
from scipy.io import loadmat


def callback(in_data, frame_count, time_info, status):
    global i
    x = 0.1 * np.random.randn(frame_count)
    x_l = np.convolve(x, hrir_l[i // 4], mode='same')
    x_r = np.convolve(x, hrir_r[i // 4], mode='same')
    x = np.vstack((x_r, x_l)).T

    x = x.flatten().astype('float32')
    x = x.tostring()
    i = (i + 1) % 100
    return (x, pyaudio.paContinue)

hrir = loadmat('hrir_final.mat')
hrir_l = hrir['hrir_l'][:, 49, :]
hrir_r = hrir['hrir_r'][:, 49, :]
i = 0

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=2,
                rate=44100,
                output=True,
                frames_per_buffer=2048,
                stream_callback=callback)

stream.start_stream()
while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()
p.terminate()
