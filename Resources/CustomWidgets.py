from PyQt5.QtWidgets import QMessageBox, QWidget, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from pandas.api.types import is_numeric_dtype
import pandas as pd



class ErrorMessage(QMessageBox):
    def __init__(self, text):
        super().__init__()
        self.setWindowTitle('Error')
        self.setText(text)
        self.setIcon(QMessageBox.Critical)
        self.exec_()


class SearchBar(QWidget):
    def __init__(self, label):
        super().__init__()

        self.Layout = QHBoxLayout()
        self.setLayout(self.Layout)

        self.Label = QLabel(label)
        self.Layout.addWidget(self.Label)

        self.InputField = QLineEdit()
        self.Layout.addWidget(self.InputField)

        self.SubmitButton = QPushButton('Submit')
        self.Layout.addWidget(self.SubmitButton)


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
        


