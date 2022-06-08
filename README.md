# Ortho-Para-Pal
A handy tool for analyzing the ratios between ortho-hydrogen and para-hydrogen in Raman spectra.

# Usage
Use MainWindow.py to run the GUI. The 'Resources' folder contains components that are used in the application.
There are two main functions in the main application: Ratio Finder and Visualize.
### Ratio Finder
Ratio Finder will take spectra and determine the ortho-para ratios using peak height ratios and integration ratios. <br />
The Ratio Finder tab is designed to take either a single spectrum or a directory containing spectra. The spectra must be in comma seperated value format(CSV) where the first column is the x-axis(wavelength) and second column is y-axis(intensity count). The CSV should not have any headers. <br />
The CSV files are loaded by providing an absolute path in the 'Enter file path' box. A file explorer can be opened using the 'Browse' button to select the file/folder.
The results can be saved to a location by submitting an absolute path in the 'Save path' box. The file name must be terminated with '.csv' and may overwrite files if they have the same name. Auto-save can be turned on by checking the 'Auto-save' button. Saved files are formatted as CSV and will contain ratio information and relevant information extracted from the file name.
<br /><br />
Each spectrum file name is expected in the format: <br />  date_time_gas_pressure_flowrate_temperature_misc_misc.csv <br /> <br /> 
File name example: <br />
20220517_1705_H2_5,35PSIG_0,51SLM_77,7K_1_00000_counts.csv <br /> 
    * date = date the spectrum was taken <br />
    * time = time the spectrum was taken <br />
    * gas = gas present in the system during spectrum capture <br />
    * pressure = pressure of the gas at time of capture (including units) <br />
    * flowrate = flowrate at time of capture (including units) <br />
    * temperature = temperautre at the probe during capture (including units) <br />
    * misc = any additional relevant information <br />

### Visualize
Visualize will take a CSV spectrum and load it into a graph. The CSV must have no headers, the first column will be the x-axis(wavelength), and the second column will be the y-axis(intensity count). Multiple spectra can be displayed at a time and the display color of each individual spectrum can be set. <br />
The spectra are loaded by providing an absolute path in the 'Enter file path' box. This method can only load a single spectrum at a time. <br />

# Settings
The 'Apply' button must be clicked after making changes otherwise the changes will not be saved/used
### Integration Ranges
The integration ranges set the bandwidth that the spectrum is integrated over when calculating the integration ratios. <br />

### Baseline Correction
Baseline correction helps to remove background noise and signal interference. <br />
    * Disable baseline correction - No correction is used. <br />
    * Enable linear baseline correction - Generates a linear approximation of the baseline noise. This is based on the bandwidth range provided. <br />
    * Enable background subtraction - Subtracts a background spectrum containing no hydrogen from the hydrogen spectrum. This is dependant on the spectrum settings, most notable being the number of spectrum averages. A generic background spectra can be selected based on number of averages or a custom spectrum in CSV format may be submitted. The custom spectrum must have the same columns/axes and length as the hydrogen spectrum. <br />
