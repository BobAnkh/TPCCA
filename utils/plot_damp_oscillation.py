import math

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

def dy(y, t, zeta, w0):
    x, p = y[0], y[1]
    dx = p
    dp = -2 * zeta * w0 * p - w0**2 * x
    return [dx, dp]


y0 = [-0.5, 0.0]
t = np.linspace(0, 10, 1000)
w0 = 1 * math.pi * 1.0

y1 = odeint(dy, y0, t, args=(0.0, w0))
y2 = odeint(dy, y0, t, args=(0.2, w0))
y3 = odeint(dy, y0, t, args=(1.0, w0))
y4 = odeint(dy, y0, t, args=(5.0, w0))

# color_list = ['#2A9D8F', '#E9C46A', '#F4A261', '#E76F51', '#264653']
color_list = ['#68A691', '#4361EE', '#BF0603', '#7209B7', '#F72585']
plt.figure(figsize=(6.4, 3))
plt.plot(t, y1[:, 0], color=color_list[0], label='undamped')
plt.plot(t, y2[:, 0], color=color_list[1], label='under-damped')
plt.plot(t, y3[:, 0], color=color_list[2], label='critically-damped')
plt.plot(t, y4[:, 0], color=color_list[3], label='over-damped')

plt.hlines(0,
           0,
           plt.xlim()[1],
           colors=color_list[4],
           linestyles='dashed',
           label='step excitation')
plt.vlines(0, 0, -0.5, colors=color_list[4], linestyles='dashed')

plt.xticks([])
plt.yticks([])
plt.xlabel('Time (s)', fontsize='12')
plt.ylabel('Throughput (Mbps)', fontsize='12')
plt.legend()
plt.savefig('dampOscillation.pdf', bbox_inches='tight')
