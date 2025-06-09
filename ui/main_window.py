# ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

# Import our new dashboard widget
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

    def on_load_finished(self, ok):
        """Called when a page finishes loading. Injects JS if it's the right page."""
        if not ok:
            return # Don't do anything if the page failed to load
            
        page = self.sender() # The QWebEnginePage that emitted the signal
        url = page.url().toString()

        # Only run the script on the specific sender preferences page
        if "/settings/emails/preference" in url:
            # <<< MODIFIED JAVASCRIPT WITH MORE PRECISE SELECTOR >>>
            js_code = """
                const selector = "p.font-xlarge.mb-5.ms-2 > b"; // Selector for the "Public Domains" bold tag
                
                const findElementInterval = setInterval(() => {
                    let targetElement = null;
                    // Find the bold tag that contains "Public Domains"
                    const titles = document.querySelectorAll(selector);
                    for (const title of titles) {
                        if (title.innerText.trim() === 'Public Domains') {
                            // Found it! Now get its parent container div.
                            targetElement = title.closest('div.row.p-5');
                            break;
                        }
                    }

                    if (targetElement) {
                        // Element found, stop polling
                        clearInterval(findElementInterval);
                        
                        // Style the body for a clean, dialog-like appearance
                        document.body.innerHTML = ''; // Erase everything
                        document.body.style.backgroundColor = '#f0f2f5';
                        document.body.style.display = 'flex';
                        document.body.style.justifyContent = 'center';
                        document.body.style.alignItems = 'flex-start';
                        document.body.style.paddingTop = '40px';
                        document.body.style.height = '100vh';

                        // Style the isolated element to look modern
                        targetElement.style.width = '90%';
                        targetElement.style.maxWidth = '800px';
                        targetElement.style.backgroundColor = 'white';
                        targetElement.style.border = '1px solid #dee2e6';
                        targetElement.style.borderRadius = '8px';
                        targetElement.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
                        targetElement.style.marginTop = '0'; // Reset margin

                        // Append only our target element back to the now-empty body
                        document.body.appendChild(targetElement);
                    }
                }, 200); // Check every 200 milliseconds

                // Add a timeout to stop polling after 7 seconds
                setTimeout(() => {
                    clearInterval(findElementInterval);
                }, 7000);
            """
            page.runJavaScript(js_code)

    def open_url_in_browser_tab(self, url_string: str):
        if self.browser_view and self.browser_view.parent() is not None:
             # If a browser tab is already open, just set its URL
             self.browser_view.setUrl(QUrl(url_string))
             self.tabs.setCurrentWidget(self.browser_view.parent())
             return

        self.browser_view = QWebEngineView()
        persistent_profile = QWebEngineProfile("storage", self.browser_view)
        new_page = QWebEnginePage(persistent_profile, self.browser_view)

        new_page.loadFinished.connect(self.on_load_finished)

        self.browser_view.setPage(new_page)
        self.browser_view.page().urlChanged.connect(self.on_url_changed)
        self.browser_view.setUrl(QUrl(url_string))
        
        # Determine the tab title based on the URL
        tab_title = "Browser"
        if "accounts.zoho.com" in url_string:
            tab_title = "Authorization"
        elif "/settings/emails/preference" in url_string:
            tab_title = "Sender Settings"

        browser_tab = QWidget()
        layout = QVBoxLayout(browser_tab)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.browser_view)
        
        index = self.tabs.addTab(browser_tab, tab_title)
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        # Prevent closing the main Dashboard and Settings tabs
        if index < 2: 
            return
            
        widget = self.tabs.widget(index)
        if widget:
            # Important: clear our reference to the browser view if we are closing it
            if self.browser_view and widget == self.browser_view.parent():
                self.browser_view = None
            widget.deleteLater()
            
        self.tabs.removeTab(index)

    def show_message(self, title: str, message: str, level: str = 'info'):
        if level == 'warning': QMessageBox.warning(self, title, message)
        elif level == 'critical': QMessageBox.critical(self, title, message)
        else: QMessageBox.information(self, title, message)
