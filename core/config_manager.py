# core/config_manager.py
# Manages multiple account files, now named account_N.json.

import json
import os
from pathlib import Path

class ConfigManager:
    """Manages multiple account files (account_1.json, etc.)."""

    def __init__(self):
        project_root = Path(__file__).parent.parent
        self.credentials_dir = project_root / 'credentials'
        self.credentials_dir.mkdir(exist_ok=True)

    def discover_credentials(self) -> dict[int, str]:
        """
        Scans the credentials directory for files named 'account_N.json'.
        """
        accounts = {}
        # Changed 'credentials_*.json' to 'account_*.json'
        for filename in self.credentials_dir.glob('account_*.json'):
            try:
                # The parsing logic remains the same
                index = int(filename.stem.split('_')[1])
                accounts[index] = f"Account {index}"
            except (ValueError, IndexError):
                continue
        return accounts

    def load_credentials(self, index: int) -> dict:
        """Loads a specific account file by its index."""
        # Changed 'credentials_' to 'account_'
        filepath = self.credentials_dir / f'account_{index}.json'
        if not filepath.exists():
            return {}
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def save_credentials(self, index: int, data: dict):
        """Saves a dictionary of data to a specific account file."""
        # Changed 'credentials_' to 'account_'
        filepath = self.credentials_dir / f'account_{index}.json'
        existing_data = self.load_credentials(index)
        existing_data.update(data)
            
        with open(filepath, 'w') as f:
            json.dump(existing_data, f, indent=4)

    def add_new_credentials(self, client_id: str, client_secret: str) -> int:
        """Adds a new account file."""
        existing_accounts = self.discover_credentials()
        new_index = max(existing_accounts.keys()) + 1 if existing_accounts else 1
        self.save_credentials(new_index, {"client_id": client_id, "client_secret": client_secret})
        return new_index

    def delete_credentials(self, index: int):
        """Deletes a specific account file."""
        # Changed 'credentials_' to 'account_'
        filepath = self.credentials_dir / f'account_{index}.json'
        try:
            if filepath.exists():
                os.remove(filepath)
        except OSError as e:
            print(f"Error deleting file {filepath}: {e}")
            raise