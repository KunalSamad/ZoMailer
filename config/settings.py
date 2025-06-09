# config/settings.py
# All static configuration variables for the application.

# CLIENT_ID and CLIENT_SECRET are now stored in credentials.json
# You can safely remove the old placeholder lines.

REDIRECT_URI = "http://localhost:8000"
API_BASE_URL = "https://www.zohoapis.com/invoice/v3"

# The permissions our app requires from the user
ZOHO_SCOPES = "ZohoInvoice.fullaccess.all"