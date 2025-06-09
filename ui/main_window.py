# ui/main_window.py
# Defines the main window for the ZoMailer application.

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget, QMessageBox
from PyQt6.QtCore import Qt, QUrl
# Import the necessary WebEngine widgets
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

from .settings_tab import SettingsTab

class MainWindow(QMainWindow):
    """
    The main application window, now with a tabbed interface and a web browser.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle('ZoMailer - Main Application')
        self.setGeometry(100, 100, 1024, 768)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        
        self.browser_tab_index = -1

        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout()
        welcome_label = QLabel('Welcome to ZoMailer Dashboard')
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        dashboard_layout.addWidget(welcome_label)
        dashboard_tab.setLayout(dashboard_layout)

        self.settings_tab = SettingsTab()

        self.tabs.addTab(dashboard_tab, "Dashboard")
        self.tabs.addTab(self.settings_tab, "Settings")

        self.statusBar().showMessage('Ready')

    def open_url_in_browser_tab(self, url_string: str):
        """Creates a new 'Browser' tab or focuses the existing one to load a URL."""
        if self.browser_tab_index != -1 and self.tabs.widget(self.browser_tab_index):
             browser_view = self.tabs.widget(self.browser_tab_index).findChild(QWebEngineView)
             browser_view.setUrl(QUrl(url_string))
             self.tabs.setCurrentIndex(self.browser_tab_index)
             return

        browser_view = QWebEngineView()
        
        # --- FIX STARTS HERE ---
        # 1. Create a persistent profile to store cookies and data.
        #    Using "storage" as a unique name ensures it's not an "off-the-record" profile.
        persistent_profile = QWebEngineProfile("storage", browser_view)

        # 2. Create a new QWebEnginePage with this profile.
        new_page = QWebEnginePage(persistent_profile, browser_view)
        
        # 3. Set this new, custom page on the view.
        browser_view.setPage(new_page)
        # --- FIX ENDS HERE ---
        
        browser_view.setUrl(QUrl(url_string))
        
        self.browser_tab_index = self.tabs.addTab(browser_view, "Browser")
        self.tabs.setCurrentWidget(browser_view)
        
        browser_view.loadFinished.connect(lambda _, index=self.browser_tab_index, view=browser_view: 
                                        self.tabs.setTabText(index, view.page().title()[:20]))

    def close_tab(self, index):
        """Handles the closing of a tab."""
        if index < 2:
            return
            
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)
        
        if index == self.browser_tab_index:
            self.browser_tab_index = -1

    def show_message(self, title: str, message: str, level: str = 'info'):
        """A helper method to show a popup message box from the main window."""
        if level == 'warning':
            QMessageBox.warning(self, title, message)
        elif level == 'critical':
        
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)