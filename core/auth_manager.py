# core/auth_manager.py
# Handles all OAuth 2.0 logic like exchanging and refreshing tokens.

import requests
import time
from config import settings

class AuthManager:
    """Handles the logic of exchanging and refreshing Zoho OAuth tokens."""

    def exchange_code_for_tokens(self, client_id: str, client_secret: str, code: str) -> dict:
        """
        Makes the backend request to get the initial tokens.
        Returns the JSON response from Zoho.
        """
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
            # Re-raise with more context
            raise ConnectionError(f"Network error during token exchange: {e}") from e