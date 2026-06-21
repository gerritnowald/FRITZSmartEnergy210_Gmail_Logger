import pandas as pd
import numpy as np

from scipy.optimize import curve_fit

import argparse

from matplotlib import pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter

# -------------------------------------------------------------------------------
# argument parsing

parser = argparse.ArgumentParser(description='Plot temperature and power data from CSV file.')
parser.add_argument('--dataset',   type=str, default='data.csv', help='CSV file to read data from (default: data.csv)')
parser.add_argument('--hours_avg', type=int, default=4,  help='Number of hours for moving average (default: 4)')
parser.add_argument('--days_avg',  type=int, default=14, help='Number of days for moving average (default: 14)')
args = parser.parse_args()

# -------------------------------------------------------------------------------
# load data file

data = pd.read_csv(args.dataset)
data['Time'] = pd.to_datetime(data['Time'])

# -------------------------------------------------------------------------------
# curve fit

def sine(x, Ay, Ad, Tavg, φy, φd):
    return Ay * np.sin(2 * np.pi / (365 * 24 * 60 * 60) * x + φy) + \
           Ad * np.sin(2 * np.pi / (24 * 60 * 60      ) * x + φd) + Tavg

data.dropna(inplace=True, axis=0)

seconds = (data['Time']-data['Time'].iloc[0]).dt.total_seconds()
params, _ = curve_fit(sine, seconds, data['Temperature / C'])
data['Temperature fit'] = sine(seconds, *params)

print("Fitted temperature function:")
print(f"{params[0]:7.2f} * np.sin(2π t/a + {params[3]:.2f}) + \n" \
      f"{params[1]:7.2f} * np.sin(2π t/d + {params[4]:.2f}) + {params[2]:.2f}")

# -------------------------------------------------------------------------------
# all data over time

# low pass filter (moving average)
data['Temperature MA'] = data['Temperature / C'].rolling(args.hours_avg*4, min_periods=1).mean()
data['Temperature MA'] = data['Temperature MA'].shift(- args.hours_avg*2)

fig1, axes1 = plt.subplots(nrows=2, ncols=1, figsize=(9, 16), sharex=True)
fig1.suptitle(f'All data over time ({data.shape[0]//96} days)')

# temperature
ax1 = data.plot(
    x='Time', y=['Power / W','Temperature fit','Temperature / C','Temperature MA'],
    secondary_y='Power / W',
    ax=axes1[0],
    legend=True,
    grid=True, 
)
widths = [ 0.2, 0.1, 0.5]   # fit, temp, temp_ma
for lw, line in zip(widths, ax1.get_lines()):
    line.set_linewidth(lw)
ax1.right_ax.lines[0].set_linewidth(0.2)    # power
ax1.set_ylabel('Temperature / °C')
ax1.right_ax.set_ylabel('Power / W')

#  energy
energy = data.copy()
energy['Time'] = energy['Time'].dt.date
energy = energy.groupby('Time').agg('sum')
energy['Energy / kWh'] = energy['Power / W'] * 0.25 / 1e3  # convert to kWh

# moving average
energy['Energy MA'] = energy['Energy / kWh'].rolling(args.days_avg, min_periods=1).mean()
energy['Energy MA'] = energy['Energy MA'].shift(- args.days_avg // 2)

energy.plot(
    y=['Energy / kWh', 'Energy MA'],
    ax=axes1[1],
    drawstyle='steps-post',
    ylabel='Energy per day / kWh',
    xlabel='Date',
    rot=45,
    legend=True,
    grid=True)
axes1[1].fill_between(energy.index, energy['Energy / kWh'].values, step='post', alpha=1)

# -------------------------------------------------------------------------------
# over time of day, stats from last x days

stats = data.copy()
stats = stats.iloc[-args.days_avg*96:] # filter last x days
stats['Time'] = stats['Time'].dt.time
stats = stats.groupby('Time').agg(['min','median','max'])

# Create datetime index for proper hourly ticks
stats.index = pd.to_datetime('2000-01-01 ' + stats.index.astype(str))

fig2, axes2 = plt.subplots(nrows=2, ncols=1, figsize=(9, 16), sharex=True)
fig2.suptitle(f'Data over time of day (last {args.days_avg} days)')

# temperature
stats['Temperature / C'].plot(
    y=['max', 'median', 'min'],
    style=['k:', '-', 'k:'],
    ax=axes2[0],
    ylabel='Temperature / °C',
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

# Set hourly xticks
axes2[1].xaxis.set_major_locator(HourLocator(interval=1))
axes2[1].xaxis.set_major_formatter(DateFormatter('%H:%M'))

plt.show()