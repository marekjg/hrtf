import cv2
import pyaudio

import numpy as np
from scipy.io import loadmat


def angle_to_idx(angle):
    idx = int(np.argmin(np.abs(azimuths - angle)))
    return idx


def pyaudio_callback(in_data, frame_count, time_info, status):
    global i
    global dist
    x = np.random.randn(frame_count) * dist ** 2 / 5
    x_l = np.convolve(x, hrir_l[i], mode='same')
    x_r = np.convolve(x, hrir_r[i], mode='same')
    x = np.vstack((x_r, x_l)).T

    x = x.flatten().astype('float32')
    x = x.tostring()
    return x, pyaudio.paContinue


def mouse_callback(event, x, y, flags, param):
    global win_x
    global win_y
    global i
    global dist

    win_x, win_y = x, y
    x, y = x - 256, 512 - y
    angle = -90 + np.arctan2(y, x) * 180 / np.pi
    dist = 1 - (x ** 2 + y ** 2) ** 0.5 / (256 ** 2 + 512 ** 2) ** 0.5
    i = angle_to_idx(angle)
    print(i, angle, dist)


def initialize_cv2():
    win_name = 'room'
    cv2.namedWindow(win_name)
    cv2.setMouseCallback(win_name, mouse_callback)
    img = np.uint8(np.zeros((512, 512)))
    return win_name, img

win_name, img = initialize_cv2()
win_x, win_y = 0, 0

hrir = loadmat('hrir_final.mat')
hrir_l = hrir['hrir_l'][:, 49, :]
hrir_r = hrir['hrir_r'][:, 49, :]
azimuths = np.float32([-80, -65, -55, -45, -40,
                       -35, -30, -25, -20, -15,
                       -10, -5, 0, 5, 10,
                       15, 20, 25, 30, 35,
                       40, 45, 55, 65, 80])
i = 17
dist = 0.01

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=2,
                rate=44100,
                output=True,
                frames_per_buffer=2048,
                stream_callback=pyaudio_callback)

stream.start_stream()
radius = 0
while stream.is_active():
    img[:] = 0
    cv2.circle(img, (win_x, win_y), radius // 2, 128, 1)
    radius = (radius + 1) % 100
    cv2.imshow(win_name, img)

    key = cv2.waitKey(1)
    if key == 27:
        break

stream.stop_stream()
stream.close()
p.terminate()
