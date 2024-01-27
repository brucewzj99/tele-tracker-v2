# sheets_api.py
from googleapiclient.discovery import build
from .auth import get_credentials


class SheetManager:
    def __init__(self):
        self.creds = get_credentials()
        self.sheets_api = build("sheets", "v4", credentials=self.creds)
