import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMenuBar, QMenu, QAction, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtWidgets
from Resources.FileSearchPage import FileSearchPage
from Resources.VisualizePage import VisualizePage
from Resources.CustomWidgets import SettingsWindow



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Ortho-Para Pal')
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'Resources\\Quantum Q Favicon.jpg')))
        self.setMinimumSize(800, 750)

        self.loadSettings()

        self.loadHelp()

        self.constructMenuBar()

        self.constructTabs()

    # Load settings from the json file 
    def loadSettings(self):
        with open(os.path.join(os.path.dirname(__file__), 'Resources\\settings.json'), 'r') as json_file:
            self.settings = json.load(json_file)
        
        # Create settings window
        self.SettingsWindow = SettingsWindow(settings=self.settings)
        self.SettingsWindow.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'Resources\\SettingsGear.png')))

    def loadHelp(self):
        with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as help_file:
            help_text = help_file.read()

        # Create help window
        self.HelpWindow = QTextEdit()
        self.HelpWindow.setWindowTitle('Help')
        self.HelpWindow.setMinimumSize(600, 600)
        self.HelpWindow.setReadOnly(True)
        self.HelpWindow.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'Resources\\HelpQuestionMark.png')))
        self.HelpWindow.setMarkdown(help_text)

    def constructMenuBar(self):
        # Create menu bar
        self.MenuBar = QMenuBar()
        self.setMenuBar(self.MenuBar)

        # Add settings to menu bar
        self.settingsAction = QAction('Settings')
        self.settingsAction.triggered.connect(self.SettingsWindow.showWindow)
        self.MenuBar.addAction(self.settingsAction)

        # Add help menu to menu bar
        self.helpAction = QAction('Help')
        self.helpAction.triggered.connect(self.HelpWindow.show)
        self.helpAction.triggered.connect(self.HelpWindow.activateWindow)
        self.MenuBar.addAction(self.helpAction)

    def constructTabs(self):
        # Initialize tab widget
        self.Tabs = QTabWidget()
        self.setCentralWidget(self.Tabs)

        # Initialize file searching page and functionality
        self.SearchTab = FileSearchPage(self.settings)
        self.SettingsWindow.ApplyButton.clicked.connect(self.SearchTab.settingsUpdated) # Signal for settings update
        self.Tabs.addTab(self.SearchTab, 'Ratio Finder')

        # Initialize visualization page and functionality
        self.VisualizePage = VisualizePage(self.settings)
        self.SettingsWindow.ApplyButton.clicked.connect(self.VisualizePage.settingsUpdated) # Signal for settings update
        self.Tabs.addTab(self.VisualizePage, 'Visualize')
    
    def closeEvent(self, e):
        self.SettingsWindow.close()
        return super().closeEvent(e)


if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec())