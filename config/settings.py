# config/settings.py
# All static configuration variables for the application.

# --- URLs for OAuth 2.0 Flow ---
ZOHO_ACCOUNTS_BASE_URL = "https://accounts.zoho.com" # You correctly fixed this before
ZOHO_AUTH_URL = f"{ZOHO_ACCOUNTS_BASE_URL}/oauth/v2/auth"
ZOHO_TOKEN_URL = f"{ZOHO_ACCOUNTS_BASE_URL}/oauth/v2/token"

ZOHO_API_CONSOLE_URL = "https://api-console.zoho.com"


# --- Static Application Details ---
REDIRECT_URI = "http://localhost:8000"

# --- FIX: Align this URL with the data center above ---
API_BASE_URL = "https://www.zohoapis.com/invoice/v3" # Changed from .in to .com

# The permissions our app requires from the user
ZOHO_SCOPES = "ZohoInvoice.fullaccess.all"