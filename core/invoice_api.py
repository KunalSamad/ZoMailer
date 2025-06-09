# core/invoice_api.py
# A dedicated client for making authenticated calls to the Zoho Invoice API.

import requests
from config import settings

class InvoiceApi:
    """Handles making authenticated requests to the Zoho Invoice API."""

    def __init__(self):
        self.base_url = settings.API_BASE_URL

    def _get_auth_headers(self, access_token: str) -> dict:
        """Constructs the standard authorization header."""
        if not access_token:
            raise ValueError("Access token cannot be empty.")
        return {
            'Authorization': f'Zoho-oauthtoken {access_token}'
        }

    def get_organizations(self, access_token: str) -> dict:
        """
        Fetches the list of organizations associated with the access token.
        """
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/organizations"
        
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch organizations: {e}") from e

    # <<< The update_organization_details method has been removed >>>
