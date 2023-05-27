import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
import json
from firebase_admin.credentials import Certificate

DATABASE_URL = os.getenv("DATABASE_URL")
FIREBASE_JSON = json.loads(os.environ["FIREBASE_JSON"])

firebase_admin.initialize_app(Certificate(FIREBASE_JSON), {"databaseURL": DATABASE_URL})
