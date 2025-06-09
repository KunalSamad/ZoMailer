# run_setup.py
# This is the main entry point for the setup application.
# It orchestrates the UI and the backend logic, connecting them together.

import sys
from PyQt6.QtWidgets import QApplication

# Import our custom modules
from ui.setup_window import SetupWindow
from core.config_manager import ConfigManager

class SetupController:
    """
    The controller that connects the UI to the business logic.
    """
    def __init__(self):
        # Instantiate the logic and the UI
        self.view = SetupWindow()
        self.model = ConfigManager()
        
        # Connect the UI's 'save' button to a handler method in this controller
        self.view.save_button.clicked.connect(self.handle_save_action)

    def run(self):
        """Shows the main window and starts the application."""
        self.view.show()

    def handle_save_action(self):
        """
        This method is triggered when the user clicks the 'Save' button.
        """
        # 1. Get data from the view
        client_id, client_secret = self.view.get_credentials()

        # 2. Validate the data
        if not client_id or not client_secret:
            self.view.show_message(
                'Input Error', 
                'Both Client ID and Client Secret must be filled out.', 
                level='warning'
            )
            return

        # 3. Pass the data to the model (logic) to be processed
        try:
            self.model.save_credentials(client_id, client_secret)
            self.view.show_message(
                'Success', 
                'Credentials have been saved successfully.'
            )
            # 4. Close the application on success
            self.view.close()
        except Exception as e:
            self.view.show_message(
                'Error',
                f'An unexpected error occurred:\n{e}',
                level='critical'
            )


if __name__ == '__main__':
    # Ensure the settings file exists with placeholders before starting
    # This can be done manually or via a helper script. For now, we assume
    # the initial settings.py from the previous step exists.
    
    app = QApplication(sys.argv)
    controller = SetupController()
    controller.run()
    sys.exit(app.exec())