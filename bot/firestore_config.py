from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
import os
import json

firebase_json = json.loads(os.environ["FIREBASE_JSON"])

cred = credentials.Certificate(firebase_json)
firebase_admin.initialize_app(cred)

db = firestore.client()
