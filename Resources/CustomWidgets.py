import os
import json
import typing
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QApplication, QMessageBox, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
                                QLabel, QLineEdit, QPushButton, QFileDialog, QTreeView, QColorDialog,
                                QCheckBox, QListWidget, QListWidgetItem)
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

        # Window settings
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'Resources\\SettingsGear.png')))
        self.setMinimumWidth(300)

        # Main layout for settings window
        self.MainLayout = QGridLayout()
        self.setLayout(self.MainLayout)

        # Input field for ortho range
        self.OrthoRange = RangeInputWidget('Ortho Range')
        self.MainLayout.addWidget(self.OrthoRange)

        # Input field for para range
        self.ParaRange = RangeInputWidget('Para Range')
        self.MainLayout.addWidget(self.ParaRange)

        # Input field for the baseline range
        self.BaselineRange = RangeInputWidget('Baseline range')
        self.MainLayout.addWidget(self.BaselineRange)

        # Enable/disable baseline correction
        self.EnableBaselineCorrection = QCheckBox('Enable baseline subtraction')
        self.MainLayout.addWidget(self.EnableBaselineCorrection)

        # Button to apply the settings 
        self.ApplyButton = QPushButton('Apply')
        self.ApplyButton.clicked.connect(self.settingsApply)
        self.MainLayout.addWidget(self.ApplyButton)

    def showWindow(self):
        # Populates fields with current settings
        self.OrthoRange.populateRange(self.settings['orthoRange'])
        self.ParaRange.populateRange(self.settings['paraRange'])
        self.BaselineRange.populateRange(self.settings['baselineRange'])
        self.EnableBaselineCorrection.setChecked(self.settings['enableBaselineCorrection'])

        # Show the settings window 
        self.show()
    
    def settingsApply(self):
        # Update settings in settings dictionary
        self.settings['orthoRange'] = self.OrthoRange.getRange()
        self.settings['paraRange'] = self.ParaRange.getRange()
        self.settings['baselineRange'] = self.BaselineRange.getRange()
        self.settings['enableBaselineCorrection'] = self.EnableBaselineCorrection.isChecked()

        # Write settings to the file
        with open(os.path.join(os.path.dirname(__file__), 'settings.json'), 'w+') as json_file:
            json.dump(self.settings, json_file)


class RangeInputWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        # Create main widget layout
        self.MainLayout = QVBoxLayout()
        self.setLayout(self.MainLayout)

        # Title for the widget
        self.TitleLabel = QLabel(title)
        font = self.TitleLabel.font()
        font.setBold(True)
        font.setPointSize(9)
        self.TitleLabel.setFont(font)
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
        print('added')
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
