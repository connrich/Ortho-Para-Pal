import sys
from PyQt5.QtWidgets import QApplication, QWidget, QCheckBox, QGridLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QFont
from Resources.CustomWidgets import ErrorMessage, Page, SearchBar, GraphDisplayWidget
import pandas as pd
import pyqtgraph as pg


class VisualizePage(Page):
    def __init__(self, settings):
        super().__init__()

        # Global app settings
        self.settings = settings

        # Input field for loading file
        self.SearchBar = SearchBar('Enter file path: ')
        self.SearchBar.SubmitButton.clicked.connect(lambda: self.loadCSV(self.SearchBar.InputField.text()))
        self.PageLayout.addWidget(self.SearchBar)

        # Create graph widget
        self.Graph = pg.PlotWidget(title="Spectrum")
        # self.Graph.plotItem.setMouseEnabled(y=False)
        self.Graph.setLabel('bottom', 'Wavelength (1/cm)')
        self.Graph.setLabel('left', 'Intensity Count')
        self.PageLayout.addWidget(self.Graph, 2, 0)

        # Initialize toolbar
        self.initToolbar()

        # Vertical lines to show ortho and para ranges
        self.ortho_low = pg.InfiniteLine(pos=self.settings['orthoRange'][0], angle=90, pen='y')
        self.ortho_high = pg.InfiniteLine(pos=self.settings['orthoRange'][1], angle=90, pen='y')
        self.para_low = pg.InfiniteLine(pos=self.settings['paraRange'][0], angle=90, pen='r')
        self.para_high = pg.InfiniteLine(pos=self.settings['paraRange'][1], angle=90, pen='r')
        self.showOPRanges(True)
    
        # Create graph data widget
        self.GraphDisplay = GraphDisplayWidget(GraphDisplay=self.Graph)
        self.PageLayout.addWidget(self.GraphDisplay, 2, 1)

        self.PageLayout.setRowStretch(0 ,0)
        self.PageLayout.setRowStretch(1 ,0)
    
    # Initialize tool bar buttons
    def initToolbar(self):
        # Create toolbar layout
        self.ToolbarLayout = QHBoxLayout()
        self.PageLayout.addLayout(self.ToolbarLayout, 1, 0)

        # Checkbox to toggle the display of integration ranges 
        self.ShowRangeBtn = QCheckBox("Show integration ranges")
        self.ShowRangeBtn.setChecked(True)
        self.ShowRangeBtn.clicked.connect(lambda: self.showOPRanges(self.ShowRangeBtn.isChecked()))
        self.ToolbarLayout.addWidget(self.ShowRangeBtn)

        # Checkbox to toggle x-axis zooming
        self.LockX = QCheckBox("Lock X axis")
        self.LockX.clicked.connect(lambda: self.Graph.plotItem.setMouseEnabled(x=not self.LockX.isChecked()))
        self.LockX.clicked.connect(lambda: print(self.LockX.isChecked()))
        self.ToolbarLayout.addWidget(self.LockX)

        # Checkbox to toggle y-axis zooming
        self.LockY = QCheckBox("Lock Y axis")
        self.LockY.clicked.connect(lambda: self.Graph.plotItem.setMouseEnabled(y=not self.LockY.isChecked()))
        self.ToolbarLayout.addWidget(self.LockY)

    # Load a CSV from a path
    def loadCSV(self, file_path):
        df = pd.read_csv(file_path, header=None)

        # Uses class method to determine if the data frame is valid
        if self.isDFValid(df, error_msg=True):
            name = file_path.split('\\')[-1]
            plot_item = self.GraphDisplay.addDataset(self.Graph, df, file_path.split('\\')[-1])
            self.Graph.addItem(plot_item.PlotDataItem)
            return df
        else:
            return None

    # Show/hide the ranges for ortho and para
    def showOPRanges(self, show):
        if show:
            self.Graph.addItem(self.ortho_low)
            self.Graph.addItem(self.ortho_high)
            self.Graph.addItem(self.para_low)
            self.Graph.addItem(self.para_high)
        else:
            self.Graph.removeItem(self.ortho_low)
            self.Graph.removeItem(self.ortho_high)
            self.Graph.removeItem(self.para_low)
            self.Graph.removeItem(self.para_high)

    # Overloaded function for when settings are updated
    def settingsUpdated(self):
        self.ortho_low.setPos(self.settings['orthoRange'][0])
        self.ortho_high.setPos(self.settings['orthoRange'][1])
        self.para_low.setPos(self.settings['paraRange'][0])
        self.para_high.setPos(self.settings['paraRange'][1])


class SpectraWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.MainLayout = QGridLayout()
        self.setLayout(self.MainLayout)

        self.Title = QLabel('Spectra')
        font = QFont('Arial', 14)
        font.setBold(True)
        self.Title.setFont(font)
        self.MainLayout.addWidget(self.Title)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    Widget = VisualizePage()
    Widget.show()
    sys.exit(app.exec())