import os
from bot.telegram_bot import *
from bot.database_service.firestore_service import FirestoreService
from bot.google_sheet_service import * 
from bot.common import EntryType
db = FirestoreService()

# Function to test here