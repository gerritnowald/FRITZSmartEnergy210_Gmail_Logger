"""digitalizes temperature image files, merges with power data, appends to main dataset and deletes processed files"""

import glob
import argparse
from send2trash import send2trash
import os

import matplotlib.image as mpimg
from matplotlib import pyplot as plt

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

import digit_recognition

# -------------------------------------------------------------------------------
# user input

parser = argparse.ArgumentParser(description='Digitalize temperature graphs downloaded from FRITZ!SmartEnergy email reports.')
parser.add_argument('--attachment_dir', type=str, default='.\\attachments', help='Directory where downloaded attachments are stored (default: ./attachments)')
parser.add_argument('--dataset', type=str, default='data.csv', help='Output CSV file to append data (default: data.csv)')
args = parser.parse_args()

attachment_dir = args.attachment_dir
out_csv = args.dataset

# -------------------------------------------------------------------------------
# get all temperature graph files

files = glob.glob(f'{attachment_dir}\\ha_temp_*.png')

if not files:
    raise Exception(f'No temperature graph files found in {attachment_dir}')

# -------------------------------------------------------------------------------
# x-axis: pixel to hour conversion

# x-pixel     48 corresponds to hour  0
# x-pixel 960-16 corresponds to hour 24
min_max_hour = 24 * (np.array([49, 960-26]) - 48) / (960-16 - 48)
hour_px = np.linspace(min_max_hour[0], min_max_hour[1], 885)

# Create new hour values at every 15 minutes
hour = np.arange(0, 24, 15/60)

# -------------------------------------------------------------------------------
# y-axis: pixel to temperature conversion

for file in files:

    # read image
    img = mpimg.imread(file)

    # grayscale image
    gray = img[..., :3].mean(axis=2)

    # Threshold: find dark pixels (line)
    line_mask = (gray > 0.6) * 1

    # determine y-axis scale by comparing the tick labels to the references
    tick_labels_pixels = {
        'upper_left'   : line_mask[ 56:65 , 22:29], # upper label, left   digit
        'upper_middle' : line_mask[ 56:65 , 30:37], # upper label, middle digit
        'upper_right'  : line_mask[ 56:65 , 38:45], # upper label, right  digit
        'lower_left'   : line_mask[256:265, 22:29], # lower label, left   digit
        'lower_middle' : line_mask[256:265, 30:37], # lower label, middle digit
        'lower_right'  : line_mask[256:265, 38:45], # lower label, right  digit
    }

    tick_labels_numbers = tick_labels_pixels.copy()
    for key in tick_labels_pixels:
        tick_labels_numbers[key], min_residual = digit_recognition.recognize_digit(tick_labels_pixels[key])
        if min_residual > 0:
            raise Exception(f'No matching {key} tick label found for {file}')

    y_max = int(tick_labels_numbers['upper_left'] + tick_labels_numbers['upper_middle'] + tick_labels_numbers['upper_right'])
    y_min = int(tick_labels_numbers['lower_left'] + tick_labels_numbers['lower_middle'] + tick_labels_numbers['lower_right'])

    # Extract the (topmost) y-pixel number of the line
    zero_mask = (line_mask == 0)
    line_y = zero_mask.argmax(axis=0).astype(float)
    line_y[~zero_mask.any(axis=0)] = np.nan

    # convert pixels to values
    # y-pixel 267 corresponds to temperature y_min
    # y-pixel  66 corresponds to temperature y_max
    temp = (line_y[49:-26] - 267) * (y_max - y_min) / (66 - 267) + y_min

    # Interpolate temperature values to every 15 minutes
    temp = np.interp(hour, hour_px, temp)

    # extract date from filename
    date = file.split('_')[-3]

    # -------------------------------------------------------------------------------
    # load corresponding csv file with power data and add temperature data

    csvfile = sorted(glob.glob(f'{attachment_dir}\\{date}*.csv'))[-1] # get latest csv file of that day
    data = pd.read_csv(csvfile, header=1, sep=';', decimal=',')

    data['Power / W'] = data['Verbrauchswert'] / 0.25 # energy is in Wh per 15 minutes = 0.25 hours

    data = data[['Datum/Uhrzeit', 'Power / W']]    # retain only relevant columns
    data.rename(columns={'Datum/Uhrzeit': 'Time'}, inplace=True)

    data['Time'] = pd.to_datetime(date + data['Time'], format='%Y%m%d%H:%M', errors='coerce')   # add date to time 

    data['Temperature / C'] = temp.round(3)

    # -------------------------------------------------------------------------------
    # append to main dataset

    # ensure same column order as existing file if present
    if os.path.exists(out_csv):
        data.to_csv(out_csv, mode='a', header=False, index=False)
    else:
        data.to_csv(out_csv, mode='w', header=True, index=False)

    print(f'{file} digitalized and appended to data.csv')

    # -------------------------------------------------------------------------------
    # remove all files with same date from attachments folder

    files2trash = glob.glob(f'{attachment_dir}\\*{date}*')
    for file2trash in files2trash:
        send2trash(file2trash)
        print(f'Moved to trash: {file2trash}')

    print(' ')

# -------------------------------------------------------------------------------
# plot

# curve fit temperature data
def sine(x, Ay, Ad, Tavg, φy, φd):
    return Ay * np.sin(2 * np.pi / (365 * 24 * 60 * 60) * x + φy) + \
            Ad * np.sin(2 * np.pi / (24 * 60 * 60      ) * x + φd) + Tavg

data.dropna(inplace=True, axis=0)

seconds = (data['Time']-data['Time'].iloc[0]).dt.total_seconds()
params, _ = curve_fit(sine, seconds, data['Temperature / C'])
data['Temperature fit'] = sine(seconds, *params)

# plot last 14 days
ax = data.iloc[-14*96:].plot(
    x='Time', y=['Temperature / C','Temperature fit','Power / W'],
    secondary_y='Power / W',
    xlabel='Date',
    title=f'Temperature (14 days)',
    grid=True,
    style=['-',':','--']
)
ax.set_ylabel('Temperature / °C')
ax.right_ax.set_ylabel('Power / W')
plt.show()