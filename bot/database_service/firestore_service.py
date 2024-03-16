from bot.database_service.auth import get_db_client


class FirestoreService:
    """
    This class is responsible for managing the Firestore database.
    """

    def __init__(self):
        self.db = get_db_client()

    # New user setup
    def new_user_setup(self, telegram_id, sheet_id):
        user_ref = self.db.collection("users").document(str(telegram_id))
        user_ref.set({"sheet_id": sheet_id})

    # Check if user exists
    def check_if_user_exists(self, telegram_id):
        user_ref = self.db.collection("users").document(str(telegram_id))
        user_doc = user_ref.get()
        return user_doc.exists

    # Get user sheet id
    def get_user_sheet_id(self, telegram_id):
        user_ref = self.db.collection("users").document(str(telegram_id))
        user_doc = user_ref.get()
        if user_doc.exists:
            return user_doc.get("sheet_id")
        else:
            return None

    # Get all user IDs
    def get_all_user_id(self):
        users_ref = self.db.collection("users")
        user_ids = [int(user.id) for user in users_ref.stream()]
        return user_ids

    # Get all sheet IDs
    def get_all_sheet_id(self):
        users_ref = self.db.collection("users")
        sheet_ids = []
        for user in users_ref.stream():
            sheet_ids.append(user.get("sheet_id"))
        return sheet_ids
