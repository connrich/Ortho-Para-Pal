import os
import json
import typing
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QApplication, QMessageBox, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
                                QLabel, QLineEdit, QPushButton, QFileDialog, QTreeView, QColorDialog,
                                QCheckBox, QListWidget, QListWidgetItem, QButtonGroup, QRadioButton)
from PyQt5.QtGui import QFont, QIcon
from pandas.api.types import is_numeric_dtype
import pandas as pd
import pyqtgraph as pg
import sys
import random
import typing



class ErrorMessage(QMessageBox):
    def __init__(self, text):
        super().__init__()
        self.setWindowTitle('Error')
        self.setText(text)
        self.setIcon(QMessageBox.Critical)
        self.exec_()


class SearchBar(QWidget):
    def __init__(self, label, file_browse=True):
        super().__init__()

        # Main layout for widget
        self.Layout = QHBoxLayout()
        self.setLayout(self.Layout)

        # Label for specify which data should be entered
        self.Label = QLabel(label)
        self.Layout.addWidget(self.Label)

        # Input field for user
        self.InputField = QLineEdit()
        self.Layout.addWidget(self.InputField)

        # Submit the data
        self.SubmitButton = QPushButton('Submit')
        self.Layout.addWidget(self.SubmitButton)

        if file_browse:
            # Button to open file browser
            self.BrowseButton = QPushButton('Browse')
            self.BrowseButton.clicked.connect(self.openFileBrowser)
            self.Layout.addWidget(self.BrowseButton)

            # Save previous file location
            self.prev_file_loc = 'c:\\'

            # Create QFileDialog
            self.FileBrowser = FileDialog()
            self.FileBrowser.file_selected_signal.connect(self.populateInput)
            self.FileBrowser.file_selected_signal.connect(self.SubmitButton.click)
    
    def openFileBrowser(self):
        self.FileBrowser.show()
    
    def populateInput(self):
        self.InputField.setText(self.FileBrowser.selectedFiles[0])
        

class FileDialog(QFileDialog):
    file_selected_signal = QtCore.pyqtSignal()

    def __init__(self, *args):
        QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.ExistingFiles)
        btns = self.findChildren(QPushButton)
        self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
        self.openBtn.clicked.disconnect()
        self.openBtn.clicked.connect(self.openClicked)
        self.tree = self.findChild(QTreeView)

    def openClicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in inds:
            if i.column() == 0:
                files.append(os.path.join(str(self.directory().absolutePath()),str(i.data())))
        self.selectedFiles = files
        self.file_selected_signal.emit()
        self.hide()

    def filesSelected(self):
        return self.selectedFiles


class Page(QWidget):
    def __init__(self):
        super().__init__()

        self.PageLayout = QGridLayout()
        self.setLayout(self.PageLayout)
    
    # Validates if the data frame has the correct formatting
    def isDFValid(self, df, error_msg=False):
        if len(df.columns) != 2:
            if error_msg:
                ErrorMessage('Invalid CSV. Wrong number of columns. Expects 2 columns: 1st is wavelength(1/cm) and second is intensity count.')
            return False
        if not is_numeric_dtype(df[0]) or not is_numeric_dtype(df[1]):
            if error_msg:
                ErrorMessage('Encountered wrong datatype in CSV. Expects floats or integers. It also expects no column header names.')
            return False
        
        return True
    
    # Function to be called when settings are updated 
    def settingsUpdated(self):
        pass
        

