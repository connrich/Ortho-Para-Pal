import pandas as pd
from pandas.api.types import is_numeric_dtype
from os.path import exists
import os
from datetime import datetime
from pytz import timezone
from matplotlib import pyplot as plt



# Classes for organizing H state info
class Ortho:
    # Wavelength range in 1/cm
    range = [580, 595]
    # Stores peak height
    peak = 0
    # Stores integral sum
    integral = 0

class Para:
    # Wavelength range in 1/cm
    range = [347, 365]
    # Stores peak height
    peak = 0
    # Stores integral sum
    integral = 0

# Validates if the data frame has the correct formatting
def isDFValid(df):
    if len(df.columns) != 2:
        return False
    if not is_numeric_dtype(df[0]) or not is_numeric_dtype(df[1]):
        return False
    
    return True

# Calculates a linear baseline correction over a window
# window = [low, high]
def linear_correction(df, window):
    # Filter for lower spectrum
    cut_low = df[0] >= window[0]
    df = df[cut_low]
    # Filter for higher spectrum
    cut_high = df[0] <= window[1]
    df = df[cut_high]

    # Coordinates for linear baseline estimation
    first_point = df.iloc[0]
    x1 = first_point[0]
    y1 = first_point[1]
    last_point = df.iloc[-1]
    x2 = last_point[0]
    y2 = last_point[1]

    # Characteristics of the line
    slope = (y2 - y1) / (x2 - x1)
    intercept = y2 - (slope * x2)

    # Iterate through the spectrum and subtract the baseline
    for index, row in df.iterrows():
        x = row[0]
        y = row[1]
        y_prime = y - (slope * x + intercept)
        row[1] = y_prime

    return df

def background_subtraction(df, settings):
    # Number of signal averages selected
    # 0 = custom background
    # 20, 30, 50 = standard background
    averages = settings['backgroundSubtractionAverages']

    # Tries loading custom background if selected
    if averages == 0:
        path = settings['customSubtractionBackgroundPath']
        if os.path.exists(path):
            if path.split('.')[-1] == 'csv':
                background_df = pd.read_csv(path, header=None)
                if isDFValid(background_df) and len(df) == len(background_df):
                    df[1] = df[1] - background_df[1]
                    return df, True
            else:
                return df, False
        else:
            return df, False
    else:
        path = f'Resources\\Background Spectra\\20220519_He_5,3PSIG_0,2SLM_295K_1000ms_{averages}av_0ms_3_450mw_00000_counts.csv'
        background_df = pd.read_csv(path, header=None)
        # Check if the background is valid and has same length as the spectrum
        if isDFValid(background_df) and len(df) == len(background_df):
            df[1] = df[1] - background_df[1]
            return df, True # Returns dataframe and whether operation was succesful
        else:
            return df, False # Returns dataframe and whether operation was succesful

# Takes a CSV of wavelengths vs. intensity count
def RatioFinder(file_path, base_correction=True, settings=None):
    # Check if files exists
    if not exists(file_path) or file_path is None or file_path == '':
        return {'Error': 'Invalid path. File could not be found.', 
                'Filename': file_path.split('\\')[-1]}

    # Reset values
    Ortho.peak = 0
    Ortho.integral = 0
    Para.peak = 0
    Para.integral = 0
    if settings is not None:
        Ortho.range = settings['orthoRange']
        Para.range = settings['paraRange']
        base_correction = settings['enableBaselineCorrection']
        baseline_range = settings['baselineRange']
    else:
        base_correction = 0
    
    # Create data frame of spectrum data
    df = pd.read_csv(file_path, header=None)

    # Check validity of the file
    if len(df.columns) != 2:
        return {'Error': 'Invalid CSV. Wrong number of columns. Expects 2 columns: 1st is wavelength(1/cm) and second is intensity count.', 
                'Filename': file_path.split('\\')[-1]}
    if not is_numeric_dtype(df[0]) or not is_numeric_dtype(df[1]):
        return {'Error': 'Encountered wrong datatype in CSV. Expects floats or integers. It also expects no column header names.',
                'Filename': file_path.split('\\')[-1]}

    # Correct baseline if specified
    if base_correction == 1:
        df = linear_correction(df, baseline_range)
    elif base_correction == 2:
        df, success = background_subtraction(df, settings)
        if not success:
            return {'Error': 'Invalid background spectrum. Could not complete subtraction. Validate the selected custom background or select another correction option.',
                    'Filename': file_path.split('\\')[-1],
                    'Background Filename': settings['customSubtractionBackgroundPath']}

    # Iterate through rows
    for index, row in df.iterrows():
        wl = row[0]
        count = row[1]

        # Find peak ranges, integrate them, and save maximum peak height
        if wl < Ortho.range[1] and wl > Ortho.range[0]:
            Ortho.peak = max(Ortho.peak, count)
            Ortho.integral += count
        if wl < Para.range[1] and wl > Para.range[0]:
            Para.peak = max(Para.peak, count)
            Para.integral += count

    # Output dictionary for storing and returning output data
    output = {}
    output['Filename'] = file_path.split('\\')[-1]

    # Try to find time of spectrum capture based on SPC creation time
    # Assumes 'last modified time' is the moment of creation because 'creation time' refers to local machine creation
    # 'creation time' could be the time that the file was copied onto the local machine
    if 'nt' in os.name: # windows OS
        try:
            output['Time'] = datetime.fromtimestamp(os.path.getmtime(file_path.replace('csv', 'spc')))
            output['Time'] = output['Time'].astimezone(timezone('US/Pacific'))
            output['Time'] = output['Time'].strftime("%Y%m%d %H:%M:%S %Z")
        except Exception as e:
            output['Time'] = None
    else: # other OS
        try:
            output['Time'] = datetime.fromtimestamp(os.stat(file_path.replace('csv', 'spc')).st_birthtime)
            output['Time'] = output['Time'].astimezone(timezone('US/Pacific'))
            output['Time'] = output['Time'].strftime("%Y%m%d %H:%M:%S %Z")
        except Exception as e:
            output['Time'] = None

    # Data relating to peak height
    peak_sum = Para.peak + Ortho.peak
    output['Para peak'] = Para.peak
    output['Ortho peak'] = Ortho.peak
    output['Para peak percent'] = Para.peak / peak_sum * 100
    # output['Ortho peak percent'] = Ortho.peak / peak_sum * 100
    output['O/P peak ratio'] = Ortho.peak / Para.peak

    # Data relating to integration
    integral_sum = Para.integral + Ortho.integral
    output['Para integral'] = Para.integral
    output['Ortho integral'] = Ortho.integral
    output['Para integral percent'] = Para.integral / integral_sum * 100
    # output['Ortho integral percent'] = Ortho.integral / integral_sum * 100
    output['O/P integral ratio'] =  Ortho.integral / Para.integral

    return output



if __name__ == "__main__":
    result = RatioFinder('C:/Users/Quantum/Desktop/Raman Spectra/20220412 H2 test LN2 DUT2 0.5in8cm/20220412_H2_154PSI_0.5SLM_77.3K_1_00000.csv')
    print(result)