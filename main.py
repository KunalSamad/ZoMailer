# main.py
# The primary entry point for the ZoMailer application.

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow
from ui.settings_tab import SettingsTab # Import SettingsTab to access its constants
from core.config_manager import ConfigManager

ZOHO_API_CONSOLE_URL = "https://api-console.zoho.com/"

class AppController:
    """The main controller, now with save confirmation."""
    def __init__(self):
        self.config_manager = ConfigManager()
        self.view = MainWindow()

        # Connect UI signals to controller slots
        settings_ui = self.view.settings_tab
        settings_ui.save_button.clicked.connect(self.handle_save_action)
        settings_ui.api_console_button.clicked.connect(self.handle_open_zoho_console)
        settings_ui.add_new_button.clicked.connect(self.prepare_for_add_new)
        settings_ui.delete_button.clicked.connect(self.handle_delete_account)
        settings_ui.account_selector.currentIndexChanged.connect(self.handle_account_selection_changed)
        
        self.refresh_account_list()

    def run(self):
        self.view.show()

    def refresh_account_list(self, select_index: int = None):
        """Discovers real accounts and updates the UI."""
        accounts = self.config_manager.discover_credentials()
        self.view.settings_tab.account_selector.blockSignals(True)
        self.view.settings_tab.populate_account_list(accounts)
        
        if select_index:
            list_index = self.view.settings_tab.account_selector.findData(select_index)
            self.view.settings_tab.account_selector.setCurrentIndex(list_index)
        elif len(accounts) > 0:
            self.view.settings_tab.account_selector.setCurrentIndex(0)
        
        self.view.settings_tab.account_selector.blockSignals(False)
        self.handle_account_selection_changed()

    def prepare_for_add_new(self):
        """Activates the 'unsaved account' mode in the UI."""
        self.view.settings_tab.set_unsaved_account_mode()
        self.view.statusBar().showMessage("Enter new credential details and click 'Save Changes'.")

    def handle_account_selection_changed(self):
        """Loads data for the selected account."""
        index = self.view.settings_tab.get_selected_account_index()
        
        if index == SettingsTab.UNSAVED_ACCOUNT_PLACEHOLDER_DATA:
            self.view.settings_tab.set_credentials("", "")
            return
            
        if index is None:
            return
        
        credentials = self.config_manager.load_credentials(index)
        self.view.settings_tab.set_credentials(
            credentials.get("client_id"), credentials.get("client_secret")
        )
        self.view.statusBar().showMessage(f"Editing Account {index}")

    def handle_save_action(self):
        """Saves a new account or updates an existing one based on selection."""
        index = self.view.settings_tab.get_selected_account_index()
        client_id, client_secret = self.view.settings_tab.get_credentials()

        if not client_id or not client_secret:
            self.view.show_message("Input Error", "Client ID and Client Secret cannot be empty.", level='warning')
            return

        try:
            if index == SettingsTab.UNSAVED_ACCOUNT_PLACEHOLDER_DATA:
                # We are saving a NEW account, no confirmation needed.
                new_index = self.config_manager.add_new_credentials(client_id, client_secret)
                self.view.show_message("Success", f"Successfully created Account {new_index}.")
                self.refresh_account_list(select_index=new_index)
            elif index is not None and index > 0:
                # We are updating an EXISTING account. Ask for confirmation first.
                # --- FIX STARTS HERE ---
                reply = QMessageBox.question(
                    self.view,
                    "Confirm Overwrite",
                    f"Are you sure you want to overwrite the saved credentials for Account {index}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No  # Default button
                )

                if reply == QMessageBox.StandardButton.No:
                    self.view.statusBar().showMessage("Save operation cancelled.")
                    return  # Abort the save
                # --- FIX ENDS HERE ---
                
                # If user clicked Yes, proceed with saving.
                self.config_manager.save_credentials(index, client_id, client_secret)
                self.view.show_message("Success", f"Changes to Account {index} have been saved.")
            else:
                self.view.show_message("Save Error", "No account is selected.", level='warning')
        except Exception as e:
            self.view.show_message("Error", f"Could not save changes: {e}", level='critical')
    
    def handle_delete_account(self):
        """Deletes the currently selected account after confirmation."""
        index = self.view.settings_tab.get_selected_account_index()
        if index is None or index <= 0:
            self.view.show_message("Delete Error", "Please select a valid, saved account to delete.", level='warning')
            return
            
        reply = QMessageBox.question(
            self.view, "Confirm Delete", f"Are you sure you want to permanently delete Account {index}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.config_manager.delete_credentials(index)
                self.view.show_message("Success", f"Account {index} has been deleted.")
                self.refresh_account_list()
            except Exception as e:
                self.view.show_message("Error", f"Could not delete account: {e}", level='critical')

    def handle_open_zoho_console(self):
        self.view.open_url_in_browser_tab(ZOHO_API_CONSOLE_URL)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = AppController()
    controller.run()
    sys.exit(app.exec())