class SettingsWindow(QWidget):
    def __init__(self, settings):
        super().__init__()

        # Global app settings
        self.settings = settings

        # Fonts for settings
        self.TitleFont = QFont()
        self.TitleFont.setBold(True)
        self.TitleFont.setPointSize(9)

        # Window settings
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'Resources\\SettingsGear.png')))
        self.setMinimumWidth(300)

        # Main layout for settings window
        self.MainLayout = QGridLayout()
        self.setLayout(self.MainLayout)

        # Title for intergration ranges
        self.RangeTitle = QLabel('Integration Ranges')
        self.RangeTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.RangeTitle.setFont(self.TitleFont)
        self.MainLayout.addWidget(self.RangeTitle)

        # Input field for ortho range
        self.OrthoRange = RangeInputWidget('Ortho Range')
        self.MainLayout.addWidget(self.OrthoRange)

        # Input field for para range
        self.ParaRange = RangeInputWidget('Para Range')
        self.MainLayout.addWidget(self.ParaRange)

        # Title label for corrections
        self.CorrectionLabel = QLabel('Baseline Correction')
        self.CorrectionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.CorrectionLabel.setFont(self.TitleFont)
        self.MainLayout.addWidget(self.CorrectionLabel)

        # Group for making baseline correction options mutually exclusive
        # Button id 0 = Disabled
        # Button id 1 = Linear approximation
        # Button id 2 = Background subtraction
        self.BaselineCorrectionOptions = QButtonGroup()
        self.BaselineCorrectionOptions.setExclusive(True)

        # Enable/disable baseline correction
        self.DisableBaselineCorrection = QCheckBox('Disable baseline correction')
        self.BaselineCorrectionOptions.addButton(self.DisableBaselineCorrection)
        self.BaselineCorrectionOptions.setId(self.DisableBaselineCorrection, 0)
        self.MainLayout.addWidget(self.DisableBaselineCorrection)

        # Enable/disable linear approximation baseline correction
        self.EnableLinearCorrection = QCheckBox('Enable linear baseline correction')
        self.BaselineCorrectionOptions.addButton(self.EnableLinearCorrection)
        self.BaselineCorrectionOptions.setId(self.EnableLinearCorrection, 1)
        self.MainLayout.addWidget(self.EnableLinearCorrection)

        # Input field for the baseline range
        self.LinearBaselineRange = RangeInputWidget('Linear baseline correction range')
        self.MainLayout.addWidget(self.LinearBaselineRange)

        # Enable/disable background subtraction
        self.EnableBackgroundSubtraction = QCheckBox('Enable background subtraction')
        self.BaselineCorrectionOptions.addButton(self.EnableBackgroundSubtraction)
        self.BaselineCorrectionOptions.setId(self.EnableBackgroundSubtraction, 2)
        self.MainLayout.addWidget(self.EnableBackgroundSubtraction)

        # Mutually exclusive options for background subtraction 
        # Button id is equal to the number of averages
        # Custom background has button id = 0
        self.BackgroundSubtractionOptions = QHBoxLayout()
        self.AverageSelection = QButtonGroup()
        self.AverageSelection.setExclusive(True)
        self.avg20 = QRadioButton('20 avg.')
        self.AverageSelection.addButton(self.avg20)
        self.AverageSelection.setId(self.avg20, 20)
        self.BackgroundSubtractionOptions.addWidget(self.avg20)
        self.avg30 = QRadioButton('30 avg.')
        self.AverageSelection.addButton(self.avg30)
        self.AverageSelection.setId(self.avg30, 30)
        self.BackgroundSubtractionOptions.addWidget(self.avg30)
        self.avg50 = QRadioButton('50 avg.')
        self.AverageSelection.addButton(self.avg50)
        self.AverageSelection.setId(self.avg50, 50)
        self.BackgroundSubtractionOptions.addWidget(self.avg50)
        self.CustomBackground = QRadioButton('Custom')
        self.AverageSelection.addButton(self.CustomBackground)
        self.AverageSelection.setId(self.CustomBackground, 0)
        self.BackgroundSubtractionOptions.addWidget(self.CustomBackground)
        self.MainLayout.addLayout(self.BackgroundSubtractionOptions, 8, 0)
        self.AverageSelection.idToggled.connect(self.backgroundSelectionChanged)

        # Line edit for pasting path to custom background spectrum
        self.CustomBackgroundPath = QLineEdit('Enter path for custom background spectrum')
        self.CustomBackgroundPath.setDisabled(True)
        self.MainLayout.addWidget(self.CustomBackgroundPath)

        # Button to apply the settings 
        self.ApplyButton = QPushButton('Apply')
        self.ApplyButton.clicked.connect(self.settingsApply)
        self.MainLayout.addWidget(self.ApplyButton)

    # Populates fields with current settings
    def showWindow(self):
        # Integration ranges for ortho and para bands
        self.OrthoRange.populateRange(self.settings['orthoRange'])
        self.ParaRange.populateRange(self.settings['paraRange'])

        # Baseline correction settings
        self.BaselineCorrectionOptions.button(self.settings['enableBaselineCorrection']).setChecked(True)
        self.LinearBaselineRange.populateRange(self.settings['linearBaselineRange'])
        self.AverageSelection.button(self.settings['backgroundSubtractionAverages']).setChecked(True)

        # Show the settings window 
        self.show()
    
    # Update settings in settings dictionary
    def settingsApply(self):
        # Save settings for ortho and para integration ranges
        self.settings['orthoRange'] = self.OrthoRange.getRange()
        self.settings['paraRange'] = self.ParaRange.getRange()

        # Save settings for baseline correction
        self.settings['enableBaselineCorrection'] = self.BaselineCorrectionOptions.checkedId()
        self.settings['linearBaselineRange'] = self.LinearBaselineRange.getRange()
        self.settings['backgroundSubtractionAverages'] = self.AverageSelection.checkedId()
        self.settings['customSubtractionBackground'] = self.CustomBackgroundPath.text()

        # Write settings to the settings file
        with open(os.path.join(os.path.dirname(__file__), 'settings.json'), 'w+') as json_file:
            json.dump(self.settings, json_file)

    # Slot to enable input for custom background subtraction path
    # Only enabled when custom is selected
    def backgroundSelectionChanged(self, id, checked):
        if id == 0 and checked == True:
            self.CustomBackgroundPath.setEnabled(True)
        else:
            self.CustomBackgroundPath.setEnabled(False)


