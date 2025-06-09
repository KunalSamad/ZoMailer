# core/config_manager.py
# Manages multiple credential files in the 'credentials' directory.

import json
import os
from pathlib import Path

class ConfigManager:
    """Manages multiple credential files (credentials_1.json, etc.)."""

    def __init__(self):
        project_root = Path(__file__).parent.parent
        self.credentials_dir = project_root / 'credentials'
        self.credentials_dir.mkdir(exist_ok=True)

    def discover_credentials(self) -> dict[int, str]:
        """
        Scans the credentials directory and returns a dictionary
        mapping the account index to its display name.
        """
        accounts = {}
        for filename in self.credentials_dir.glob('credentials_*.json'):
            try:
                index = int(filename.stem.split('_')[1])
                accounts[index] = f"Account {index}"
            except (ValueError, IndexError):
                continue
        return accounts

    def load_credentials(self, index: int) -> dict:
        """Loads a specific credential file by its index."""
        filepath = self.credentials_dir / f'credentials_{index}.json'
        if not filepath.exists():
            return {"client_id": "", "client_secret": ""}
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                data.setdefault("client_id", "")
                data.setdefault("client_secret", "")
                return data
        except (json.JSONDecodeError, IOError):
            return {"client_id": "", "client_secret": ""}

    def save_credentials(self, index: int, client_id: str, client_secret: str):
        """Saves (updates) a specific credential file by its index."""
        filepath = self.credentials_dir / f'credentials_{index}.json'
        data_to_save = {"client_id": client_id, "client_secret": client_secret}
        with open(filepath, 'w') as f:
            json.dump(data_to_save, f, indent=4)

    def add_new_credentials(self, client_id: str, client_secret: str) -> int:
        """
        Finds the next available index and creates a new credential file
        with the provided data. Returns the new index.
        """
        existing_accounts = self.discover_credentials()
        new_index = max(existing_accounts.keys()) + 1 if existing_accounts else 1
        # Call the existing save method to create the file with data
        self.save_credentials(new_index, client_id, client_secret)
        return new_index

    def delete_credentials(self, index: int):
        """Deletes a specific credential file."""
        filepath = self.credentials_dir / f'credentials_{index}.json'
        try:
            if filepath.exists():
                os.remove(filepath)
        except OSError as e:
            print(f"Error deleting file {filepath}: {e}")
            raise