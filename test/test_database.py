from bot.database_service import firestore_service

from unittest import TestCase


class TestFirestoreService(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.db = firestore_service.FirestoreService()
        cls.telegram_id = "123456"
        cls.sheet_id = "sheet123"
        cls.telegram_username = "test_user"

    def test_check_if_user_exists(self):
        # Act
        user_exists = self.db.check_if_user_exists(self.telegram_id)

        # Assert
        self.assertTrue(user_exists)

    def test_get_user_sheet_id(self):
        # Act
        sheet_id = self.db.get_user_sheet_id(self.telegram_id, self.telegram_username)

        # Assert
        self.assertEqual(sheet_id, self.sheet_id)
