from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
import os
import json


def get_db_client():
    """
    Get credentials for the Google Sheets API.
    """
    firebase_json = json.loads(os.environ["FIREBASE_JSON"])

    cred = credentials.Certificate(firebase_json)
    firebase_admin.initialize_app(cred)

    return firestore.client()
