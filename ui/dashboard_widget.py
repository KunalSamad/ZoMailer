# ui/dashboard_widget.py
# The main widget for the Dashboard tab, now with an "Add Item" form.

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton, 
                             QFormLayout, QHBoxLayout, QComboBox, QLineEdit, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

class DashboardWidget(QWidget):
    """A widget that contains the dashboard's sub-tabs."""
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        self.sub_tabs = QTabWidget()
        main_layout.addWidget(self.sub_tabs)
        
        # Create and add the sub-tabs
        self.account_details_tab = self._create_account_details_tab()
        self.sub_tabs.addTab(self.account_details_tab, "Account Details")
        
        # <<< CREATE AND ADD THE NEW "ADD ITEM" TAB >>>
        self.add_item_tab = self._create_add_item_tab()
        self.sub_tabs.addTab(self.add_item_tab, "Add Item")

    def _create_add_item_tab(self):
        """Creates the UI for the 'Add Item' sub-tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)

        form_layout = QFormLayout()
        
        self.item_name_input = QLineEdit()
        self.item_name_input.setPlaceholderText("e.g., Web Design Services")
        
        self.item_rate_input = QLineEdit()
        self.item_rate_input.setValidator(QDoubleValidator(0.00, 9999999.99, 2))
        self.item_rate_input.setPlaceholderText("e.g., 150.00")

        self.item_description_input = QTextEdit()
        self.item_description_input.setPlaceholderText("A detailed description of the service or product.")
        self.item_description_input.setFixedHeight(100)
        
        form_layout.addRow("<b>Item Name:*</b>", self.item_name_input)
        form_layout.addRow("<b>Rate:*</b>", self.item_rate_input)
        form_layout.addRow("<b>Description:</b>", self.item_description_input)

        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.setFixedWidth(120)
        self.add_item_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_item_button)

        layout.addLayout(form_layout)
        layout.addLayout(buttons_layout)
        
        return tab_widget

    def _create_account_details_tab(self):
        """Creates the UI for the 'Account Details' sub-tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)
        
        org_selection_layout = QHBoxLayout()
        org_selection_layout.addWidget(QLabel("<b>Select Organization:</b>"))
        self.organization_selector = QComboBox()
        self.organization_selector.setMinimumWidth(300)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setFixedWidth(100)
        
        org_selection_layout.addWidget(self.organization_selector)
        org_selection_layout.addWidget(self.refresh_button)
        org_selection_layout.addStretch()
        layout.addLayout(org_selection_layout)

        details_layout = QFormLayout()
        details_layout.setSpacing(10)
        details_layout.setContentsMargins(0, 10, 0, 0)
        
        self.org_id_label = QLabel("...") 
        self.org_name_label = QLabel("...")
        self.contact_name_label = QLabel("...")
        self.email_label = QLabel("...")
        self.country_label = QLabel("...")
        self.currency_code_label = QLabel("...")
        
        self.change_sender_name_button = QPushButton("Change Sender Name") 
        self.change_sender_name_button.setFixedWidth(160) 

        self.view_email_templates_button = QPushButton("View Email Templates")
        self.view_email_templates_button.setFixedWidth(160)

        contact_layout = QHBoxLayout()
        contact_layout.setContentsMargins(0,0,0,0)
        contact_layout.addWidget(self.contact_name_label)
        contact_layout.addStretch()
        contact_layout.addWidget(self.change_sender_name_button)
        
        template_actions_layout = QHBoxLayout()
        template_actions_layout.setContentsMargins(0,0,0,0)
        template_actions_layout.addWidget(self.view_email_templates_button)
        template_actions_layout.addStretch()

        details_layout.addRow("Organization ID:", self.org_id_label)
        details_layout.addRow("Organization Name:", self.org_name_label)
        details_layout.addRow("Primary Contact:", contact_layout) 
        details_layout.addRow("Email:", self.email_label)
        details_layout.addRow("Country:", self.country_label)
        details_layout.addRow("Currency:", self.currency_code_label)
        details_layout.addRow("Actions:", template_actions_layout)
        
        layout.addLayout(details_layout)
        return tab_widget

    def populate_organizations_list(self, organizations: list):
        """Populates the organization dropdown with a list of organizations."""
        self.organization_selector.blockSignals(True)
        self.organization_selector.clear()
        
        if not organizations:
            self.organization_selector.addItem("No organizations found.", None)
        else:
            for org in organizations:
                self.organization_selector.addItem(org.get('name', 'Unnamed Org'), org)
                
        self.organization_selector.blockSignals(False)
        if self.organization_selector.count() > 0:
            self.organization_selector.currentIndexChanged.emit(0)

    def display_organization_details(self, details: dict | None):
        """Populates the labels with data from a single organization dictionary."""
        if not details:
            self.clear_organization_details()
            return
            
        self.org_id_label.setText(details.get('organization_id', 'N/A')) 
        self.org_name_label.setText(details.get('name', 'N/A'))
        self.contact_name_label.setText(details.get('contact_name', 'N/A'))
        self.email_label.setText(details.get('email', 'N/A'))
        self.country_label.setText(details.get('country', 'N/A'))
        self.currency_code_label.setText(
            f"{details.get('currency_code', 'N/A')} ({details.get('currency_symbol', '')})"
        )
        
    def clear_organization_details(self):
        """Resets the detail labels and organization dropdown to their default state."""
        placeholder_text = "N/A - Select an authorized account in Settings"
        self.org_id_label.setText(placeholder_text) 
        self.org_name_label.setText(placeholder_text)
        self.contact_name_label.setText(placeholder_text)
        self.email_label.setText(placeholder_text)
        self.country_label.setText(placeholder_text)
        self.currency_code_label.setText(placeholder_text)
        
        self.organization_selector.blockSignals(True)
        self.organization_selector.clear()
        self.organization_selector.addItem("N/A", None)
        self.organization_selector.blockSignals(False)

    def clear_add_item_form(self):
        """Clears all input fields in the 'Add Item' form."""
        self.item_name_input.clear()
        self.item_rate_input.clear()
        self.item_description_input.clear()