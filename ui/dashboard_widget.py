# ui/dashboard_widget.py
# The main widget for the Dashboard tab.

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton, 
                             QFormLayout, QHBoxLayout, QComboBox, QLineEdit, QTextEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox)
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
        
        self.items_tab = self._create_items_tab()
        self.sub_tabs.addTab(self.items_tab, "Items")
        
        # <<< RENAMED MAIN TAB to "Customers" and refactored its creation >>>
        self.customers_tab = self._create_customers_tab()
        self.sub_tabs.addTab(self.customers_tab, "Customers")


    # <<< METHOD RENAMED AND REFACTORED to create a container tab widget >>>
    def _create_customers_tab(self):
        """Creates the main 'Customers' container tab, which holds its own sub-tabs."""
        # This is now a tab widget itself to hold sub-tabs
        customers_main_tabs = QTabWidget()

        # Create the "Add Customers" sub-tab and add it
        add_customer_sub_tab = self._create_add_customer_sub_tab()
        customers_main_tabs.addTab(add_customer_sub_tab, "Add Customers")

        # You could add other customer-related sub-tabs here in the future (e.g., "View Customers")
        
        return customers_main_tabs

    # <<< NEW HELPER METHOD to create the content for the "Add Customers" sub-tab >>>
    def _create_add_customer_sub_tab(self):
        """Creates the UI for the 'Add Customers' sub-tab."""
        sub_tab_widget = QWidget()
        main_layout = QVBoxLayout(sub_tab_widget)
        main_layout.setSpacing(10)

        instructions = QLabel("Add customer details below. The Display Name is required. Click 'Add Row' to add more customers.")
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)

        self.customers_input_table = QTableWidget()
        # <<< COLUMN COUNT REDUCED TO 2 >>>
        self.customers_input_table.setColumnCount(2)
        # <<< "Company Name" HEADER REMOVED >>>
        self.customers_input_table.setHorizontalHeaderLabels(["Display Name*", "Email"])
        self.customers_input_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.customers_input_table.setRowCount(1)
        main_layout.addWidget(self.customers_input_table)

        buttons_layout = QHBoxLayout()
        self.add_customer_row_button = QPushButton("Add Row")
        self.remove_customer_row_button = QPushButton("Remove Selected Row(s)")
        self.submit_customers_button = QPushButton("Submit All Customers")
        self.submit_customers_button.setStyleSheet("background-color: #007BFF; color: white; padding: 10px;")
        
        buttons_layout.addWidget(self.add_customer_row_button)
        buttons_layout.addWidget(self.remove_customer_row_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.submit_customers_button)
        main_layout.addLayout(buttons_layout)
        
        return sub_tab_widget


    def _create_items_tab(self):
        """Creates the UI for the combined 'Items' tab."""
        tab_widget = QWidget()
        main_layout = QVBoxLayout(tab_widget)
        main_layout.setSpacing(15)

        add_item_groupbox = QGroupBox("Add New Item")
        add_item_layout = QVBoxLayout(add_item_groupbox)
        add_item_layout.setSpacing(10)
        
        form_layout = QFormLayout()
        
        self.item_name_input = QLineEdit()
        self.item_name_input.setPlaceholderText("e.g., Web Design Services")
        
        self.item_rate_input = QLineEdit()
        self.item_rate_input.setValidator(QDoubleValidator(0.00, 9999999.99, 2))
        self.item_rate_input.setPlaceholderText("e.g., 150.00")

        self.item_description_input = QTextEdit()
        self.item_description_input.setPlaceholderText("A detailed description of the service or product.")
        self.item_description_input.setFixedHeight(80)
        
        form_layout.addRow("<b>Item Name:*</b>", self.item_name_input)
        form_layout.addRow("<b>Rate:*</b>", self.item_rate_input)
        form_layout.addRow("<b>Description:</b>", self.item_description_input)

        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.setFixedWidth(120)
        self.add_item_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_item_button)

        add_item_layout.addLayout(form_layout)
        add_item_layout.addLayout(buttons_layout)
        main_layout.addWidget(add_item_groupbox)

        view_items_groupbox = QGroupBox("Existing Items")
        view_items_layout = QVBoxLayout(view_items_groupbox)
        view_items_layout.setSpacing(10)

        top_layout = QHBoxLayout()
        self.refresh_items_button = QPushButton("Refresh Item List")
        self.refresh_items_button.setFixedWidth(150)
        top_layout.addStretch()
        top_layout.addWidget(self.refresh_items_button)
        view_items_layout.addLayout(top_layout)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels(["Name", "Rate", "Description"])
        self.items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.items_table.setWordWrap(True)
        
        view_items_layout.addWidget(self.items_table)
        main_layout.addWidget(view_items_groupbox)
        
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
        
        self.refresh_button = QPushButton("Refresh Details")
        self.refresh_button.setFixedWidth(120)
        
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

    def add_customer_input_row(self):
        """Adds a new empty row to the customer input table."""
        self.customers_input_table.insertRow(self.customers_input_table.rowCount())

    def remove_selected_customer_rows(self):
        """Removes all currently selected rows from the customer input table."""
        selected_rows = sorted(list(set(index.row() for index in self.customers_input_table.selectedIndexes())), reverse=True)
        for row in selected_rows:
            self.customers_input_table.removeRow(row)

    # <<< MODIFIED to remove "company_name" logic >>>
    def get_and_validate_customer_data(self):
        """Reads and validates all customer data from the input table."""
        customers_to_create = []
        for row in range(self.customers_input_table.rowCount()):
            display_name_item = self.customers_input_table.item(row, 0)
            email_item = self.customers_input_table.item(row, 1)

            display_name = display_name_item.text().strip() if display_name_item else ""
            
            if not display_name:
                return None, f"Row {row + 1}: Display Name is a required field and cannot be empty."

            email_address = email_item.text().strip() if email_item else ""

            # The 'company_name' key is no longer included
            customer_data = {
                "contact_name": display_name,
            }

            if email_address:
                customer_data["contact_persons"] = [
                    {
                        "email": email_address,
                        "is_primary_contact": True
                    }
                ]
            
            customers_to_create.append(customer_data)
        
        return customers_to_create, None

    def populate_items_table(self, items: list):
        """Clears and populates the items table with new data."""
        self.items_table.setRowCount(0)
        if not items: return
        self.items_table.setRowCount(len(items))
        for row, item in enumerate(items):
            rate = f"{item.get('rate', 0.0):.2f}"
            name_item = QTableWidgetItem(item.get('name', 'N/A'))
            rate_item = QTableWidgetItem(rate)
            desc_item = QTableWidgetItem(item.get('description', ''))
            rate_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.items_table.setItem(row, 0, name_item)
            self.items_table.setItem(row, 1, rate_item)
            self.items_table.setItem(row, 2, desc_item)
        self.items_table.resizeColumnsToContents()
        self.items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def populate_organizations_list(self, organizations: list):
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
        self.populate_items_table([])

    def clear_add_item_form(self):
        self.item_name_input.clear()
        self.item_rate_input.clear()
        self.item_description_input.clear()