# main.py
import sys
import requests
import time
from urllib.parse import urlencode, urlparse, parse_qs

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QUrl

from ui.main_window import MainWindow
from ui.settings_tab import SettingsTab
from core.config_manager import ConfigManager
from core.auth_manager import AuthManager
from core.invoice_api import InvoiceApi
from config import settings

class AppController:
    """The main controller, managing multiple organizations."""
    def __init__(self):
        self.config_manager = ConfigManager()
        self.auth_manager = AuthManager()
        self.invoice_api = InvoiceApi()
        self.view = MainWindow()
        self._authorizing_account_index = None
        
        # Connect UI signals
        settings_ui = self.view.settings_tab
        settings_ui.save_button.clicked.connect(self.handle_save_action)
        settings_ui.api_console_button.clicked.connect(self.handle_open_zoho_console)
        settings_ui.add_new_button.clicked.connect(self.prepare_for_add_new)
        settings_ui.delete_button.clicked.connect(self.handle_delete_account)
        settings_ui.account_selector.currentIndexChanged.connect(self.handle_account_selection_changed)
        settings_ui.authorize_button.clicked.connect(self.handle_authorization_start)
        
        self.view.redirect_url_intercepted.connect(self.handle_redirect_url)
        
        # Connect Dashboard signals
        dashboard_ui = self.view.dashboard_widget
        dashboard_ui.organization_selector.currentIndexChanged.connect(
            self.handle_organization_selection_changed
        )
        dashboard_ui.change_sender_name_button.clicked.connect(self.handle_open_sender_settings)
        dashboard_ui.refresh_button.clicked.connect(self.handle_fetch_org_details)
        dashboard_ui.view_email_templates_button.clicked.connect(self.handle_view_email_templates)


        self.refresh_account_list()

    def run(self):
        self.view.show()

    def handle_organization_selection_changed(self):
        """Displays the details of the organization selected from the dropdown."""
        selected_org_data = self.view.dashboard_widget.organization_selector.currentData()
        self.view.dashboard_widget.display_organization_details(selected_org_data)
        
    def handle_view_email_templates(self):
        """Opens the Zoho invoice email templates list page in the browser tab."""
        selected_org_data = self.view.dashboard_widget.organization_selector.currentData()
        
        if not selected_org_data or 'organization_id' not in selected_org_data:
            self.view.show_message(
                "Action Blocked",
                "Please select a valid organization from the dropdown first.",
                level='warning'
            )
            return
        
        org_id = selected_org_data['organization_id']
        
        # This URL navigates directly to the list of templates for invoice notifications.
        url = f"https://invoice.zoho.com/app/{org_id}#/settings/emails/templates?email_type=invoice_notification"
        
        self.view.statusBar().showMessage("Opening email templates list...")
        self.view.open_url_in_browser_tab(url)

    def handle_fetch_org_details(self):
        """Fetches org data and populates the new organization dropdown."""
        self.view.statusBar().showMessage("Refreshing organization details...")
        index = self.view.settings_tab.get_selected_account_index()
        if index is None or index <= 0:
            self.view.statusBar().showMessage("Cannot refresh: No authorized account selected.")
            return

        access_token = self.get_valid_access_token(index)
        if not access_token:
            self.view.statusBar().showMessage("Refresh failed: Could not get access token.")
            return

        try:
            org_data = self.invoice_api.get_organizations(access_token)
            if org_data.get('code') == 0 and org_data.get('organizations'):
                organizations_list = org_data['organizations']
                self.view.dashboard_widget.populate_organizations_list(organizations_list)
                self.view.statusBar().showMessage(f"Successfully refreshed and loaded {len(organizations_list)} organization(s).")
            else:
                message = org_data.get('message', 'Unknown API error.')
                self.view.show_message("API Error", f"Failed to get organization details: {message}", level='critical')
                self.view.dashboard_widget.clear_organization_details() 
        except Exception as e:
            self.view.show_message("Error", f"An error occurred while fetching data: {e}", level='critical')
            self.view.dashboard_widget.clear_organization_details()

    def handle_open_sender_settings(self):
        """Opens the Zoho sender email settings page in the browser tab."""
        selected_org_data = self.view.dashboard_widget.organization_selector.currentData()
        
        if not selected_org_data or 'organization_id' not in selected_org_data:
            self.view.show_message(
                "Action Blocked",
                "Please select a valid organization from the dropdown first.",
                level='warning'
            )
            return
        
        org_id = selected_org_data['organization_id']
        # Construct the URL dynamically for the selected organization
        url = f"https://invoice.zoho.com/app/{org_id}#/settings/emails/preference"
        
        self.view.open_url_in_browser_tab(url)

    def get_valid_access_token(self, account_index: int) -> str | None:
        creds = self.config_manager.load_credentials(account_index)
        if not creds.get('refresh_token'):
            return None
        expiry_ts = creds.get('token_expiry_timestamp', 0)
        if expiry_ts > time.time() + 30:
            return creds.get('access_token')
        try:
            token_data = self.auth_manager.refresh_access_token(
                creds['client_id'], creds['client_secret'], creds['refresh_token']
            )
            data_to_save = {
                'access_token': token_data['access_token'],
                'token_expiry_timestamp': int(time.time()) + token_data.get('expires_in', 3600)
            }
            self.config_manager.save_credentials(account_index, data_to_save)
            return data_to_save['access_token']
        except Exception as e:
            self.view.show_message("Authentication Error", f"Could not refresh access token: {e}", level='critical')
            return None
            
    def handle_account_selection_changed(self):
        index = self.view.settings_tab.get_selected_account_index()
        self.view.dashboard_widget.clear_organization_details()
        if index == SettingsTab.UNSAVED_ACCOUNT_PLACEHOLDER_DATA:
            self.view.settings_tab.set_credentials("", "")
            return
        if index is None: 
            return
        credentials = self.config_manager.load_credentials(index)
        is_authorized = bool(credentials.get("refresh_token"))
        self.view.settings_tab.set_credentials(
            credentials.get("client_id"),
            credentials.get("client_secret"),
            credentials.get("refresh_token")
        )
        self.view.statusBar().showMessage(f"Selected Account {index}")
        if is_authorized:
            self.handle_fetch_org_details()
            
    def prepare_for_add_new(self):
        self.view.settings_tab.set_unsaved_account_mode()
        self.view.dashboard_widget.clear_organization_details()
        self.view.statusBar().showMessage("Enter new credential details and click 'Save Changes'.")
        
    def handle_authorization_start(self):
        index = self.view.settings_tab.get_selected_account_index()
        if index is None or index <= 0:
            self.view.show_message("Error", "Please select a valid, saved account to authorize.", level='warning')
            return
        creds = self.config_manager.load_credentials(index)
        client_id = creds.get('client_id')
        if not client_id:
            self.view.show_message("Error", "Please save a Client ID for this account before authorizing.", level='warning')
            return
        self._authorizing_account_index = index
        params = {
            'scope': settings.ZOHO_SCOPES, 'client_id': client_id, 'response_type': 'code',
            'redirect_uri': settings.REDIRECT_URI, 'access_type': 'offline'
        }
        auth_url = f"{settings.ZOHO_AUTH_URL}?{urlencode(params)}"
        self.view.open_url_in_browser_tab(auth_url)
        
    def handle_redirect_url(self, url: QUrl):
        self.view.statusBar().showMessage("Authorization redirect detected. Capturing token...")
        parsed_url = urlparse(url.toString())
        query_params = parse_qs(parsed_url.query)
        grant_code = query_params.get('code', [None])[0]
        if not grant_code:
            self.view.show_message("Authorization Failed", "Could not capture the grant token from Zoho.", level='critical')
            return
        self.view.statusBar().showMessage("Grant token captured! Exchanging for tokens...")
        self.exchange_code_for_tokens(grant_code)
        
    def exchange_code_for_tokens(self, code: str):
        index = self._authorizing_account_index
        if not index: return
        creds = self.config_manager.load_credentials(index)
        client_id = creds.get('client_id')
        client_secret = creds.get('client_secret')
        try:
            token_data = self.auth_manager.exchange_code_for_tokens(client_id, client_secret, code)
            data_to_save = {}
            if 'access_token' in token_data:
                data_to_save['access_token'] = token_data['access_token']
                expires_in_seconds = token_data.get('expires_in', 3600)
                data_to_save['token_expiry_timestamp'] = int(time.time()) + expires_in_seconds
            else:
                error_details = token_data.get('error', 'Unknown error.')
                self.view.show_message("Authorization Failed", f"Could not retrieve tokens from Zoho. Details: {error_details}", level='critical')
                return
            if 'refresh_token' in token_data:
                data_to_save['refresh_token'] = token_data['refresh_token']
                self.config_manager.save_credentials(index, data_to_save)
                self.view.show_message("Success!", "Application successfully authorized. Refresh token saved.")
            else:
                self.config_manager.save_credentials(index, data_to_save)
                self.view.show_message("Success!", "Account re-authorized. New access token acquired.")
            self.handle_account_selection_changed()
        except Exception as e:
            self.view.show_message("Error", f"An error occurred during token exchange: {e}", level='critical')
        finally:
            self._authorizing_account_index = None
            
    def refresh_account_list(self, select_index: int = None):
        accounts = self.config_manager.discover_credentials()
        current_selection = self.view.settings_tab.account_selector.currentData()
        self.view.settings_tab.account_selector.blockSignals(True)
        self.view.settings_tab.populate_account_list(accounts)
        index_to_select = select_index if select_index is not None else current_selection
        if index_to_select:
            list_index = self.view.settings_tab.account_selector.findData(index_to_select)
            self.view.settings_tab.account_selector.setCurrentIndex(list_index)
        elif len(accounts) > 0:
            self.view.settings_tab.account_selector.setCurrentIndex(0)
        self.view.settings_tab.account_selector.blockSignals(False)
        self.handle_account_selection_changed()
        
    def handle_save_action(self):
        index = self.view.settings_tab.get_selected_account_index()
        client_id, client_secret = self.view.settings_tab.get_credentials()
        if not client_id or not client_secret:
            self.view.show_message("Input Error", "Client ID and Client Secret cannot be empty.", level='warning')
            return
        try:
            creds_to_save = {"client_id": client_id, "client_secret": client_secret}
            if index == SettingsTab.UNSAVED_ACCOUNT_PLACEHOLDER_DATA:
                new_index = self.config_manager.add_new_credentials(client_id, client_secret)
                self.view.show_message("Success", f"Successfully created Account {new_index}.")
                self.refresh_account_list(select_index=new_index)
            elif index is not None and index > 0:
                reply = QMessageBox.question(self.view, "Confirm Overwrite", f"This will overwrite the Client ID and Secret but preserve the authorization. Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    self.view.statusBar().showMessage("Save operation cancelled.")
                    return
                self.config_manager.save_credentials(index, creds_to_save)
                self.view.show_message("Success", f"Changes to Account {index} have been saved.")
                self.handle_account_selection_changed()
            else:
                self.view.show_message("Save Error", "No account is selected.", level='warning')
        except Exception as e:
            self.view.show_message("Error", f"Could not save changes: {e}", level='critical')
            
    def handle_delete_account(self):
        index = self.view.settings_tab.get_selected_account_index()
        if index is None or index <= 0:
            self.view.show_message("Delete Error", "Please select a valid, saved account to delete.", level='warning')
            return
        reply = QMessageBox.question(self.view, "Confirm Delete", f"Are you sure you want to permanently delete Account {index}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.config_manager.delete_credentials(index)
                self.view.show_message("Success", f"Account {index} has been deleted.")
                self.refresh_account_list()
            except Exception as e:
                self.view.show_message("Error", f"Could not delete account: {e}", level='critical')
                
    def handle_open_zoho_console(self):
        self.view.open_url_in_browser_tab(settings.ZOHO_API_CONSOLE_URL)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = AppController()
    controller.run()
    sys.exit(app.exec())