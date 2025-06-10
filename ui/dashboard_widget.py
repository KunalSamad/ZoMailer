# ui/dashboard_widget.py
# The main widget for the Dashboard tab.

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton, 
                             QFormLayout, QHBoxLayout, QComboBox, QLineEdit, QTextEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
                             QDateEdit, QSpinBox, QAbstractItemView)
from PyQt6.QtCore import Qt, QDate
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
        
        self.customers_tab = self._create_customers_tab()
        self.sub_tabs.addTab(self.customers_tab, "Customers")

        self.invoice_tab = self._create_invoice_tab()
        self.sub_tabs.addTab(self.invoice_tab, "Invoice")

        # <<< The "Send Invoice" tab is no longer added to the main tab widget here >>>

        # Store item data for populating combos
        self._item_list_data = []

    def _create_send_invoice_tab(self):
        """Creates the UI for sending draft invoices."""
        tab_widget = QWidget()
        main_layout = QVBoxLayout(tab_widget)
        main_layout.setSpacing(10)

        top_layout = QHBoxLayout()
        self.refresh_draft_invoices_button = QPushButton("Refresh Drafts")
        top_layout.addWidget(QLabel("Showing all invoices with 'Draft' status."))
        top_layout.addStretch()
        top_layout.addWidget(self.refresh_draft_invoices_button)
        main_layout.addLayout(top_layout)

        self.draft_invoices_table = QTableWidget()
        self.draft_invoices_table.setColumnCount(5)
        self.draft_invoices_table.setHorizontalHeaderLabels(["Customer Name", "Invoice #", "Date", "Due Date", "Amount"])
        self.draft_invoices_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.draft_invoices_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.draft_invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.draft_invoices_table.setWordWrap(True)
        main_layout.addWidget(self.draft_invoices_table)

        bottom_layout = QHBoxLayout()
        self.send_selected_invoices_button = QPushButton("Send Selected Invoice(s)")
        self.send_selected_invoices_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.send_selected_invoices_button)
        main_layout.addLayout(bottom_layout)
        
        return tab_widget

    # <<< MODIFIED to include "Send Invoice" as a sub-tab >>>
    def _create_invoice_tab(self):
        """Creates the main 'Invoice' container tab."""
        invoice_main_tabs = QTabWidget()

        # Create and add the first sub-tab
        create_invoice_sub_tab = self._create_create_invoice_sub_tab()
        invoice_main_tabs.addTab(create_invoice_sub_tab, "Create Invoice")

        # Create and add the second sub-tab
        send_invoice_sub_tab = self._create_send_invoice_tab()
        invoice_main_tabs.addTab(send_invoice_sub_tab, "Send Invoice")

        return invoice_main_tabs

    def _create_create_invoice_sub_tab(self):
        """Creates the UI for the 'Create Invoice' sub-tab."""
        sub_tab_widget = QWidget()
        main_layout = QVBoxLayout(sub_tab_widget)
        main_layout.setSpacing(15)
        top_groupbox = QGroupBox("Invoice Details")
        top_layout = QFormLayout(top_groupbox)
        self.invoice_customer_selector = QComboBox()
        self.invoice_date_edit = QDateEdit(QDate.currentDate())
        self.invoice_date_edit.setCalendarPopup(True)
        self.invoice_due_date_edit = QDateEdit(QDate.currentDate().addDays(14))
        self.invoice_due_date_edit.setCalendarPopup(True)
        top_layout.addRow("<b>Customer:*</b>", self.invoice_customer_selector)
        top_layout.addRow("<b>Invoice Date:</b>", self.invoice_date_edit)
        top_layout.addRow("<b>Due Date:</b>", self.invoice_due_date_edit)
        main_layout.addWidget(top_groupbox)
        lines_groupbox = QGroupBox("Line Items")
        lines_layout = QVBoxLayout(lines_groupbox)
        self.invoice_line_items_table = QTableWidget()
        self.invoice_line_items_table.setColumnCount(2)
        self.invoice_line_items_table.setHorizontalHeaderLabels(["Item*", "Quantity*"])
        self.invoice_line_items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.invoice_line_items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        lines_layout.addWidget(self.invoice_line_items_table)
        line_buttons_layout = QHBoxLayout()
        self.add_invoice_line_button = QPushButton("Add Line")
        self.remove_invoice_line_button = QPushButton("Remove Selected Line")
        line_buttons_layout.addStretch()
        line_buttons_layout.addWidget(self.add_invoice_line_button)
        line_buttons_layout.addWidget(self.remove_invoice_line_button)
        lines_layout.addLayout(line_buttons_layout)
        main_layout.addWidget(lines_groupbox)
        submit_layout = QHBoxLayout()
        self.create_invoice_button = QPushButton("Create Invoice")
        self.create_invoice_button.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; font-weight: bold;")
        submit_layout.addStretch()
        submit_layout.addWidget(self.create_invoice_button)
        main_layout.addLayout(submit_layout)
        main_layout.addStretch()
        return sub_tab_widget

    def _create_customers_tab(self):
        """Creates the main 'Customers' container tab, which holds its own sub-tabs."""
        customers_main_tabs = QTabWidget()
        add_customer_sub_tab = self._create_add_customer_sub_tab()
        customers_main_tabs.addTab(add_customer_sub_tab, "Add Customers")
        view_customers_sub_tab = self._create_view_customers_sub_tab()
        customers_main_tabs.addTab(view_customers_sub_tab, "View Customers")
        return customers_main_tabs

    def _create_view_customers_sub_tab(self):
        """Creates the UI for the 'View Customers' sub-tab."""
        sub_tab_widget = QWidget()
        main_layout = QVBoxLayout(sub_tab_widget)
        main_layout.setSpacing(10)
        top_layout = QHBoxLayout()
        self.refresh_customers_button = QPushButton("Refresh Customer List")
        self.refresh_customers_button.setFixedWidth(180)
        top_layout.addStretch()
        top_layout.addWidget(self.refresh_customers_button)
        main_layout.addLayout(top_layout)
        self.customers_view_table = QTableWidget()
        self.customers_view_table.setColumnCount(2)
        self.customers_view_table.setHorizontalHeaderLabels(["Display Name", "Email"])
        self.customers_view_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.customers_view_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.customers_view_table.setWordWrap(True)
        main_layout.addWidget(self.customers_view_table)
        return sub_tab_widget

    def _create_add_customer_sub_tab(self):
        """Creates the UI for the 'Add Customers' sub-tab."""
        sub_tab_widget = QWidget()
        main_layout = QVBoxLayout(sub_tab_widget)
        main_layout.setSpacing(10)
        instructions = QLabel("Add customer details below. The Display Name is required. Click 'Add Row' to add more customers.")
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)
        self.customers_input_table = QTableWidget()
        self.customers_input_table.setColumnCount(2)
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
        """Creates the main 'Items' container tab, which holds its own sub-tabs."""
        items_main_tabs = QTabWidget()
        add_item_sub_tab = self._create_add_item_sub_tab()
        items_main_tabs.addTab(add_item_sub_tab, "Add Item")
        view_items_sub_tab = self._create_view_items_sub_tab()
        items_main_tabs.addTab(view_items_sub_tab, "View Item")
        return items_main_tabs

    def _create_add_item_sub_tab(self):
        """Creates the UI for the 'Add Item' sub-tab."""
        sub_tab_widget = QWidget()
        main_layout = QVBoxLayout(sub_tab_widget)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
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
        main_layout.addLayout(form_layout)
        main_layout.addLayout(buttons_layout)
        return sub_tab_widget

    def _create_view_items_sub_tab(self):
        """Creates the UI for the 'View Item' sub-tab."""
        sub_tab_widget = QWidget()
        main_layout = QVBoxLayout(sub_tab_widget)
        main_layout.setSpacing(10)
        top_layout = QHBoxLayout()
        self.refresh_items_button = QPushButton("Refresh Item List")
        self.refresh_items_button.setFixedWidth(150)
        top_layout.addStretch()
        top_layout.addWidget(self.refresh_items_button)
        main_layout.addLayout(top_layout)
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels(["Name", "Rate", "Description"])
        self.items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.items_table.setWordWrap(True)
        main_layout.addWidget(self.items_table)
        return sub_tab_widget

    def _create_account_details_tab(self):
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

    def populate_draft_invoices_table(self, invoices: list):
        """Populates the draft invoices table."""
        self.draft_invoices_table.setRowCount(0)
        if not invoices:
            return
        
        self.draft_invoices_table.setRowCount(len(invoices))
        for row, invoice in enumerate(invoices):
            user_data = {
                "invoice_id": invoice.get('invoice_id'),
                "customer_id": invoice.get('customer_id')
            }
            customer_name_item = QTableWidgetItem(invoice.get('customer_name', 'N/A'))
            customer_name_item.setData(Qt.ItemDataRole.UserRole, user_data)
            self.draft_invoices_table.setItem(row, 0, customer_name_item)
            self.draft_invoices_table.setItem(row, 1, QTableWidgetItem(invoice.get('invoice_number', '')))
            self.draft_invoices_table.setItem(row, 2, QTableWidgetItem(invoice.get('date', '')))
            self.draft_invoices_table.setItem(row, 3, QTableWidgetItem(invoice.get('due_date', '')))
            self.draft_invoices_table.setItem(row, 4, QTableWidgetItem(f"{invoice.get('total', 0.0):.2f}"))

    def get_selected_invoice_data(self):
        """Gets the data dictionaries of the selected rows in the draft invoices table."""
        data_list = []
        selected_rows = sorted(list(set(index.row() for index in self.draft_invoices_table.selectedIndexes())))
        for row in selected_rows:
            item = self.draft_invoices_table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole):
                data_list.append(item.data(Qt.ItemDataRole.UserRole))
        return data_list

    def add_customer_input_row(self):
        self.customers_input_table.insertRow(self.customers_input_table.rowCount())

    def remove_selected_customer_rows(self):
        selected_rows = sorted(list(set(index.row() for index in self.customers_input_table.selectedIndexes())), reverse=True)
        for row in selected_rows:
            self.customers_input_table.removeRow(row)

    def get_and_validate_customer_data(self):
        customers_to_create = []
        for row in range(self.customers_input_table.rowCount()):
            display_name_item = self.customers_input_table.item(row, 0)
            email_item = self.customers_input_table.item(row, 1)
            display_name = display_name_item.text().strip() if display_name_item else ""
            if not display_name:
                return None, f"Row {row + 1}: Display Name is a required field and cannot be empty."
            email_address = email_item.text().strip() if email_item else ""
            customer_data = { "contact_name": display_name }
            if email_address:
                customer_data["contact_persons"] = [{ "email": email_address, "is_primary_contact": True }]
            customers_to_create.append(customer_data)
        return customers_to_create, None

    def populate_customers_table(self, customers: list):
        self.customers_view_table.setRowCount(0)
        if not customers: return
        self.customers_view_table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            email = customer.get('email', '')
            name_item = QTableWidgetItem(customer.get('contact_name', 'N/A'))
            email_item = QTableWidgetItem(email)
            self.customers_view_table.setItem(row, 0, name_item)
            self.customers_view_table.setItem(row, 1, email_item)

    def populate_items_table(self, items: list):
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

    def populate_organizations_list(self, organizations: list, org_id_to_select: str = None):
        """Populates the organization dropdown and optionally re-selects an organization."""
        self.organization_selector.blockSignals(True)
        self.organization_selector.clear()
        if not organizations:
            self.organization_selector.addItem("No organizations found.", None)
        else:
            for org in organizations:
                self.organization_selector.addItem(org.get('name', 'Unnamed Org'), org)
        if org_id_to_select:
            for i in range(self.organization_selector.count()):
                org_data = self.organization_selector.itemData(i)
                if org_data and org_data.get('organization_id') == org_id_to_select:
                    self.organization_selector.setCurrentIndex(i)
                    break
        self.organization_selector.blockSignals(False)
        if self.organization_selector.currentIndex() == -1 and self.organization_selector.count() > 0:
             self.organization_selector.setCurrentIndex(0)
             self.organization_selector.currentIndexChanged.emit(0)
        else:
             self.display_organization_details(self.organization_selector.currentData())

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
        self.populate_customers_table([])
        self.populate_draft_invoices_table([])

    def clear_add_item_form(self):
        self.item_name_input.clear()
        self.item_rate_input.clear()
        self.item_description_input.clear()

    def populate_invoice_customer_dropdown(self, customers: list):
        self.invoice_customer_selector.clear()
        self.invoice_customer_selector.addItem("--- Select a Customer ---", None)
        for customer in customers:
            self.invoice_customer_selector.addItem(
                customer.get('contact_name', 'N/A'), 
                customer
            )

    def store_item_list(self, items: list):
        """Stores the fetched item list to be used by invoice line item combos."""
        self._item_list_data = items
        if self.invoice_line_items_table.rowCount() == 0:
            self.add_invoice_line_row()

    def add_invoice_line_row(self):
        """Adds a new row to the invoice line items table."""
        row_position = self.invoice_line_items_table.rowCount()
        self.invoice_line_items_table.insertRow(row_position)
        item_combo = QComboBox()
        item_combo.addItem("--- Select an Item ---", None)
        for item in self._item_list_data:
            item_combo.addItem(item.get('name', 'N/A'), item.get('item_id', None))
        quantity_spin = QSpinBox()
        quantity_spin.setMinimum(1)
        quantity_spin.setMaximum(9999)
        self.invoice_line_items_table.setCellWidget(row_position, 0, item_combo)
        self.invoice_line_items_table.setCellWidget(row_position, 1, quantity_spin)

    def remove_selected_invoice_line(self):
        """Removes the currently selected row from the invoice line item table."""
        current_row = self.invoice_line_items_table.currentRow()
        if current_row >= 0:
            self.invoice_line_items_table.removeRow(current_row)

    def get_invoice_data(self):
        """Reads and validates all data from the create invoice form."""
        customer_data = self.invoice_customer_selector.currentData()
        if not customer_data or not customer_data.get('contact_id'):
            return None, "You must select a customer."
        
        if not customer_data.get('email'):
             return None, f"Selected customer '{customer_data.get('contact_name')}' has no email address. Please update the customer record before creating an invoice."

        invoice_data = {
            "customer_id": customer_data['contact_id'],
            "date": self.invoice_date_edit.date().toString("yyyy-MM-dd"),
            "due_date": self.invoice_due_date_edit.date().toString("yyyy-MM-dd"),
            "line_items": []
        }
        for row in range(self.invoice_line_items_table.rowCount()):
            item_combo = self.invoice_line_items_table.cellWidget(row, 0)
            quantity_spin = self.invoice_line_items_table.cellWidget(row, 1)
            item_id = item_combo.currentData()
            quantity = quantity_spin.value()
            if item_id:
                invoice_data["line_items"].append({ "item_id": item_id, "quantity": quantity })
        if not invoice_data["line_items"]:
            return None, "Invoice must have at least one line item."
        return invoice_data, None

    def clear_invoice_form(self):
        self.invoice_customer_selector.setCurrentIndex(0)
        self.invoice_date_edit.setDate(QDate.currentDate())
        self.invoice_due_date_edit.setDate(QDate.currentDate().addDays(14))
        self.invoice_line_items_table.setRowCount(0)
        self.add_invoice_line_row()