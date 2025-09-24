import glob
import argparse
from send2trash import send2trash

import matplotlib.image as mpimg

import numpy as np
import pandas as pd

# -------------------------------------------------------------------------------
# user input

parser = argparse.ArgumentParser(description='Digitalize temperature graphs downloaded from FRITZ!SmartEnergy email reports.')
parser.add_argument('--attachment_dir', type=str, default='.\\attachments', help='Directory where downloaded attachments are stored (default: ./attachments)')
args = parser.parse_args()

attachment_dir = args.attachment_dir

# -------------------------------------------------------------------------------
# reference tick labels to determine y axis scale

tick_labels = {
    20: np.array([
        [1, 0, 0, 0, 0, 0, 1],
        [0, 0, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 0, 0, 1],
        [1, 1, 1, 0, 0, 1, 1],
        [1, 1, 0, 0, 1, 1, 1],
        [1, 0, 0, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]
    ]),
    40: np.array([
        [1, 1, 1, 1, 0, 0, 1],
        [1, 1, 1, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 1],
        [0, 0, 1, 1, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 1],
        [1, 1, 1, 1, 0, 0, 1],
        [1, 1, 1, 0, 0, 0, 0]
    ])
}

# -------------------------------------------------------------------------------
# residual function to compare tick labels

residual = lambda x, y: np.sum(np.abs(x - y))

# -------------------------------------------------------------------------------
# get all temperature graph files

files = glob.glob(f'{attachment_dir}\\ha_temp_*.png')

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

    # determine y-axis scale by checking the tick labels (max either 20°C or 40°C)
    # find the closest tick label to the reference labels
    tick_label = line_mask[56:65, 30:37]
    y_max = min(tick_labels, key=lambda k: residual(tick_label, tick_labels[k]))

    # Extract the (topmost) y-pixel number of the line
    zero_mask = (line_mask == 0)
    line_y = zero_mask.argmax(axis=0).astype(float)
    line_y[~zero_mask.any(axis=0)] = np.nan

    # convert pixels to values
    # y-pixel 267 corresponds to temperature 0
    # y-pixel  66 corresponds to temperature y_max
    temp = y_max * (line_y[49:-26] - 267) / (66 - 267)

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

    dataset = pd.read_csv('data.csv')
    dataset = pd.concat([dataset, data], ignore_index=True)
    dataset.to_csv('data.csv', index=False)

    print(f'{file} digitalized and appended to data.csv')

    # -------------------------------------------------------------------------------
    # remove all files with same date from attachments folder

    files2trash = glob.glob(f'{attachment_dir}\\*{date}*')
    for file2trash in files2trash:
        send2trash(file2trash)
        print(f'Moved to trash: {file2trash}')

    print(' ')