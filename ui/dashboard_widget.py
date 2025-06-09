# ui/dashboard_widget.py
# The main widget for the Dashboard tab, now with organization selection.

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton, 
                             QFormLayout, QHBoxLayout, QComboBox)
from PyQt6.QtCore import Qt

class DashboardWidget(QWidget):
    """A widget that contains the dashboard's sub-tabs."""
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        self.sub_tabs = QTabWidget()
        main_layout.addWidget(self.sub_tabs)
        
        # Create and add the first sub-tab
        self.account_details_tab = self._create_account_details_tab()
        self.sub_tabs.addTab(self.account_details_tab, "Account Details")

    def _create_account_details_tab(self):
        """Creates the UI for the 'Account Details' sub-tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)
        
        # --- Organization Selection and Refresh Layout ---
        org_selection_layout = QHBoxLayout()
        org_selection_layout.addWidget(QLabel("<b>Select Organization:</b>"))
        self.organization_selector = QComboBox()
        self.organization_selector.setMinimumWidth(300)
        
        self.refresh_button = QPushButton("Refresh") # <<< NEW REFRESH BUTTON
        self.refresh_button.setFixedWidth(100)
        
        org_selection_layout.addWidget(self.organization_selector)
        org_selection_layout.addWidget(self.refresh_button) # <<< ADDED TO LAYOUT
        org_selection_layout.addStretch()
        layout.addLayout(org_selection_layout)

        # Details layout for displaying information
        details_layout = QFormLayout()
        details_layout.setSpacing(10)
        details_layout.setContentsMargins(0, 10, 0, 0) # Add some top margin
        
        # --- Labels to display organization details ---
        self.org_id_label = QLabel("...") 
        self.org_name_label = QLabel("...")
        self.contact_name_label = QLabel("...")
        self.email_label = QLabel("...")
        self.country_label = QLabel("...")
        self.currency_code_label = QLabel("...")
        
        # --- Button to change sender name ---
        self.change_sender_name_button = QPushButton("Change Sender Name") 
        self.change_sender_name_button.setFixedWidth(160) 
        contact_layout = QHBoxLayout()
        contact_layout.setContentsMargins(0,0,0,0)
        contact_layout.addWidget(self.contact_name_label)
        contact_layout.addStretch()
        contact_layout.addWidget(self.change_sender_name_button)

        # --- Add rows to the form layout ---
        details_layout.addRow("Organization ID:", self.org_id_label)
        details_layout.addRow("Organization Name:", self.org_name_label)
        details_layout.addRow("Primary Contact:", contact_layout) 
        details_layout.addRow("Email:", self.email_label)
        details_layout.addRow("Country:", self.country_label)
        details_layout.addRow("Currency:", self.currency_code_label)
        
        layout.addLayout(details_layout)
        return tab_widget

    def populate_organizations_list(self, organizations: list):
        """Populates the organization dropdown with a list of organizations."""
        self.organization_selector.blockSignals(True) # Prevent signals during population
        self.organization_selector.clear()
        
        if not organizations:
            self.organization_selector.addItem("No organizations found.", None)
        else:
            for org in organizations:
                # Add the organization name as the text, and the whole org dictionary as the data
                self.organization_selector.addItem(org.get('name', 'Unnamed Org'), org)
                
        self.organization_selector.blockSignals(False)
        # Manually trigger the first display after populating
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
        
        # Also clear the organization list
        self.organization_selector.blockSignals(True)
        self.organization_selector.clear()
        self.organization_selector.addItem("N/A", None)
        self.organization_selector.blockSignals(False)
