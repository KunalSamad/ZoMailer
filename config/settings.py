# config/settings.py
# All static configuration variables for the application.

# --- URLs for OAuth 2.0 Flow ---
ZOHO_ACCOUNTS_BASE_URL = "https://accounts.zoho.com" # Use .in, .com, .eu, etc. as needed
ZOHO_AUTH_URL = f"{ZOHO_ACCOUNTS_BASE_URL}/oauth/v2/auth"
ZOHO_TOKEN_URL = f"{ZOHO_ACCOUNTS_BASE_URL}/oauth/v2/token"

# --- FIX: Define the missing Console URL ---
ZOHO_API_CONSOLE_URL = "https://api-console.zoho.in"


# --- Static Application Details ---
REDIRECT_URI = "http://localhost:8000" # Must match what you entered in the Zoho API Console
API_BASE_URL = "https://www.zohoapis.in/invoice/v3"

# The permissions our app requires from the user
ZOHO_SCOPES = "ZohoInvoice.fullaccess.all"