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
        """Fetches the list of organizations associated with the access token."""
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/organizations"
        
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch organizations: {e}") from e

    def get_items(self, access_token: str, organization_id: str) -> dict:
        """Fetches the list of items for a specific organization."""
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/items?organization_id={organization_id}"

        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch items: {e}") from e

    def create_item(self, access_token: str, organization_id: str, item_data: dict) -> dict:
        """Creates a new item in Zoho Invoice for a specific organization."""
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/items?organization_id={organization_id}"
        
        payload = item_data.copy()

        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            try:
                error_details = e.response.json()
                message = error_details.get('message', str(e))
            except:
                message = str(e)
            raise ConnectionError(f"Failed to create item: {message}") from e
            
    def get_customers(self, access_token: str, organization_id: str) -> dict:
        """Fetches the list of contacts (customers) for a specific organization."""
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/contacts?organization_id={organization_id}"

        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch customers: {e}") from e

    def create_customer(self, access_token: str, organization_id: str, customer_data: dict) -> dict:
        """Creates a new customer in Zoho Invoice."""
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/contacts?organization_id={organization_id}"
        
        payload = customer_data.copy()

        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error creating customer: {e}") from e

    # <<< NEW METHOD to create an invoice >>>
    def create_invoice(self, access_token: str, organization_id: str, invoice_data: dict) -> dict:
        """
        Creates a new invoice.
        """
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/invoices?organization_id={organization_id}"
        
        payload = invoice_data.copy()
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error creating invoice: {e}") from e