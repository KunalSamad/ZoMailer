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

    # ... (get_organizations, get_items, create_item, get_customers, create_customer, create_invoice are all correct and unchanged) ...
    def get_organizations(self, access_token: str) -> dict:
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/organizations"
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch organizations: {e}") from e

    def get_items(self, access_token: str, organization_id: str) -> dict:
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/items?organization_id={organization_id}"
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch items: {e}") from e

    def create_item(self, access_token: str, organization_id: str, item_data: dict) -> dict:
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
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/contacts?organization_id={organization_id}"
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch customers: {e}") from e

    def create_customer(self, access_token: str, organization_id: str, customer_data: dict) -> dict:
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/contacts?organization_id={organization_id}"
        payload = customer_data.copy()
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error creating customer: {e}") from e

    def create_invoice(self, access_token: str, organization_id: str, invoice_data: dict) -> dict:
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/invoices?organization_id={organization_id}"
        payload = invoice_data.copy()
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error creating invoice: {e}") from e

    def get_draft_invoices(self, access_token: str, organization_id: str) -> dict:
        headers = self._get_auth_headers(access_token)
        endpoint = f"{self.base_url}/invoices?organization_id={organization_id}&status=draft"
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch draft invoices: {e}") from e

    # <<< THIS METHOD CONTAINS THE FIX >>>
    def send_invoice_email(self, access_token: str, organization_id: str, invoice_id: str) -> dict:
        """
        Emails an invoice to the customer. This action also automatically
        changes the invoice's status from 'draft' to 'sent'.
        The correct API for this is POST /invoices/{invoice_id}/email
        """
        headers = self._get_auth_headers(access_token)
        
        # This is the correct endpoint to trigger the email action.
        endpoint = f"{self.base_url}/invoices/{invoice_id}/email?organization_id={organization_id}"
        
        try:
            # An empty POST request is typically used to trigger the default email action.
            response = requests.post(endpoint, headers=headers)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error sending invoice: {e}") from e