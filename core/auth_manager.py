# core/auth_manager.py
# Handles all OAuth 2.0 logic like exchanging and refreshing tokens.

import requests
import time
from config import settings

class AuthManager:
    """Handles the logic of exchanging and refreshing Zoho OAuth tokens."""

    def exchange_code_for_tokens(self, client_id: str, client_secret: str, code: str) -> dict:
        """Makes the backend request to get the initial tokens."""
        payload = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': settings.REDIRECT_URI,
            'code': code,
        }
        
        try:
            response = requests.post(settings.ZOHO_TOKEN_URL, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error during token exchange: {e}") from e

    def refresh_access_token(self, client_id: str, client_secret: str, refresh_token: str) -> dict:
        """
        Uses a refresh token to get a new access token.
        Returns the JSON response from Zoho containing the new access token.
        """
        payload = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
        }
        
        try:
            print("Attempting to refresh access token...")
            response = requests.post(settings.ZOHO_TOKEN_URL, data=payload)
            response.raise_for_status()
            print("Successfully refreshed access token.")
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Network error during token refresh: {e}") from e