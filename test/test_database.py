from bot.database_service import firestore_service
from unittest import TestCase
from bot.error_handler import DatabaseError

class TestFirestoreService(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.db = firestore_service.FirestoreService()
        cls.telegram_id = "123456"
        cls.fake_telegram_id = "123"
        cls.sheet_id = "sheet123"
        cls.telegram_username = "test_user"

    def test_check_if_user_exists(self):
        # Act
        user_exists = self.db.check_if_user_exists(self.telegram_id)

        # Assert
        self.assertTrue(user_exists)

    
    def test_check_if_user_dont_exists(self):
        # Act
        user_exists = self.db.check_if_user_exists(self.fake_telegram_id)

        # Assert
        self.assertFalse(user_exists)

    def test_get_user_sheet_id(self):
        # Act
        sheet_id = self.db.get_user_sheet_id(self.telegram_id, self.telegram_username)

        # Assert
        self.assertEqual(sheet_id, self.sheet_id)

    
    def test_get_dont_exist_user_sheet_id(self):
        # Act & Assert
        with self.assertRaises(DatabaseError) as context:
            self.db.get_user_sheet_id(self.fake_telegram_id, self.telegram_username)

        # Check if the error message is as expected
        self.assertIn("User does not exist", context.exception.extra_info)