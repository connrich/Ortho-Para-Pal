import sys
from PyQt5.QtWidgets import QApplication, QWidget, QCheckBox
from Resources.CustomWidgets import ErrorMessage, Page, SearchBar
import pandas as pd
import pyqtgraph as pg


class VisualizePage(Page):
    def __init__(self):
        super().__init__()

        self.orthoRange = [580, 595]
        self.paraRange = [347, 365]

        self.SearchBar = SearchBar('Enter file path: ')
        self.SearchBar.SubmitButton.clicked.connect(lambda: self.loadCSV(self.SearchBar.InputField.text()))
        self.PageLayout.addWidget(self.SearchBar)

        # Button to toggle the ranges 
        self.ShowRangeBtn = QCheckBox("Show ranges")
        self.ShowRangeBtn.setChecked(True)
        self.ShowRangeBtn.clicked.connect(lambda: self.showOPRanges(self.ShowRangeBtn.isChecked()))
        self.PageLayout.addWidget(self.ShowRangeBtn)

        # Create graph widget
        self.Graph = pg.PlotWidget(title="Spectrum")
        self.Graph.plotItem.setMouseEnabled(y=False)
        self.Graph.setLabel('bottom', 'Wavelength (1/cm)')
        self.Graph.setLabel('left', 'Intensity Count')
        self.PageLayout.addWidget(self.Graph)

        # Vertical lines to show ortho and para ranges
        self.ortho_low = pg.InfiniteLine(pos=self.orthoRange[0], angle=90, pen='y', movable=True)
        self.ortho_high = pg.InfiniteLine(pos=self.orthoRange[1], angle=90, pen='y', movable=True)
        self.para_low = pg.InfiniteLine(pos=self.paraRange[0], angle=90, pen='r', movable=True)
        self.para_high = pg.InfiniteLine(pos=self.paraRange[1], angle=90, pen='r', movable=True)
        self.showOPRanges(True)
    
    def loadCSV(self, file_path):
        df = pd.read_csv(file_path, header=None)

        if self.isDFValid(df, error_msg=True):
            self.Graph.clear()
            self.showOPRanges(True)
            self.Graph.plot(df[0], df[1])
            return df
        else:
            return None

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Widget = VisualizePage()
    Widget.show()
    sys.exit(app.exec())