import serial
import struct
import matplotlib.pyplot as plt
import time
import math

s = serial.Serial(port='COM3', baudrate=115200)

plot = 0

if not plot:
    while True:
        rx = s.read(4)
        print(rx.hex(), struct.unpack('f', rx)[0])
        # if struct.unpack('f', rx)[0]==1.0:
        #     print('a')

l = 100
m1 = [0.0] * l
m2 = [0.0] * l
t = [0.0] * l

plt.ion()

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

line1, = ax1.plot(t, m1)
line2, = ax2.plot(t, m2)

t0 = 0

while True:
    # rx = s.read(4)

    data = struct.unpack('f', s.read(4))[0]

    if not t0:
        t0 = time.time()

    t.append(time.time() - t0)
    t.pop(0)

    # print(ch,type(ch))
    # print(data)
    if data == 1.0:
        data = struct.unpack('f', s.read(4))[0]

        m1.append(data)
        m1.pop(0)
        line1.set_ydata(m1)
        line1.set_xdata(t)
        ax1.set_ylim(1.1 * i for i in [min(m1), max(m1)])
        ax1.set_xlim([min(t), max(t)])

    if data == 2.0:
        data = struct.unpack('f', s.read(4))[0]

        m2.append(data)
        m2.pop(0)
        line2.set_ydata(m2)
        line2.set_xdata(t)
        ax2.set_ylim(1.1 * i for i in [min(m2), max(m2)])
        ax2.set_xlim([min(t), max(t)])

    # print(rx.hex(), struct.unpack('f', rx)[0])

    fig.canvas.draw()
    fig.canvas.flush_events()
    # line1.draw()

