import pandas as pd
import numpy as np

from scipy.optimize import curve_fit

import datetime

from matplotlib import pyplot as plt
# plt.style.use('dark_background')

# -------------------------------------------------------------------------------
# load data file

data = pd.read_csv('data.csv')
data['Time'] = pd.to_datetime(data['Time'])

# -------------------------------------------------------------------------------
# low pass filter (moving average)

hours_avg = 4

# data is sampled every 15 minutes
data['Temperature MA'] = data['Temperature / C'].rolling(hours_avg*4, min_periods=1).mean()
data['Temperature MA'] = data['Temperature MA'].shift(- hours_avg*2)

# -------------------------------------------------------------------------------
# curve fit

def sine(x, Ay, Ad, Tavg, φy, φd):
    return Ay * np.sin(2 * np.pi / (365 * 24 * 60 * 60) * x + φy) + \
           Ad * np.sin(2 * np.pi / (24 * 60 * 60      ) * x + φd) + Tavg

data.dropna(inplace=True, axis=0)

seconds = (data['Time']-data['Time'].iloc[0]).dt.total_seconds()
params, _ = curve_fit(sine, seconds, data['Temperature / C'])
data['Temperature fit'] = sine(seconds, *params)

print(params)

# -------------------------------------------------------------------------------
# Overview (14 days)

ax1 = data.iloc[-14*96:].plot(
    x='Time', y=['Temperature / C','Temperature fit','Power / W'],
    secondary_y='Power / W',
    xlabel='Date',
    title=f'Overview (14 days)',
    grid=True,
    style=['-',':','--']
)
ax1.set_ylabel('Temperature / °C')
ax1.right_ax.set_ylabel('Power / W')

# -------------------------------------------------------------------------------
# all data over time

fig1, axes1 = plt.subplots(nrows=2, ncols=1, figsize=(9, 16), sharex=True)
fig1.suptitle('All data over time')

# temperature
ax2 = data.plot(
    x='Time', y='Temperature MA',
    ax=axes1[0],
    xlabel='Date',
    ylabel='Temperature / °C', 
    legend=False,
    grid=True, 
    linewidth=.4
)
axes1[0].plot(data['Time'], data['Temperature fit'], '--', linewidth=.3)
axes1[0].legend(['Measurement (MA)', 'Fit'])

#  energy
energy = data.copy()
energy['Time'] = energy['Time'].dt.date
energy = energy.groupby('Time').agg('sum')
energy = energy['Power / W'] * 0.25 / 1e3  # convert to kWh

energy.plot(
    ax=axes1[1],
    drawstyle='steps-mid',
    ylabel='Energy per day / kWh',
    xlabel='Time',
    rot=45,
    grid=True)
axes1[1].fill_between(energy.index, energy.values, step='mid', alpha=1)

# -------------------------------------------------------------------------------
# over time of day, stats from last 14 days

days = 14

stats = data.copy()
stats = stats.iloc[-days*96:] # filter last 14 days
stats['Time'] = stats['Time'].dt.time
stats = stats.groupby('Time').agg(['min','median','max'])

fig2, axes2 = plt.subplots(nrows=2, ncols=1, figsize=(9, 16), sharex=True)
fig2.suptitle(f'Data over time of day (last {days} days)')

# temperature
stats['Temperature / C'].plot(
    y=['max', 'median', 'min'],
    style=['k:', '-', 'k:'],
    ax=axes2[0],
    ylabel='Temperature / °C',
    xlabel='Time',
    grid=True
)

# power
start_time = datetime.time(6, 0)
end_time   = datetime.time(18, 0)

filtered_stats = stats[stats.index.to_series().between(start_time, end_time)]

filtered_stats['Power / W'].plot(
    y=['max', 'median'],
    style=['k--', '-'],
    drawstyle='steps-pre',
    ax=axes2[1],
    ylabel='Power / W',
    xlabel='Time',
    grid=True
)

plt.show()