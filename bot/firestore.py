from bot.firestore_config import db


# New user setup
def new_user_setup(telegram_id, sheet_id):
    user_ref = db.collection("users").document(str(telegram_id))
    user_ref.set({"sheet_id": sheet_id})


# Check if user exists
def check_if_user_exists(telegram_id):
    user_ref = db.collection("users").document(str(telegram_id))
    user_doc = user_ref.get()
    return user_doc.exists


# Get user sheet id
def get_user_sheet_id(telegram_id):
    user_ref = db.collection("users").document(str(telegram_id))
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.get("sheet_id")
    else:
        return None


# Get all user IDs
def get_all_user_id():
    users_ref = db.collection("users")
    user_ids = [int(user.id) for user in users_ref.stream()]
    return user_ids


# Get all sheet IDs
def get_all_sheet_id():
    users_ref = db.collection("users")
    sheet_ids = []
    for user in users_ref.stream():
        sheet_ids.append(user.get("sheet_id"))
    return sheet_ids
