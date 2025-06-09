# ui/settings_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFormLayout, QHBoxLayout, QComboBox, QFrame)

class SettingsTab(QWidget):
    UNSAVED_ACCOUNT_PLACEHOLDER_TEXT = "--- New Account (Unsaved) ---"
    UNSAVED_ACCOUNT_PLACEHOLDER_DATA = -1

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Account Selection Section
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(10)
        selection_layout.addWidget(QLabel("Select Account:"))
        self.account_selector = QComboBox()
        self.account_selector.setMinimumWidth(200)
        selection_layout.addWidget(self.account_selector)
        self.add_new_button = QPushButton("Add New Account")
        self.delete_button = QPushButton("Delete Selected Account")
        self.delete_button.setStyleSheet("background-color: #dc3545; color: white;")
        selection_layout.addWidget(self.add_new_button)
        selection_layout.addWidget(self.delete_button)
        selection_layout.addStretch()
        main_layout.addLayout(selection_layout)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # Credential Details Section
        details_layout = QFormLayout()
        details_layout.setSpacing(10)
        self.client_id_input = QLineEdit()
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        details_layout.addRow("Client ID:", self.client_id_input)
        details_layout.addRow("Client Secret:", self.client_secret_input)

        # --- New Authorization Status Label ---
        self.auth_status_label = QLabel("Status: Unknown")
        self.auth_status_label.setStyleSheet("font-weight: bold;")
        details_layout.addRow("Authorization Status:", self.auth_status_label)
        main_layout.addLayout(details_layout)

        # Action Buttons Section
        action_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Changes")
        self.save_button.setStyleSheet("background-color: #007BFF; color: white; padding: 10px;")
        
        # --- New Authorize Button ---
        self.authorize_button = QPushButton("Authorize This Account")
        self.authorize_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
        
        self.api_console_button = QPushButton("Go to Zoho API Console")
        
        action_layout.addWidget(self.save_button)
        action_layout.addWidget(self.authorize_button)
        action_layout.addWidget(self.api_console_button)
        action_layout.addStretch()
        main_layout.addLayout(action_layout)
        main_layout.addStretch()

    def get_credentials(self) -> tuple[str, str]:
        return self.client_id_input.text().strip(), self.client_secret_input.text().strip()

    def set_credentials(self, client_id: str, client_secret: str, refresh_token: str = None):
        self.client_id_input.setText(client_id or "")
        self.client_secret_input.setText(client_secret or "")
        if refresh_token:
            self.auth_status_label.setText("Status: Authorized")
            self.auth_status_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.auth_status_label.setText("Status: Not Authorized")
            self.auth_status_label.setStyleSheet("font-weight: bold; color: red;")
            
    def populate_account_list(self, accounts: dict[int, str]):
        self.account_selector.clear()
        if not accounts:
            self.account_selector.addItem("No accounts exist", self.UNSAVED_ACCOUNT_PLACEHOLDER_DATA)
            return
        for index in sorted(accounts.keys()):
            self.account_selector.addItem(accounts[index], index)
            
    def get_selected_account_index(self) -> int:
        return self.account_selector.currentData()

    def set_unsaved_account_mode(self):
        placeholder_index = self.account_selector.findData(self.UNSAVED_ACCOUNT_PLACEHOLDER_DATA)
        if placeholder_index != -1:
            self.account_selector.setItemText(placeholder_index, self.UNSAVED_ACCOUNT_PLACEHOLDER_TEXT)
            self.account_selector.setCurrentIndex(placeholder_index)
        else:
            self.account_selector.insertItem(0, self.UNSAVED_ACCOUNT_PLACEHOLDER_TEXT, self.UNSAVED_ACCOUNT_PLACEHOLDER_DATA)
            self.account_selector.setCurrentIndex(0)
        self.set_credentials("", "")