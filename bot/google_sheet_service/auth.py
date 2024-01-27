import os
import json
from google.oauth2 import service_account


def get_credentials():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    google_json = os.getenv("GOOGLE_JSON")
    google_service = json.loads(google_json)
    creds = service_account.Credentials.from_service_account_info(
        google_service, scopes=SCOPES
    )
    return creds
