# ui/setup_window.py
# This module contains only the UI definition using PyQt.
# It has NO KNOWLEDGE of file systems or configuration logic.

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

class SetupWindow(QWidget):
    """
    The GUI window for the initial credential setup.
    It is responsible for layout and presentation only.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('ZoMailer - Initial Setup')
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel('Enter Zoho API Credentials')
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        client_id_label = QLabel('Client ID:')
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText('Enter the Client ID from Zoho API Console')

        client_secret_label = QLabel('Client Secret:')
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_secret_input.setPlaceholderText('Enter the Client Secret')

        self.save_button = QPushButton('Save and Exit')
        self.save_button.setStyleSheet("background-color: #007BFF; color: white; padding: 10px;")

        layout.addWidget(title_label)
        layout.addWidget(client_id_label)
        layout.addWidget(self.client_id_input)
        layout.addWidget(client_secret_label)
        layout.addWidget(self.client_secret_input)
        layout.addStretch()
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def get_credentials(self) -> tuple[str, str]:
        """Returns the text from the input fields."""
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()
        return client_id, client_secret

    def show_message(self, title: str, message: str, level: str = 'info'):
        """Displays a popup message box."""
        if level == 'warning':
            QMessageBox.warning(self, title, message)
        elif level == 'critical':
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)