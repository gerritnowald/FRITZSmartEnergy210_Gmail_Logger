import pandas as pd
import numpy as np

from scipy.optimize import curve_fit

import argparse

from matplotlib import pyplot as plt
# plt.style.use('dark_background')

# -------------------------------------------------------------------------------
# argument parsing

parser = argparse.ArgumentParser(description='Plot temperature and power data from CSV file.')
parser.add_argument('--dataset', type=str, default='data.csv', help='CSV file to read data from (default: data.csv)')
parser.add_argument('--hours_avg', type=int, default=4, help='Number of hours for moving average (default: 4)')
parser.add_argument('--days', type=int, default=14, help='Number of days to show in time of day plot (default: 14)')
args = parser.parse_args()

# -------------------------------------------------------------------------------
# load data file

data = pd.read_csv(args.dataset)
data['Time'] = pd.to_datetime(data['Time'])

# -------------------------------------------------------------------------------
# low pass filter (moving average)

# data is sampled every 15 minutes
data['Temperature MA'] = data['Temperature / C'].rolling(args.hours_avg*4, min_periods=1).mean()
data['Temperature MA'] = data['Temperature MA'].shift(- args.hours_avg*2)

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
# Overview (x days)

ax1 = data.iloc[-args.days*96:].plot(
    x='Time', y=['Temperature / C','Temperature fit','Power / W'],
    secondary_y='Power / W',
    xlabel='Date',
    title=f'Overview ({args.days} days)',
    grid=True,
    style=['-',':','--']
)
ax1.set_ylabel('Temperature / °C')
ax1.right_ax.set_ylabel('Power / W')

# -------------------------------------------------------------------------------
# all data over time

fig1, axes1 = plt.subplots(nrows=2, ncols=1, figsize=(9, 16), sharex=True)
fig1.suptitle(f'All data over time ({data.shape[0]//96} days)')

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
# over time of day, stats from last x days

stats = data.copy()
stats = stats.iloc[-args.days*96:] # filter last x days
stats['Time'] = stats['Time'].dt.time
stats = stats.groupby('Time').agg(['min','median','max'])

fig2, axes2 = plt.subplots(nrows=2, ncols=1, figsize=(9, 16), sharex=True)
fig2.suptitle(f'Data over time of day (last {args.days} days)')

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
stats['Power / W'].plot(
    y=['max', 'median', 'min'],
    style=['k:', '-', 'k:'],
    drawstyle='steps-pre',
    ax=axes2[1],
    ylabel='Power / W',
    xlabel='Time',
    grid=True
)

plt.show()