import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QWidget, QApplication, QGridLayout, QLabel, 
                             QLineEdit, QPushButton, QHBoxLayout, QTreeView, QRadioButton)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import Qt
from Resources.CustomWidgets import ErrorMessage, Page, SearchBar
# from CustomWidgets import ErrorMessage, Page, SearchBar

from Resources.RatioFinder import RatioFinder



class FileSearchPage(Page):
    def __init__(self):
        super().__init__()
        # self.PageLayout = QGridLayout()
        # self.setLayout(self.PageLayout)

        self.SearchBar = SearchBar('Enter file path: ')
        self.SearchBar.SubmitButton.clicked.connect(self.gatherRatios)
        self.PageLayout.addWidget(self.SearchBar)

        # Input field for saving the data to a CSV
        self.DatabaseInputLayout = QHBoxLayout()
        self.DatabaseInputLayout.addWidget(QLabel("   Database Path:"))
        self.DBLocation = QLineEdit()
        self.DatabaseInputLayout.addWidget(self.DBLocation)
        self.DBAppendBtn = QRadioButton('Append to db')
        self.DatabaseInputLayout.addWidget(self.DBAppendBtn)
        self.PageLayout.addLayout(self.DatabaseInputLayout, 1, 0, Qt.AlignRight | Qt.AlignTop)

        # Viewng window for the generated tree
        self.TreeViewer = QTreeView()
        self.TreeViewer.setHeaderHidden(True)
        self.PageLayout.addWidget(self.TreeViewer)

        # Setup for displaying results in tree view
        self.TreeModel = QStandardItemModel(0, 2)
        self.TreeViewer.setModel(self.TreeModel)
    
        # Parses submitted path
    def gatherRatios(self):
        # Get file path from line edit
        path = self.SearchBar.InputField.text()

        # Check if path is valid 
        if os.path.exists(path):
            # Determine if object is file or folder
            if os.path.isdir(path):
                # Iterate through all files in the folder
                results = []
                found_valid_file = False
                for file_name in os.listdir(path):
                    # Check if the file is a CSV
                    if file_name.split('.')[-1] == 'csv':
                        results.append(self.getRatio(os.path.join(path, file_name)))
                        found_valid_file = True
                
                if not found_valid_file:
                    ErrorMessage('Could not find a valid CSV file.')
                    return
                    
            elif os.path.isfile(path):
                # Check if the file is a CSV
                if path.split('.')[-1] == 'csv':
                    results = [self.getRatio(path)]
                else:
                    ErrorMessage('Error: Wrong file type. Only accepts CSV format or a folder containing CSV.')
                    return
            
            self.displayResults(results)

    # Called when file path is submitted 
    def getRatio(self, path):  
        # Check if path is valid
        if path != '' and os.path.exists(path) and path.split('.')[-1] == 'csv':
            # Get ratio results
            return RatioFinder(path)          

    # Takes dictionary as argument and displays key/value pairs 
    def displayResults(self, results):
        # Reset tree model
        self.TreeModel.clear()
        self.TreeModel.setColumnCount(2)
        rootNode = self.TreeModel.invisibleRootItem()

        for result in results:
            # Append to database if selected
            if self.DBAppendBtn.isChecked():
                self.addResultToDB(result) 

            # Create branch with file name 
            file_branch = QStandardItem()
            file_branch.setEditable(False)
            file_branch.setText(result.pop('Filename'))
            if 'Error' in result:
                file_branch.setForeground(QColor(255,0,0))
            rootNode.appendRow(file_branch)

            # Populate the file branch
            labels = []
            values = []
            # Generate a column of data labels and a column of corresponding values 
            for row, key in enumerate(result):
                label_item = QStandardItem()
                label_item.setEditable(False)
                label_item.setText(key)
                labels.append(label_item)

                value_item = QStandardItem()
                value_item.setEditable(False)
                value_item.setText(str(result[key]))
                values.append(value_item)

            file_branch.appendColumn(labels)
            file_branch.appendColumn(values)

            self.TreeViewer.setModel(self.TreeModel)
            self.TreeViewer.resizeColumnToContents(0) 

    # Append to CSV database
    def addResultToDB(self, result):
        # Check if result is an error
        if 'Error' in result:
            return

        # Take file name from path 
        result['Filename'] = result['Filename'].split('\\')[-1]

        # Append additional result fields
        name = result['Filename'].split('_')[1:5]
        result['Gas'] = name.pop(0)
        pressure = self.splitUnits(name.pop(0))
        result[f'Pressure ({pressure[1]})'] = pressure[0]
        flow = self.splitUnits(name.pop(0))
        result[f'Flow ({flow[1]})'] = flow[0]
        temp = self.splitUnits(name.pop(0))
        result[f'Temperature ({temp[1]})'] = temp[0]

        # Create dataframe from result dictionary
        result_df = pd.DataFrame.from_dict([result])

        # Path provided in text input box
        db_path = self.DBLocation.text()
        # Validate the provided database path 
        if os.path.exists(db_path):
            if db_path.split('.')[-1] == 'csv':
                # Check if the CSV is empty
                try:
                    db_df = pd.read_csv(db_path)
                    # Check if file is already save to database
                    if result['Filename'] not in db_df['Filename'].values:
                        # Append result to database
                        df = pd.concat([db_df, result_df])
                        # Save new dataframe to database CSV
                        df.to_csv(db_path, index=False)
                # Exception for exmpty CSV
                except pd.errors.EmptyDataError:
                    result_df.to_csv(db_path, index=False)
                    print('excepted')
        # File does not currently exist
        else:
            result_df.to_csv(db_path, index=False)
    
    def splitUnits(self, value):
        for idx, i in enumerate(value):
            if i.isalpha():
                break
        return [value[:idx], value[idx:]]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Widget = FileSearchPage()
    Widget.show()
    sys.exit(app.exec())