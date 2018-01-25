##Source : https://jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

string = 'C:/ffmpeg/bin/ffmpeg'
plt.rcParams['animation.ffmpeg_path'] = string.decode('utf-8')

fig, ax = plt.subplots()
xdata, ydata ,xdata1, ydata1= [], [], [], []

x = [1,1,2,2]
x1 = [1,2]
my_xticks = ['Data 1', 'Data 2']
y = [100856.83, 93621.38, 42403, 37143.26]

plt.xticks(x1, my_xticks)
plot1, = plt.plot([], [], 'rD', animated=True)
plot2, = plt.plot([], [], 'gD', animated=True)
plt.legend([plot1,plot2], ["Total Cost from Modified Eisenhut heuristic","Total Cost from Modified Dixon-Silver heuristic"])
plt.xlabel("Data Set")
plt.ylabel("Total Cost")
plt.title("Comparison of Total cost for two heuristics with different data sets")

def init():
    ax.set_xlim(0,3)
    ax.set_ylim(min(y) - 10000, max(y) + 30000)
    return plot1,

def init1():
    ax.set_xlim(0, 3)
    ax.set_ylim(min(y) - 10000, max(y) + 10000)
    return plot2,

def update(frame):
    xdata.append(x[frame - 1])
    ydata.append(y[frame - 1])
    plot1.set_data(xdata, ydata)
    return plot1,

def update1(frame):
    xdata1.append(x[frame - 1])
    ydata1.append(y[frame - 1])
    plot2.set_data(xdata1, ydata1)
    return plot2,



a = FuncAnimation(fig, update, frames=np.arange(1,2),
                    init_func=init, blit=True, interval = 2000, repeat = 0)
an = FuncAnimation(fig, update1, frames=np.arange(2,3),
                    init_func=init1, blit=True, interval = 4000, repeat = 0)
ani = FuncAnimation(fig, update, frames=np.arange(3,4),
                    init_func=init, blit=True, interval = 6000, repeat = 0)
anim = FuncAnimation(fig, update1, frames=np.arange(4,5),
                    init_func=init1, blit=True, interval = 8000, repeat = 0)


# FFwriter=animation.FFMpegWriter(fps=30, extra_args=['-vcodec', 'libx264'])
# anim.save('basic_animation.mp4', writer=FFwriter)

plt.show()