import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtWidgets
from Resources.FileSearchPage import FileSearchPage
from Resources.VisualizePage import VisualizePage


# TODO
# Moveable integration limits
# Load multiple spectra for graphing
#   - Need selection for which to display
# Database viewer
# Automation of SPC conversion
#   - Autoclicker for EFTIR


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Ortho-Para Pal')
        self.setWindowIcon(QIcon('Resources\\Quantum Q Favicon.jpg'))
        self.setMinimumSize(550, 500)

        self.constructTabs()
    
    def constructTabs(self):
        # Initialize tab widget
        self.Tabs = QTabWidget()
        self.setCentralWidget(self.Tabs)

        # Initialize file searching page and functionality
        self.SearchTab = FileSearchPage()
        self.Tabs.addTab(self.SearchTab, 'File Search')

        # Initialize visualization page and functionality
        self.VisualizePage = VisualizePage()
        self.Tabs.addTab(self.VisualizePage, 'Visualize')


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec())