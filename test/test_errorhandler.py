import unittest
from unittest.mock import patch
from bot.error_handler import GoogleSheetError, TelegramBotError, DatabaseError

class TestErrorHandling(unittest.TestCase):
    
    def test_google_sheet_error_raises_correctly(self):
        # Define the message and extra_info
        message = "Test failure in Google Sheets"
        extra_info = "Invalid Range"
        
        # Check if the exception is raised with the correct message
        with self.assertRaises(GoogleSheetError) as context:
            raise GoogleSheetError(message, extra_info)
        
        # Verify that the message in the exception is as expected
        self.assertEqual(str(context.exception), f"GoogleSheetError: {message}")

    def test_telegram_bot_error_raises_correctly(self):
        message = "Failed to send message"
        extra_info = "User not found"
        
        with self.assertRaises(TelegramBotError) as context:
            raise TelegramBotError(message, extra_info)
        
        self.assertEqual(str(context.exception), f"TelegramBotError: {message}")

    def test_database_error_raises_correctly(self):
        message = "Database connection failed"
        extra_info = "Timeout occurred"
        
        with self.assertRaises(DatabaseError) as context:
            raise DatabaseError(message, extra_info)
        
        self.assertEqual(str(context.exception), f"DatabaseError: {message}")