import sys
from PyQt5.QtWidgets import QApplication, QWidget, QCheckBox
from Resources.CustomWidgets import ErrorMessage, Page, SearchBar
import pandas as pd
import pyqtgraph as pg


class VisualizePage(Page):
    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        self.orthoRange = self.settings['orthoRange']
        self.paraRange = self.settings['paraRange']

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
        self.ortho_low = pg.InfiniteLine(pos=self.orthoRange[0], angle=90, pen='y')
        self.ortho_high = pg.InfiniteLine(pos=self.orthoRange[1], angle=90, pen='y')
        self.para_low = pg.InfiniteLine(pos=self.paraRange[0], angle=90, pen='r')
        self.para_high = pg.InfiniteLine(pos=self.paraRange[1], angle=90, pen='r')
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Widget = VisualizePage()
    Widget.show()
    sys.exit(app.exec())