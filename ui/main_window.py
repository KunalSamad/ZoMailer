# ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget, QMessageBox
from PyQt6.QtCore import Qt, QUrl, pyqtSignal # Import pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

from .settings_tab import SettingsTab

class MainWindow(QMainWindow):
    # --- New Signal ---
    # This signal will be emitted when the redirect URL with the grant code is detected.
    redirect_url_intercepted = pyqtSignal(QUrl)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('ZoMailer - Main Application')
        self.setGeometry(100, 100, 1024, 768)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        self.browser_view = None # Keep a reference to the browser view

        # ... (rest of __init__ is the same: dashboard_tab, settings_tab, addTab calls, statusBar) ...
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
        if self.browser_view and self.browser_view.parent() is not None:
             self.browser_view.setUrl(QUrl(url_string))
             self.tabs.setCurrentWidget(self.browser_view.parent())
             return

        self.browser_view = QWebEngineView()
        persistent_profile = QWebEngineProfile("storage", self.browser_view)
        new_page = QWebEnginePage(persistent_profile, self.browser_view)
        self.browser_view.setPage(new_page)
        
        # --- Connect urlChanged signal ---
        self.browser_view.page().urlChanged.connect(self.on_url_changed)
        
        self.browser_view.setUrl(QUrl(url_string))
        
        browser_tab = QWidget() # A container widget for the browser
        layout = QVBoxLayout(browser_tab)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.browser_view)
        
        index = self.tabs.addTab(browser_tab, "Authorization")
        self.tabs.setCurrentIndex(index)
        
    def on_url_changed(self, url: QUrl):
        """Monitors URL changes to find the grant token."""
        from config import settings # Local import
        if url.toString().startswith(settings.REDIRECT_URI):
            self.redirect_url_intercepted.emit(url)
            # Find and close the authorization tab
            for i in range(self.tabs.count()):
                if self.tabs.widget(i) == self.browser_view.parent():
                    self.close_tab(i)
                    break

    def close_tab(self, index):
        if index < 2: return
        widget = self.tabs.widget(index)
        if widget and self.browser_view and widget == self.browser_view.parent():
            self.browser_view = None # Clear reference
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)

    def show_message(self, title: str, message: str, level: str = 'info'):
        # ... (show_message method is the same) ...
        if level == 'warning': QMessageBox.warning(self, title, message)
        elif level == 'critical': QMessageBox.critical(self, title, message)
        else: QMessageBox.information(self, title, message)