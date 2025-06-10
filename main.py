# main.py
import sys
import requests
import time
from urllib.parse import urlencode, urlparse, parse_qs

from PyQt6.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PyQt6.QtCore import QUrl, Qt

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
        dashboard_ui.organization_selector.currentIndexChanged.connect(self.handle_organization_selection_changed)
        dashboard_ui.change_sender_name_button.clicked.connect(self.handle_open_sender_settings)
        dashboard_ui.view_email_templates_button.clicked.connect(self.handle_view_email_templates)
        dashboard_ui.refresh_button.clicked.connect(self.handle_refresh_all)
        # Items Tab
        dashboard_ui.add_item_button.clicked.connect(self.handle_add_item)
        dashboard_ui.refresh_items_button.clicked.connect(self.handle_fetch_items)
        # Customers Tab
        dashboard_ui.add_customer_row_button.clicked.connect(self.handle_add_customer_row)
        dashboard_ui.remove_customer_row_button.clicked.connect(self.handle_remove_customer_row)
        dashboard_ui.submit_customers_button.clicked.connect(self.handle_submit_customers)
        dashboard_ui.refresh_customers_button.clicked.connect(self.handle_fetch_customers)
        # <<< NEW CONNECTIONS for the invoice form >>>
        dashboard_ui.add_invoice_line_button.clicked.connect(self.handle_add_invoice_line)
        dashboard_ui.remove_invoice_line_button.clicked.connect(self.handle_remove_invoice_line)
        dashboard_ui.create_invoice_button.clicked.connect(self.handle_create_invoice)

        self.refresh_account_list()

    # <<< NEW METHODS to handle the invoice creation process >>>
    def handle_add_invoice_line(self):
        """Tells the view to add a new row to the invoice line items table."""
        self.view.dashboard_widget.add_invoice_line_row()

    def handle_remove_invoice_line(self):
        """Tells the view to remove the selected row from the invoice line items table."""
        self.view.dashboard_widget.remove_selected_invoice_line()

    def handle_create_invoice(self):
        """Gathers data from the form and calls the API to create an invoice."""
        self.view.statusBar().showMessage("Validating invoice...")
        
        # 1. Get and validate data from the form
        invoice_data, error_msg = self.view.dashboard_widget.get_invoice_data()
        if error_msg:
            self.view.show_message("Validation Error", error_msg, level='warning')
            return

        # 2. Get authentication details
        organization_id = self.view.dashboard_widget.organization_selector.currentData()['organization_id']
        account_index = self.view.settings_tab.get_selected_account_index()
        access_token = self.get_valid_access_token(account_index)
        if not access_token:
            self.view.show_message("Authentication Error", "Could not get a valid access token.", level='critical')
            return

        # 3. Call API to create invoice
        self.view.statusBar().showMessage("Creating invoice...")
        try:
            response = self.invoice_api.create_invoice(access_token, organization_id, invoice_data)
            if response.get('code') == 0:
                invoice_id = response['invoice']['invoice_id']
                self.view.show_message("Success", f"Successfully created invoice with ID: {invoice_id}")
                self.view.dashboard_widget.clear_invoice_form()
            else:
                message = response.get('message', 'An unknown API error occurred.')
                self.view.show_message("API Error", f"Could not create invoice: {message}", level='critical')
        except Exception as e:
            self.view.show_message("Error", f"An unexpected error occurred: {e}", level='critical')
        finally:
            self.view.statusBar().showMessage("Ready")


    def handle_fetch_customers(self):
        """Fetches the customer list and populates both customer tables/dropdowns."""
        self.view.statusBar().showMessage("Fetching customers...")
        selected_org_data = self.view.dashboard_widget.organization_selector.currentData()
        if not selected_org_data or 'organization_id' not in selected_org_data:
            self.view.statusBar().showMessage("Select an organization to view customers.")
            self.view.dashboard_widget.populate_customers_table([])
            self.view.dashboard_widget.populate_invoice_customer_dropdown([])
            return
        organization_id = selected_org_data['organization_id']
        account_index = self.view.settings_tab.get_selected_account_index()
        access_token = self.get_valid_access_token(account_index)
        if not access_token:
            self.view.show_message("Authentication Error", "Could not get access token to fetch customers.", level='critical')
            self.view.statusBar().showMessage("Ready")
            return
        try:
            response = self.invoice_api.get_customers(access_token, organization_id)
            if response.get('code') == 0:
                customers_list = response.get('contacts', [])
                self.view.dashboard_widget.populate_customers_table(customers_list)
                self.view.dashboard_widget.populate_invoice_customer_dropdown(customers_list) # Populate invoice form too
                self.view.statusBar().showMessage(f"Successfully fetched {len(customers_list)} customer(s).")
            else:
                message = response.get('message', 'An unknown API error occurred.')
                self.view.show_message("API Error", f"Could not fetch customers: {message}", level='critical')
        except Exception as e:
            self.view.show_message("Error", f"An unexpected error occurred while fetching customers: {e}", level='critical')
        finally:
            self.view.statusBar().showMessage("Ready")
            
    def handle_fetch_items(self):
        """Fetches the item list and populates the items table and invoice form."""
        self.view.statusBar().showMessage("Fetching items...")
        selected_org_data = self.view.dashboard_widget.organization_selector.currentData()
        if not selected_org_data or 'organization_id' not in selected_org_data:
            self.view.statusBar().showMessage("Select an organization to view items.")
            self.view.dashboard_widget.populate_items_table([])
            return
        organization_id = selected_org_data['organization_id']
        account_index = self.view.settings_tab.get_selected_account_index()
        access_token = self.get_valid_access_token(account_index)
        if not access_token:
            self.view.show_message("Authentication Error", "Could not get access token to fetch items.", level='critical')
            self.view.statusBar().showMessage("Ready")
            return
        try:
            response = self.invoice_api.get_items(access_token, organization_id)
            if response.get('code') == 0:
                items_list = response.get('items', [])
                self.view.dashboard_widget.populate_items_table(items_list)
                self.view.dashboard_widget.store_item_list(items_list) # Store for invoice form
                self.view.statusBar().showMessage(f"Successfully fetched {len(items_list)} item(s).")
            else:
                message = response.get('message', 'An unknown API error occurred.')
                self.view.show_message("API Error", f"Could not fetch items: {message}", level='critical')
        except Exception as e:
            self.view.show_message("Error", f"An unexpected error occurred while fetching items: {e}", level='critical')
        finally:
            self.view.statusBar().showMessage("Ready")

    # ... (all other methods from the previous step remain the same) ...
    def handle_add_customer_row(self):
        """Tells the view to add a new row to the customer input table."""
        self.view.dashboard_widget.add_customer_input_row()

    def handle_remove_customer_row(self):
        """Tells the view to remove selected rows from the customer input table."""
        self.view.dashboard_widget.remove_selected_customer_rows()

    def handle_submit_customers(self):
        """Submits all valid customers from the input table to the Zoho API."""
        dashboard_ui = self.view.dashboard_widget
        
        customers_to_create, error_msg = dashboard_ui.get_and_validate_customer_data()
        if error_msg:
            self.view.show_message("Validation Error", error_msg, level='warning')
            return
        if not customers_to_create:
            self.view.show_message("No Data", "There are no customers to submit.", level='warning')
            return

        reply = QMessageBox.question(
            self.view, "Confirm Submission",
            f"You are about to submit {len(customers_to_create)} customer(s). Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return

        selected_org_data = dashboard_ui.organization_selector.currentData()
        organization_id = selected_org_data['organization_id']
        account_index = self.view.settings_tab.get_selected_account_index()
        access_token = self.get_valid_access_token(account_index)
        if not access_token:
            self.view.show_message("Authentication Error", "Could not get a valid access token.", level='critical')
            return

        progress = QProgressDialog("Submitting customers...", "Cancel", 0, len(customers_to_create), self.view)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        
        success_count = 0
        failed_entries = []

        for i, customer in enumerate(customers_to_create):
            progress.setValue(i)
            progress.setLabelText(f"Submitting '{customer['contact_name']}'...")
            if progress.wasCanceled():
                break

            try:
                response = self.invoice_api.create_customer(access_token, organization_id, customer)
                if response.get('code') == 0:
                    success_count += 1
                else:
                    error = response.get('message', 'Unknown API error')
                    failed_entries.append(f"'{customer['contact_name']}': {error}")
            except Exception as e:
                failed_entries.append(f"'{customer['contact_name']}': {e}")
        
        progress.setValue(len(customers_to_create))

        summary_message = f"Submission Complete!\n\n- Successful: {success_count}\n- Failed: {len(failed_entries)}"
        if failed_entries:
            summary_message += "\n\nFailures:\n" + "\n".join(f"- {entry}" for entry in failed_entries)
        
        QMessageBox.information(self.view, "Submission Report", summary_message)
        
        if success_count > 0 and not failed_entries:
             dashboard_ui.customers_input_table.setRowCount(1)
             dashboard_ui.customers_input_table.clearContents()

    def run(self):
        self.view.show()

    def handle_refresh_all(self):
        """Refreshes org details, items, and customers."""
        self.handle_fetch_org_details()
        self.handle_fetch_items()
        self.handle_fetch_customers()

    def handle_add_item(self):
        """Handles the logic for the 'Add Item' button click."""
        dashboard_ui = self.view.dashboard_widget
        item_name = dashboard_ui.item_name_input.text().strip()
        rate_str = dashboard_ui.item_rate_input.text().strip()
        description = dashboard_ui.item_description_input.toPlainText().strip()

        if not item_name or not rate_str:
            self.view.show_message("Input Error", "Item Name and Rate are required.", level='warning')
            return
        
        try:
            rate = float(rate_str)
        except ValueError:
            self.view.show_message("Input Error", "Rate must be a valid number.", level='warning')
            return

        selected_org_data = dashboard_ui.organization_selector.currentData()
        if not selected_org_data or 'organization_id' not in selected_org_data:
            self.view.show_message("Error", "Please select a valid organization from the 'Account Details' tab first.", level='critical')
            return
        organization_id = selected_org_data['organization_id']

        self.view.statusBar().showMessage("Authenticating...")
        account_index = self.view.settings_tab.get_selected_account_index()
        if account_index is None:
             self.view.show_message("Error", "Please select a valid account first.", level='critical')
             self.view.statusBar().showMessage("Ready")
             return
             
        access_token = self.get_valid_access_token(account_index)
        if not access_token:
            self.view.show_message("Authentication Error", "Could not get a valid access token.", level='critical')
            self.view.statusBar().showMessage("Ready")
            return

        self.view.statusBar().showMessage(f"Adding item '{item_name}'...")
        item_payload = { "name": item_name, "rate": rate, "description": description }

        try:
            response = self.invoice_api.create_item(access_token, organization_id, item_payload)
            if response.get('code') == 0:
                self.view.show_message("Success", f"Item '{item_name}' was added successfully.")
                dashboard_ui.clear_add_item_form()
                self.handle_fetch_items()
            else:
                message = response.get('message', 'An unknown API error occurred.')
                self.view.show_message("API Error", f"Could not add item: {message}", level='critical')
        except Exception as e:
            self.view.show_message("Error", f"An unexpected error occurred: {e}", level='critical')
        finally:
            self.view.statusBar().showMessage("Ready")

    def handle_organization_selection_changed(self):
        """Displays org details and fetches items/customers for the selected org."""
        selected_org_data = self.view.dashboard_widget.organization_selector.currentData()
        self.view.dashboard_widget.display_organization_details(selected_org_data)
        if selected_org_data:
            self.handle_fetch_items()
            self.handle_fetch_customers()
        
    def handle_view_email_templates(self):
        selected_org_data = self.view.dashboard_widget.organization_selector.currentData()
        if not selected_org_data or 'organization_id' not in selected_org_data:
            self.view.show_message("Action Blocked", "Please select a valid organization from the dropdown first.", level='warning')
            return
        
        org_id = selected_org_data['organization_id']
        url = f"https://invoice.zoho.com/app/{org_id}#/settings/emails/templates?email_type=invoice_notification"
        
        self.view.statusBar().showMessage("Opening email templates list...")
        self.view.open_url_in_browser_tab(url)

    def handle_fetch_org_details(self):
        """Fetches org data and populates the organization dropdown."""
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
        selected_org_data = self.view.dashboard_widget.organization_selector.currentData()
        if not selected_org_data or 'organization_id' not in selected_org_data:
            self.view.show_message("Action Blocked","Please select a valid organization from the dropdown first.", level='warning')
            return
        
        org_id = selected_org_data['organization_id']
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
            token_data = self.auth_manager.refresh_access_token(creds['client_id'], creds['client_secret'], creds['refresh_token'])
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