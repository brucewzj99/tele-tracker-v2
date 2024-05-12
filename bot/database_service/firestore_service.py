from bot.database_service.auth import get_db_client
from datetime import datetime, timedelta
import pytz
from bot.error_handler import DatabaseError


class FirestoreService:
    """
    This class is responsible for managing the Firestore database.
    """

    def __init__(self, collection_name="users"):
        self.db = get_db_client()
        self.collection_name = collection_name

    # New user setup
    def new_user_setup(self, telegram_id, sheet_id, telegram_username):
        try:
            user_ref = self.db.collection(self.collection_name).document(
                str(telegram_id)
            )
            timestamp = datetime.now(pytz.timezone("Asia/Singapore"))
            user_ref.set(
                {
                    "sheet_id": sheet_id,
                    "datetime_created": timestamp,
                    "username": telegram_username,
                    "usage_count": 0,
                    "last_accessed": timestamp,
                    "hourly_accessed": timestamp,
                    "overusage_count": 0,
                }
            )
        except Exception as e:
            raise DatabaseError(message="Error setting up new user", extra_info=str(e))

    # Check if user exists
    def check_if_user_exists(self, telegram_id):
        try:
            user_ref = self.db.collection(self.collection_name).document(
                str(telegram_id)
            )
            user_doc = user_ref.get()
            return user_doc.exists
        except Exception as e:
            raise DatabaseError(
                message="Error checking if user exists", extra_info=str(e)
            )

    # Get user sheet id
    def get_user_sheet_id(self, telegram_id, telegram_username):
        user_ref = self.db.collection(self.collection_name).document(str(telegram_id))
        user_doc = user_ref.get()

        if user_doc.exists:
            try:
                # Update username if it is different
                if user_doc.get("username") != telegram_username:
                    user_ref.update({"username": telegram_username})

                # Get the current time
                now = datetime.now(pytz.timezone("Asia/Singapore"))
                # Retrieve the hourly accessed time
                hourly_accessed = user_doc.get("hourly_accessed")

                if not hourly_accessed:
                    hourly_accessed = now

                usage_count = user_doc.get("usage_count")
                overusage_count = user_doc.get("overusage_count")
                if (now - hourly_accessed) < timedelta(hours=1):
                    if usage_count < 30:
                        usage_count += 1
                    else:
                        overusage_count += 1  # Increment overusage count if limit reached within the hour
                else:
                    # Reset if a new hour has started
                    usage_count = 1
                    hourly_accessed = now

                # Update the last accessed time, usage count and overusage count
                user_ref.update(
                    {
                        "last_accessed": now,
                        "hourly_accessed": hourly_accessed,
                        "usage_count": usage_count,
                        "overusage_count": overusage_count,
                    }
                )
                return user_doc.get("sheet_id")
            except Exception as e:
                raise DatabaseError(
                    message="Error getting user sheet id", extra_info=str(e)
                )
        raise DatabaseError(
                    message="User does not exist", extra_info="User does not exist"
                )

    # Get all user IDs
    def get_all_user_id(self):
        try:
            users_ref = self.db.collection(self.collection_name)
            user_ids = [int(user.id) for user in users_ref.stream()]
            return user_ids
        except Exception as e:
            raise DatabaseError(message="Error getting all user ids", extra_info=str(e))

    # Get user count
    def get_user_count(self):
        try:
            users_ref = self.db.collection(self.collection_name)
            user_count = len([user.id for user in users_ref.stream()])
            return user_count
        except Exception as e:
            raise DatabaseError(message="Error getting user count", extra_info=str(e))