# ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

from .dashboard_widget import DashboardWidget
from .settings_tab import SettingsTab

class MainWindow(QMainWindow):
    redirect_url_intercepted = pyqtSignal(QUrl)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('ZoMailer - Main Application')
        self.setGeometry(100, 100, 1024, 768)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.browser_view = None

        self.dashboard_widget = DashboardWidget()
        self.settings_tab = SettingsTab()
        
        self.tabs.addTab(self.dashboard_widget, "Dashboard")
        self.tabs.addTab(self.settings_tab, "Settings")
        
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.statusBar().showMessage('Ready')
    
    def on_url_changed(self, url: QUrl):
        from config import settings
        if url.toString().startswith(settings.REDIRECT_URI):
            self.redirect_url_intercepted.emit(url)
            for i in range(self.tabs.count()):
                if self.browser_view and self.tabs.widget(i) == self.browser_view.parent():
                    self.close_tab(i)
                    break

    # <<< RE-INTRODUCED 'on_load_finished' with new JavaScript >>>
    def on_load_finished(self, ok):
        """Called when a page finishes loading. Injects JS if it's the right page."""
        if not ok:
            return 
            
        page = self.sender()
        url = page.url().toString()

        # Only run the script on the specific email template editor page
        if "/settings/emails/templates/edit" in url:
            # This JS tries to find the main content editor of the template page.
            # Selectors are based on educated guesses and may need tweaking if Zoho
            # changes its web page structure.
            js_code = """
                const selector = "div.email-template-edit-page"; // A likely container for the editor
                
                const findElementInterval = setInterval(() => {
                    const targetElement = document.querySelector(selector);

                    if (targetElement) {
                        // Element found, stop polling
                        clearInterval(findElementInterval);
                        
                        // Style the body for a clean, dialog-like appearance
                        document.body.innerHTML = ''; 
                        document.body.style.backgroundColor = '#f0f2f5';
                        document.body.style.display = 'flex';
                        document.body.style.justifyContent = 'center';
                        document.body.style.alignItems = 'flex-start';
                        document.body.style.padding = '20px';
                        document.body.style.height = '100vh';
                        document.body.style.overflow = 'auto';

                        // Style the isolated element to look modern
                        targetElement.style.width = '100%';
                        targetElement.style.maxWidth = '1200px';
                        targetElement.style.margin = '0';

                        // Append only our target element back to the now-empty body
                        document.body.appendChild(targetElement);
                    }
                }, 200); // Check every 200 milliseconds

                // Add a timeout to stop polling after 10 seconds
                setTimeout(() => {
                    clearInterval(findElementInterval);
                }, 10000);
            """
            page.runJavaScript(js_code)

    def open_url_in_browser_tab(self, url_string: str):
        if self.browser_view and self.browser_view.parent() is not None:
             self.browser_view.setUrl(QUrl(url_string))
             self.tabs.setCurrentWidget(self.browser_view.parent())
             return

        self.browser_view = QWebEngineView()
        persistent_profile = QWebEngineProfile("storage", self.browser_view)
        new_page = QWebEnginePage(persistent_profile, self.browser_view)

        # <<< RE-INTRODUCED the connection to on_load_finished >>>
        new_page.loadFinished.connect(self.on_load_finished)

        self.browser_view.setPage(new_page)
        self.browser_view.page().urlChanged.connect(self.on_url_changed)
        self.browser_view.setUrl(QUrl(url_string))
        
        tab_title = "Browser"
        if "accounts.zoho.com" in url_string:
            tab_title = "Authorization"
        elif "/settings/emails/preference" in url_string:
            tab_title = "Sender Settings"
        # <<< NEW: Set title for the template editor tab >>>
        elif "/settings/emails/templates/edit" in url_string:
            tab_title = "Template Editor"


        browser_tab = QWidget()
        layout = QVBoxLayout(browser_tab)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.browser_view)
        
        index = self.tabs.addTab(browser_tab, tab_title)
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        if index < 2: 
            return
            
        widget = self.tabs.widget(index)
        if widget:
            if self.browser_view and widget == self.browser_view.parent():
                self.browser_view = None
            widget.deleteLater()
            
        self.tabs.removeTab(index)

    def show_message(self, title: str, message: str, level: str = 'info'):
        if level == 'warning': QMessageBox.warning(self, title, message)
        elif level == 'critical': QMessageBox.critical(self, title, message)
        else: QMessageBox.information(self, title, message)