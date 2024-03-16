"""
auth.py

This file contains a function that returns the credentials for the Google Sheets API. 
The credentials are obtained from the GOOGLE_JSON environment variable, which is set in the .env file.
The get_credentials function uses the google.oauth2.service_account module to create a credentials 
object from the service account info in the GOOGLE_JSON environment variable. 
The credentials object is then returned to the caller.

"""

import os
import json
from google.oauth2 import service_account


def get_credentials():
    """
    Get credentials for the Google Sheets API.
    """
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    google_json = os.getenv("GOOGLE_JSON")
    google_service = json.loads(google_json)
    creds = service_account.Credentials.from_service_account_info(
        google_service, scopes=SCOPES
    )
    return creds
