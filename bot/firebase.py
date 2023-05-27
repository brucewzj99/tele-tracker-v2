from bot.firebase_config import db


# new user setup
def new_user_setup(telegram_id, sheet_id):
    ref = db.reference("/users/" + str(telegram_id))
    ref.update(
        {
            "sheet_id": sheet_id,
        }
    )


# check if user exists
def check_if_user_exists(telegram_id):
    ref = db.reference("/users/" + str(telegram_id))
    return ref.get() is not None


# get user sheet id
def get_user_sheet_id(telegram_id):
    ref = db.reference("/users/" + str(telegram_id) + "/sheet_id")
    return ref.get()
