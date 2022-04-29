import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QApplication, QMessageBox, QWidget, QGridLayout, QHBoxLayout, 
                                QLabel, QLineEdit, QPushButton, QFileDialog, QTreeView)
from pandas.api.types import is_numeric_dtype
import pandas as pd
import sys



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
            self.FileBrowser.file_selected_signal.connect(self.SubmitButton.clicked.emit)

    
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
        

if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)

    test_widget = SearchBar('Enter path:')
    test_widget.show()

    sys.exit(app.exec())
