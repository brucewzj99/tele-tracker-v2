import logging


logging.basicConfig(level=logging.ERROR, filename='telegram_bot.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class BaseError(Exception):
    """Base class for other exceptions"""
    def __init__(self, error_class, message="An error occurred", extra_info=""):
        self.message = message
        self.extra_info = extra_info
        self.error_class = error_class
        logging.error(f"{error_class}: {message} {extra_info}")
        print(f"{error_class}: {message} {extra_info}")
        super().__init__(f"{self.error_class}: {self.message}")

class GoogleSheetError(BaseError):
    """Exception raised for errors in the Google Sheet service."""
    def __init__(self, message="", extra_info=""):
        super().__init__("GoogleSheetError", message, extra_info)

class TelegramBotError(BaseError):
    """Exception raised for errors in the Telegram bot operations."""
    def __init__(self, message="", extra_info=""):
        super().__init__("TelegramBotError", message, extra_info)

class DatabaseError(BaseError):
    """Exception raised for errors in database operations."""
    def __init__(self, message="", extra_info=""):
        super().__init__("DatabaseError", message, extra_info)