# Widget for inputting and storing upper and lower limits
class RangeInputWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        # Create main widget layout
        self.MainLayout = QVBoxLayout()
        self.setLayout(self.MainLayout)

        # Title for the widget
        self.TitleLabel = QLabel(title)
        self.TitleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.MainLayout.addWidget(self.TitleLabel)

        # Input boxes for low and high range 
        self.InputLayout = QHBoxLayout()
        self.MainLayout.addLayout(self.InputLayout)
        self.LowInput = QLineEdit()
        self.LowInput.setMaximumWidth(60)
        self.InputLayout.addWidget(self.LowInput)
        self.HighInput = QLineEdit()
        self.HighInput.setMaximumWidth(60)
        self.InputLayout.addWidget(self.HighInput)
    
    def getRange(self):
        return [float(self.LowInput.text()), float(self.HighInput.text())]
    
    def populateRange(self, rnge):
        self.LowInput.setText(str(rnge[0]))
        self.HighInput.setText(str(rnge[1]))


class GraphDisplayWidget(QWidget):
    def __init__(self, GraphDisplay=None, title='Graph Properties'):
        super().__init__()

        # Widget size settings
        self.setMaximumWidth(400)

        # Layout of the widget
        self.Layout = QVBoxLayout()
        self.Layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.Layout.setSpacing(1)
        self.setLayout(self.Layout)

        # Displayed widget title
        self.title = title
        self.TitleLabel = QLabel(self.title)
        self.TitleLabel.setFixedHeight(40)
        self.TitleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.Layout.addWidget(self.TitleLabel)

        # Layout for various data items
        self.DataItems = QVBoxLayout()
        self.Layout.addLayout(self.DataItems)

        # Graph for display the data
        self.GraphDisplay = GraphDisplay

    def addDataset(self, parent_graph, df, name, color=None):
        item = DataItem(self, parent_graph, df, name, color)
        self.DataItems.addLayout(item)
        return item
    
    def removeDataset(self, DataItem):
        self.DataItems.removeItem(DataItem)
    
    
class DataItem(QHBoxLayout):
    def __init__(self, parent, parent_graph, data, name, color=None):
        super().__init__()

        # Parent GraphSettingWidget
        self.parent = parent

        # Graphwidget where this data is displayed
        self.parent_graph = parent_graph

        # Plot item used to display data on graph
        self.PlotDataItem = pg.PlotDataItem(data[0], data[1], pen=pg.mkPen())

        # Set the name of the data
        self.name = name
        self.NameLabel = QLabel(name)
        self.addWidget(self.NameLabel) 
        
        # Set the color for display
        self.ColorButton = QPushButton()
        self.ColorButton.setFixedWidth(28)
        self.ColorButton.clicked.connect(self.changeColor)
        self.addWidget(self.ColorButton)
        if color is None:
            self.setColor((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        else:
            self.setColor(color)
        
        # Button for deleting the data
        self.DeleteButton = QPushButton()
        self.DeleteButton.setText('X')
        self.DeleteButton.setFixedWidth(28)
        self.DeleteButton.clicked.connect(self.delete)
        self.DeleteButton.clicked.connect(self.DeleteButton.deleteLater)
        self.addWidget(self.DeleteButton)

        self.setContentsMargins(0, 0, 0, 0)
    
    def setName(self, name: str) -> None:
        self.name = name
        self.NameLabel.setText(self.name)
    
    def setColor(self, color: tuple) -> None:
        r, g, b = color
        self.ColorButton.setStyleSheet(f"QPushButton {{ background-color: rgb({r}, {g}, {b});}};") 
        self.PlotDataItem.setPen(pg.mkPen(color))
    
    def changeColor(self):
        color = QColorDialog.getColor()
        if color is not None:
            self.setColor((color.red(), color.green(), color.blue()))

    def delete(self) -> None:
        self.parent.removeDataset(self)
        self.parent_graph.removeItem(self.PlotDataItem)
        for i in reversed(range(self.count())):
            self.itemAt(i).widget().deleteLater()
        self.deleteLater()

            

if __name__ == '__main__':
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)

    test_widget = GraphDisplayWidget()
    test_widget.show()

    sys.exit(app.exec())
